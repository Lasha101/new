# /emails.py
"""The French emails the application sends. Plain text, one function per email,
each returning (subject, body).

The trial welcome email is « Email A » of acquisition/ScanID-Emails-Essai.docx,
adapted as Spec v2 asks: the address is https://scanid.fr/app/, the identifiant
is the email, and a one-time link to choose the password replaces the
provisional password (a password is never sent by email).
"""
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import config
import invoicing

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


def _purchases_paragraph(invoice_number: Optional[str]) -> str:
    """Where the purchase is detailed — and, once invoices are issued, that its
    invoice is attached (Alex, 08/10/2026)."""
    attached = f"Votre facture {invoice_number} est jointe à cet e-mail. " if invoice_number else ""
    return (f"{attached}Le détail de vos achats est dans « Mon compte » → « Mes achats ». Le reçu de paiement "
            "vous a été envoyé par Stripe.\n\n")


def password_reset(user: Dict[str, Any], raw_token: str) -> Tuple[str, str]:
    subject = "Réinitialisation de votre mot de passe ScanID"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        "Vous avez demandé à réinitialiser le mot de passe de votre espace ScanID.\n\n"
        "Pour choisir un nouveau mot de passe, ouvrez ce lien (valable "
        f"{config.PASSWORD_TOKEN_HOURS} heures, utilisable une seule fois) :\n"
        f"{password_link(raw_token)}\n\n"
        f"Votre identifiant : {user.get('user_name')}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet e-mail : "
        "votre mot de passe actuel reste valable.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def trial_admin_notification(request: Dict[str, Any]) -> Tuple[str, str]:
    subject = f"Demande d'essai — {request.get('societe') or request.get('nom')}"
    lines = [
        "Nouvelle demande d'essai sur scanid.fr/essai.html (20 documents offerts).",
        "",
        f"Nom : {request.get('nom')}",
        f"Société : {request.get('societe') or '—'}",
        f"E-mail : {request.get('email')}",
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
    subject = "Votre espace ScanID est ouvert — 20 documents offerts"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        "Votre espace ScanID est prêt. Vous disposez de 20 documents offerts — de quoi traiter un "
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
        "Une question, un doute, un document qui résiste ? Répondez simplement à cet e-mail — "
        "c'est moi qui vous lis.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def trial_credits_added(user: Dict[str, Any]) -> Tuple[str, str]:
    """« Valider » on a trial request whose account a purchase had already opened
    (Alex, 03/10/2026): only the trial's documents are added — the account and
    its access exist, so no password link."""
    subject = f"{config.TRIAL_CREDITS} documents offerts ajoutés à votre espace ScanID"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Votre demande d'essai est validée : {config.TRIAL_CREDITS} documents offerts ont été ajoutés à votre "
        "espace ScanID.\n\n"
        f"Votre espace : {config.app_public_url()}\n"
        f"Votre identifiant : {user.get('user_name')}\n"
        "Votre mot de passe : celui que vous avez choisi (sinon, « Mot de passe oublié ? » sur la page de "
        "connexion).\n\n"
        "Une question, un doute, un document qui résiste ? Répondez simplement à cet e-mail — "
        "c'est moi qui vous lis.\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def purchase_confirmation(user: Dict[str, Any], pack: int, expires_at: datetime,
                          invoice_number: Optional[str] = None) -> Tuple[str, str]:
    subject = f"Vos {_scans(pack)} documents ScanID sont disponibles"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Merci pour votre achat du Pack {_scans(pack)}. Vos {_scans(pack)} documents ont été ajoutés à "
        f"votre espace ScanID ; ils sont valables jusqu'au {_date_fr(expires_at)}.\n\n"
        f"Votre espace : {config.app_public_url()}\n"
        f"Votre identifiant : {user.get('user_name')}\n\n"
        f"{_purchases_paragraph(invoice_number)}"
        f"{SIGNATURE}\n"
    )
    return subject, body


def unit_purchase_confirmation(user: Dict[str, Any], quantity: int, expires_at: datetime,
                               invoice_number: Optional[str] = None) -> Tuple[str, str]:
    """« À la carte »: documents bought one by one, 1 document = 1 credit."""
    many = quantity > 1
    documents = f"{_scans(quantity)} document{'s' if many else ''}"
    subject = f"Vos {documents} ScanID sont disponibles" if many else "Votre document ScanID est disponible"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Merci pour votre achat à la carte : {documents} {'ont été ajoutés' if many else 'a été ajouté'} à "
        f"votre espace ScanID ; {'ils sont valables' if many else 'il est valable'} jusqu'au {_date_fr(expires_at)}.\n\n"
        f"Votre espace : {config.app_public_url()}\n"
        f"Votre identifiant : {user.get('user_name')}\n\n"
        f"{_purchases_paragraph(invoice_number)}"
        f"{SIGNATURE}\n"
    )
    return subject, body


