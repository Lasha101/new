"""Data residency: Google Vision must be called in the EU.

French identity documents are processed for French agencies, and the client DPA
commits to EU processing. Left unconfigured, google-cloud-vision talks to the
GLOBAL endpoint (vision.googleapis.com), which may serve the request from any
Google region — so the absence of a setting was itself the defect.
"""
import os
import re

import config

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_the_configured_endpoint_is_in_the_eu():
    assert config.VISION_API_ENDPOINT == "eu-vision.googleapis.com"


def test_the_client_is_constructed_with_that_endpoint():
    """Read from the source: the client is built at import time, and a test
    that instantiated it would need real credentials."""
    source = open(os.path.join(BACKEND, "ocr_service.py"), encoding="utf-8").read()
    construction = re.search(
        r"vision_client = vision\.ImageAnnotatorClient\((.*?)\)\n", source, re.S
    )
    assert construction, "the Vision client construction could not be found"
    body = construction.group(1)
    assert "client_options" in body, (
        "ImageAnnotatorClient() is constructed with no client_options, so it "
        "uses the global endpoint"
    )
    assert "config.VISION_API_ENDPOINT" in body


def test_the_endpoint_is_environment_overridable():
    os.environ["VISION_API_ENDPOINT"] = "us-vision.googleapis.com"
    try:
        import importlib
        importlib.reload(config)
        assert config.VISION_API_ENDPOINT == "us-vision.googleapis.com"
    finally:
        os.environ.pop("VISION_API_ENDPOINT", None)
        import importlib
        importlib.reload(config)
    assert config.VISION_API_ENDPOINT == "eu-vision.googleapis.com"


def test_images_are_sent_as_inline_bytes_not_a_gcs_uri():
    """Inline content means nothing is uploaded to a Google Cloud Storage
    bucket that would then need its own retention policy."""
    source = open(os.path.join(BACKEND, "ocr_service.py"), encoding="utf-8").read()
    assert "vision.Image(content=" in source
    assert "gcs_image_uri" not in source
    assert "source=vision.ImageSource" not in source
