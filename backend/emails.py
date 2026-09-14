# /emails.py
"""The French emails the application sends. Plain text, one function per email,
each returning (subject, body).

The trial welcome email is « Email A » of acquisition/ScanID-Emails-Essai.docx,
adapted as Spec v2 asks: the address is https://scanid.fr/app/, the identifiant
is the email, and a one-time link to choose the password replaces the
provisional password (a password is never sent by email).
"""
from datetime import datetime
from typing import Any, Dict, Tuple

import config

SIGNATURE = (
    "Bien cordialement,\n"
    "Alexandre Schepens\n"
    "ScanID — Scanner · Vérifier · Sécuriser\n"
    "contact@scanid.fr · scanid.fr"
)


def password_link(raw_token: str) -> str:
    """The token travels in the fragment (#), which browsers never send to a
    server: it cannot land in an access log or a Referer header."""
    return f"{config.app_public_url().rstrip('/')}/mot-de-passe#token={raw_token}"


def _date_fr(value: datetime) -> str:
    return f"{value.day:02d}/{value.month:02d}/{value.year:04d}"


def _scans(count: int) -> str:
    return f"{count:,}".replace(",", " ")


def password_reset(user: Dict[str, Any], raw_token: str) -> Tuple[str, str]:
    subject = "Réinitialisation de votre mot de passe ScanID"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        "Vous avez demandé à réinitialiser le mot de passe de votre espace ScanID.\n\n"
        "Pour choisir un nouveau mot de passe, ouvrez ce lien (valable "
        f"{config.PASSWORD_TOKEN_HOURS} heures, utilisable une seule fois) :\n"
        f"{password_link(raw_token)}\n\n"
        f"Votre identifiant : {user.get('user_name')}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email : "
        "votre mot de passe actuel reste valable.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def trial_admin_notification(request: Dict[str, Any]) -> Tuple[str, str]:
    subject = f"Demande d'essai — {request.get('societe') or request.get('nom')}"
    lines = [
        "Nouvelle demande d'essai sur scanid.fr/essai.html (20 scans offerts).",
        "",
        f"Nom : {request.get('nom')}",
        f"Société : {request.get('societe') or '—'}",
        f"Email : {request.get('email')}",
        f"Téléphone : {request.get('telephone') or '—'}",
        f"Volume : {request.get('volume') or '—'}",
        f"SIRET : {request.get('siret') or '—'}",
        f"N° de TVA : {request.get('tva') or '—'}",
        f"Message : {request.get('message') or '—'}",
        "",
        "Le compte est créé en attente. Pour le valider ou le refuser :",
        f"{config.app_public_url().rstrip('/')}/#demandes-essai",
        "(Administration → Demandes d'essai)",
        "",
        f"Sans décision, la demande sera supprimée automatiquement après {config.TRIAL_PURGE_DAYS} jours.",
    ]
    return subject, "\n".join(lines) + "\n"


def trial_welcome(user: Dict[str, Any], raw_token: str) -> Tuple[str, str]:
    subject = "Votre espace ScanID est ouvert — 20 scans offerts"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        "Votre espace ScanID est prêt. Vous disposez de 20 scans offerts — de quoi traiter un "
        "premier dossier groupe complet sur vos propres passeports.\n\n"
        "Vos accès :\n"
        f"- Adresse : {config.app_public_url()}\n"
        f"- Identifiant : {user.get('user_name')}\n"
        "- Mot de passe : choisissez-le vous-même grâce à ce lien (valable "
        f"{config.PASSWORD_TOKEN_HOURS} heures, utilisable une seule fois) :\n"
        f"  {password_link(raw_token)}\n\n"
        "Pour un premier essai réussi, trois minutes suffisent :\n"
        "1. Photographiez ou scannez vos documents en suivant notre guide photo (la qualité de la "
        "photo fait toute la fiabilité de la lecture) : https://scanid.fr/guide-photo.html\n"
        "2. Importez-les dans votre espace, seuls ou par lot.\n"
        "3. Téléchargez votre fichier Excel/CSV.\n\n"
        "Le guide complet est ici : https://scanid.fr/guide.html\n\n"
        "Une question, un doute, un document qui résiste ? Répondez simplement à cet email — "
        "c'est moi qui vous lis.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def purchase_confirmation(user: Dict[str, Any], pack: int, expires_at: datetime) -> Tuple[str, str]:
    subject = f"Vos {_scans(pack)} scans ScanID sont disponibles"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Merci pour votre achat du Pack {_scans(pack)}. Vos {_scans(pack)} scans ont été ajoutés à "
        f"votre espace ScanID ; ils sont valables jusqu'au {_date_fr(expires_at)}.\n\n"
        f"Votre espace : {config.app_public_url()}\n"
        f"Votre identifiant : {user.get('user_name')}\n\n"
        "Le détail de vos achats est dans « Mon Compte » → « Mes achats ». Le reçu de paiement "
        "vous a été envoyé par Stripe.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def payment_anomaly(reason: str, session: Dict[str, Any]) -> Tuple[str, str]:
    subject = "Paiement Stripe à rattacher manuellement"
    details = session.get("customer_details") or {}
    body = (
        "Un paiement Stripe confirmé n'a pas pu être crédité automatiquement.\n\n"
        f"Raison : {reason}\n"
        f"Session Stripe : {session.get('id')}\n"
        f"client_reference_id : {session.get('client_reference_id') or '—'}\n"
        f"Email du client : {details.get('email') or session.get('customer_email') or '—'}\n"
        f"Montant HT (centimes) : {session.get('amount_subtotal')}\n"
        f"Montant TTC (centimes) : {session.get('amount_total')} {session.get('currency') or ''}\n\n"
        "Aucun crédit n'a été ajouté. Vérifiez le paiement dans le tableau de bord Stripe et créditez "
        "le compte à la main depuis Administration.\n"
    )
    return subject, body