def unit_purchase_welcome(user: Dict[str, Any], raw_token: str, quantity: int, expires_at: datetime,
                          invoice_number: Optional[str] = None) -> Tuple[str, str]:
    """« À la carte » bought by an address whose account was not open yet (Alex,
    03/10/2026): the purchase opened it — the welcome, with the link to choose the
    password, and the documents bought. A password is never sent."""
    many = quantity > 1
    documents = f"{_scans(quantity)} document{'s' if many else ''}"
    subject = f"Votre espace ScanID est ouvert — {documents} disponible{'s' if many else ''}"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Merci pour votre achat à la carte : {documents} {'ont été ajoutés' if many else 'a été ajouté'} à "
        f"votre espace ScanID ; {'ils sont valables' if many else 'il est valable'} jusqu'au {_date_fr(expires_at)}.\n\n"
        "Vos accès :\n"
        f"- Adresse : {config.app_public_url()}\n"
        f"- Identifiant : {user.get('user_name')}\n"
        "- Mot de passe : choisissez-le vous-même grâce à ce lien (valable "
        f"{config.PASSWORD_TOKEN_HOURS} heures, utilisable une seule fois) :\n"
        f"  {password_link(raw_token)}\n\n"
        "Pour bien démarrer, trois minutes suffisent :\n"
        "1. Photographiez ou scannez vos documents en suivant notre guide photo (la qualité de la "
        "photo fait toute la fiabilité de la lecture) : https://scanid.fr/guide-photo.html\n"
        "2. Importez-les dans votre espace, seuls ou par lot.\n"
        "3. Téléchargez votre fichier Excel/CSV.\n\n"
        f"{_purchases_paragraph(invoice_number)}"
        "Une question, un doute, un document qui résiste ? Répondez simplement à cet e-mail — "
        "c'est moi qui vous lis.\n\n"
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
        f"E-mail du client : {details.get('email') or session.get('customer_email') or '—'}\n"
        f"Montant HT (centimes) : {session.get('amount_subtotal')}\n"
        f"Montant TTC (centimes) : {session.get('amount_total')} {session.get('currency') or ''}\n\n"
        "Aucun crédit n'a été ajouté. Vérifiez le paiement dans le tableau de bord Stripe et créditez "
        "le compte à la main depuis Administration.\n"
    )
    return subject, body


def invoice_not_issued(reason: str, user: Dict[str, Any], pack: int, credits: int, session: Dict[str, Any]) -> Tuple[str, str]:
    """To Alex: a purchase was credited but the app did not issue its invoice
    (billing address outside France, a price that is not the app's, an error)."""
    bought = f"Pack {_scans(pack)}" if pack else f"À la carte · {_scans(credits)} document{'s' if credits > 1 else ''}"
    paid, currency = session.get("amount_total"), str(session.get("currency") or "").lower()
    if not isinstance(paid, int) or isinstance(paid, bool):
        paid_text = "—"
    else:
        paid_text = invoicing.euros(paid) if currency == "eur" else f"{paid} centimes ({currency.upper() or '?'})"
    who = " ".join(v for v in (user.get("first_name"), user.get("last_name")) if v) or "—"
    subject = "Facture non émise automatiquement — à établir à la main"
    body = (
        "Un achat a été payé et crédité, mais l'application n'a pas émis sa facture.\n\n"
        f"Raison : {reason}\n\n"
        f"Achat : {bought}\n"
        f"Montant payé (TTC) : {paid_text}\n"
        f"Client : {user.get('company') or '—'} — {who} — {user.get('email')}\n"
        f"Session Stripe : {session.get('id')}\n"
        f"Paiement Stripe : {session.get('payment_intent') or '—'}\n\n"
        "Les crédits sont bien sur le compte du client. Établissez la facture à la main, dans votre propre série "
        "de numéros (jamais la série F-… de l'application).\n"
    )
    return subject, body


def credit_note(user: Dict[str, Any], note_number: str, invoice_number: str, ttc_cents: int) -> Tuple[str, str]:
    """A refund's credit note (« avoir », Alex, 08/10/2026), attached."""
    subject = f"Votre avoir {note_number} — remboursement ScanID"
    body = (
        f"Bonjour {user.get('first_name') or ''},\n\n"
        f"Suite au remboursement de votre achat, voici l'avoir {note_number} sur la facture {invoice_number}, "
        f"d'un montant de {invoicing.euros(ttc_cents)} TTC. Il est joint à cet e-mail ; vous le retrouvez aussi "
        "dans « Mon compte » → « Mes achats ».\n\n"
        f"{SIGNATURE}\n"
    )
    return subject, body


