#!/usr/bin/env python3
"""ScanID — un-hide backups in the off-site object store.

WHY THIS EXISTS
  The backup bucket runs Object Lock in COMPLIANCE mode, so an object version
  cannot be destroyed before its retention expires — not by an attacker holding
  the server's credentials, not by you, not by the provider.

  What is still possible is a DELETE. On a versioned bucket that does not erase
  anything; it writes a *delete marker* which becomes the current version. Every
  ordinary listing then shows nothing, and the backups look gone. They are not:
  the data sits underneath, intact and locked.

  Recovery is therefore not "find another copy" — it is "remove the delete
  markers". Delete markers are not themselves protected by Object Lock, so they
  can be removed, and the previous version becomes current again.

  This was verified against the real bucket rather than assumed: an object was
  deleted with rclone, confirmed absent from `rclone ls`, confirmed still
  present as a non-latest version via ListObjectVersions, and restored with
  this script.

WHY NOT rclone OR awscli
  rclone cannot address object versions before 1.62, and Ubuntu 24.04 ships
  1.60. awscli is not installed and pulling it in during an incident is not a
  plan. This uses the Python standard library only — nothing to install on a
  server you may be recovering under pressure.

CONFIGURATION
  Everything is derived from the same files backup.sh already uses. There is
  nothing to keep in sync:

    OFFSITE_DEST=rclone:<remote>:<bucket>[/<prefix>]   from backup.env
    RCLONE_CONFIG=/etc/scanid/rclone.conf              from backup.env
    endpoint / region / credentials                    from that rclone.conf

  Credentials are read but never printed.

USAGE
    s3-undelete.py                 list delete markers; change nothing
    s3-undelete.py --remove        remove every delete marker in the bucket
    s3-undelete.py --key NAME      restrict to one object (repeatable)

  Exit codes: 0 nothing to do or all removed, 1 configuration error,
  2 one or more removals failed.
"""
import argparse
import configparser
import datetime
import hashlib
import hmac
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

OPS_ENV_FILE = os.environ.get("OPS_ENV_FILE", "/etc/scanid/backup.env")
SERVICE = "s3"


def die(msg):
    print(f"scanid-s3-undelete status=error message=\"{msg}\"", file=sys.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Configuration, derived rather than duplicated
# ---------------------------------------------------------------------------
def read_env_file(path):
    """Parse the KEY=VALUE lines of backup.env. Deliberately not a shell source:
    this script never needs to execute the operator's file, only read it."""
    if not os.path.isfile(path):
        die(f"env file not readable: {path} (set OPS_ENV_FILE to override)")
    values = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = read_env_file(OPS_ENV_FILE)

dest = env.get("OFFSITE_DEST", "")
if not dest.startswith("rclone:"):
    die(f"OFFSITE_DEST is not an rclone destination ({dest or 'unset'}); "
        "nothing for this script to do")

# rclone:<remote>:<bucket>[/<prefix>]
try:
    remote_name, bucket_path = dest[len("rclone:"):].split(":", 1)
except ValueError:
    die(f"OFFSITE_DEST is malformed, expected rclone:<remote>:<bucket>: {dest}")
BUCKET = bucket_path.strip("/").split("/", 1)[0]
if not remote_name or not BUCKET:
    die(f"could not derive remote and bucket from OFFSITE_DEST: {dest}")

rclone_config = env.get("RCLONE_CONFIG", "")
if not rclone_config:
    die(f"RCLONE_CONFIG is unset in {OPS_ENV_FILE}")

cfg = configparser.ConfigParser()
if not cfg.read(rclone_config):
    die(f"RCLONE_CONFIG is not readable: {rclone_config}")
if remote_name not in cfg:
    die(f"remote [{remote_name}] not found in {rclone_config}")

section = cfg[remote_name]
try:
    ACCESS_KEY = section["access_key_id"].strip()
    SECRET_KEY = section["secret_access_key"].strip()
except KeyError as exc:
    die(f"[{remote_name}] in {rclone_config} has no {exc.args[0]}")

endpoint = section.get("endpoint", "").strip()
if not endpoint:
    die(f"[{remote_name}] in {rclone_config} has no endpoint")
HOST = urllib.parse.urlsplit(endpoint if "//" in endpoint else f"//{endpoint}").netloc
REGION = section.get("region", "").strip() or "us-east-1"


# ---------------------------------------------------------------------------
# SigV4
# ---------------------------------------------------------------------------
def _sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def request(method, path, query):
    """Signed request against the bucket. `path` and `query` must already be in
    canonical form — every caller here builds them from values S3 itself
    returned, so there is nothing user-supplied to escape."""
    now = datetime.datetime.now(datetime.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(b"").hexdigest()

    canonical_headers = (f"host:{HOST}\n"
                         f"x-amz-content-sha256:{payload_hash}\n"
                         f"x-amz-date:{amzdate}\n")
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    canonical_request = "\n".join(
        [method, path, query, canonical_headers, signed_headers, payload_hash])

    scope = f"{datestamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256", amzdate, scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    key = _sign(f"AWS4{SECRET_KEY}".encode(), datestamp)
    for part in (REGION, SERVICE, "aws4_request"):
        key = _sign(key, part)
    signature = hmac.new(key, string_to_sign.encode(), hashlib.sha256).hexdigest()

    req = urllib.request.Request(
        f"https://{HOST}{path}?{query}",
        method=method,
        headers={
            "Host": HOST,
            "x-amz-date": amzdate,
            "x-amz-content-sha256": payload_hash,
            "Authorization": (
                f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            ),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()
    except urllib.error.URLError as exc:
        die(f"cannot reach {HOST}: {exc.reason}")


def list_delete_markers():
    status, body = request("GET", f"/{BUCKET}", "versions=")
    if status != 200:
        die(f"ListObjectVersions failed: HTTP {status} {body[:400]}")
    return re.findall(
        r"<DeleteMarker>.*?<Key>(.*?)</Key>.*?<VersionId>(.*?)</VersionId>.*?</DeleteMarker>",
        body, re.S)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Remove delete markers hiding backups in the off-site bucket.")
parser.add_argument("--remove", action="store_true",
                    help="actually remove the markers; the default only lists them")
parser.add_argument("--key", action="append", default=[],
                    help="restrict to this object key (repeatable)")
args = parser.parse_args()

markers = list_delete_markers()
if args.key:
    wanted = set(args.key)
    markers = [(k, v) for k, v in markers if k in wanted]

print(f"scanid-s3-undelete bucket={BUCKET} host={HOST} markers={len(markers)}")
if not markers:
    print("nothing hidden — every backup is visible")
    raise SystemExit(0)

failures = 0
for key, version_id in markers:
    if not args.remove:
        print(f"WOULD UNHIDE  {key}  marker={version_id}")
        continue
    status, body = request(
        "DELETE",
        f"/{BUCKET}/{urllib.parse.quote(key)}",
        f"versionId={urllib.parse.quote(version_id, safe='')}",
    )
    if status in (200, 204):
        print(f"UNHIDDEN      {key}")
    else:
        failures += 1
        print(f"FAILED        {key}  HTTP {status} {body[:200]}", file=sys.stderr)

if not args.remove:
    print(f"\n{len(markers)} marker(s) would be removed. Re-run with --remove.")
raise SystemExit(2 if failures else 0)