def refund_without_credit_note(reason: str, charge: Dict[str, Any]) -> Tuple[str, str]:
    """To Alex: a Stripe refund for which the app issued no credit note."""
    refunded = charge.get("amount_refunded")
    shown = invoicing.euros(refunded) if isinstance(refunded, int) and not isinstance(refunded, bool) else "—"
    subject = "Remboursement Stripe sans avoir automatique — à traiter à la main"
    body = (
        "Un remboursement Stripe a été reçu, mais l'application n'a pas émis d'avoir.\n\n"
        f"Raison : {reason}\n\n"
        f"Paiement Stripe : {charge.get('payment_intent') or '—'}\n"
        f"Opération Stripe : {charge.get('id') or '—'}\n"
        f"Total remboursé sur ce paiement : {shown}\n\n"
        "Établissez l'avoir à la main si nécessaire.\n"
    )
    return subject, body


def _euros_or_dash(cents: Any) -> str:
    return invoicing.euros(cents) if isinstance(cents, int) and not isinstance(cents, bool) else "—"


def refund_partial(purchase: Dict[str, Any], user: Optional[Dict[str, Any]], charge: Dict[str, Any]) -> Tuple[str, str]:
    """To Alex: a partial refund — the app takes no credit back then (Alex,
    09/10/2026); the balance is his call."""
    user = user or {}
    pack, credits = purchase.get("pack"), purchase.get("credits") or 0
    bought = f"Pack {_scans(pack)}" if pack else f"À la carte · {_scans(credits)} document{'s' if credits > 1 else ''}"
    paid_at = purchase.get("paid_at")
    paid_on = invoicing.date_fr(invoicing.to_paris(paid_at).date()) if paid_at else "—"
    who = " ".join(v for v in (user.get("first_name"), user.get("last_name")) if v) or "—"
    balance = user.get("page_credits")
    subject = "Remboursement partiel — crédits non modifiés"
    body = (
        "Un remboursement partiel a été fait dans Stripe. Dans ce cas, l'application ne retire aucun crédit : "
        "corrigez le solde du client à la main si nécessaire (Administration → Gérer les utilisateurs → "
        "Crédits pages).\n\n"
        f"Achat : {bought}, payé le {paid_on}\n"
        f"Montant payé (TTC) : {_euros_or_dash(charge.get('amount'))}\n"
        f"Total remboursé sur ce paiement : {_euros_or_dash(charge.get('amount_refunded'))}\n"
        f"Client : {user.get('company') or '—'} — {who} — {user.get('email') or '—'}\n"
        f"Crédits du client à cet instant : {'—' if balance is None else _scans(balance)}\n"
        f"Paiement Stripe : {charge.get('payment_intent') or '—'}\n"
        f"Opération Stripe : {charge.get('id') or '—'}\n\n"
        "Si le reste du paiement est remboursé plus tard, l'application retirera alors les crédits de cet achat, "
        "comme pour un remboursement total.\n"
    )
    return subject, body


def refund_not_taken_back(reason: str, charge: Dict[str, Any], no_credit_note: bool = False) -> Tuple[str, str]:
    """To Alex: a Stripe refund whose credits the app did not take back — no
    ScanID purchase for that payment, or an error (Alex, 09/10/2026). When the
    same cause also left it without its credit note, this one e-mail says both."""
    kind = "remboursement total" if charge.get("refunded") is True else "remboursement partiel"
    not_issued, by_hand = (" et n'a pas émis d'avoir", ", et établissez l'avoir à la main") if no_credit_note else ("", "")
    subject = "Remboursement Stripe à traiter à la main — crédits non retirés"
    body = (
        f"Un remboursement Stripe a été reçu, mais l'application n'a pas retiré les crédits de l'achat{not_issued}.\n\n"
        f"Raison : {reason}\n\n"
        f"Paiement Stripe : {charge.get('payment_intent') or '—'}\n"
        f"Opération Stripe : {charge.get('id') or '—'}\n"
        f"Total remboursé sur ce paiement : {_euros_or_dash(charge.get('amount_refunded'))} ({kind})\n\n"
        "Corrigez le solde du client à la main si nécessaire (Administration → Gérer les utilisateurs → "
        f"Crédits pages){by_hand}.\n"
    )
    return subject, body
