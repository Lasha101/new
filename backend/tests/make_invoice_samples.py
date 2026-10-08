"""The samples Alex's accountant validates before invoices go live (Alex,
« Invoices issued by the app », 08/10/2026, §5): one invoice for a Pack 100 and
one credit note for its refund, as PDF.

Not a test (pytest collects test_*.py only). Run from backend/:
    ../newvenv/bin/python tests/make_invoice_samples.py [output directory]

They come from the real path — /signup, a signed Stripe webhook for the Pack 100,
then a signed charge.refunded for the whole amount — on a throwaway SQLite
database, with the e-mails kept in memory: nothing is sent, nothing reaches
PostgreSQL. The numbers are therefore the first of the real series
(F-AAAA-00001, AV-AAAA-00001); the client is fictional, and each PDF carries a
« SPÉCIMEN » banner."""
import hashlib
import os
import sys
from datetime import date

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOSITORY = os.path.dirname(BACKEND_DIR)
os.chdir(BACKEND_DIR)          # main.py mounts ./static relative to the working directory
sys.path.insert(0, BACKEND_DIR)

SECRET = "whsec_samples_only"
# Before anything is imported: the e-mails stay in memory, whatever backend/.env says.
os.environ.update(MAIL_BACKEND="outbox", MAIL_ADMIN_TO="contact@scanid.fr", INVOICES_ENABLED="1",
                  STRIPE_WEBHOOK_SECRET=SECRET)
os.environ.pop("MAIL_OUTBOX_DIR", None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import invoicing  # noqa: E402
import mailer  # noqa: E402
import models  # noqa: E402
from database import get_db  # noqa: E402
from main import app  # noqa: E402
from tests.test_invoices import luhn_siret, pack_event, refund_event, signed, signup, user_id_of  # noqa: E402

BANNER = "SPÉCIMEN — exemple à valider, client fictif, sans valeur comptable"
EMAIL = "camille.exemple@example.com"
SIRET = luhn_siret("1234567820001")          # SIREN 123 456 782: fictional
SIREN = SIRET[:9]
VAT = f"FR{(12 + 3 * (int(SIREN) % 97)) % 97:02d}{SIREN}"


def main(out_dir: str) -> None:
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def throwaway_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = throwaway_db
    real_render = invoicing.render_pdf
    invoicing.render_pdf = lambda document, banner=None: real_render(document, banner=BANNER)
    try:
        client = TestClient(app)
        signup(client, first_name="Camille", last_name="Exemple", company="Agence Exemple Voyages", email=EMAIL,
               billing_street="12 rue de l'Exemple", billing_postal_code="75011", billing_city="Paris",
               billing_country="France", siret=SIRET, vat_number=VAT)
        db = Session()
        purchase = pack_event(user_id_of(db, EMAIL), session_id="cs_live_specimen", payment_intent="pi_specimen",
                              details={"email": EMAIL})
        assert signed(client, purchase, secret=SECRET).json()["result"] == "credited"
        refund = refund_event(11_880, payment_intent="pi_specimen", charge_id="ch_specimen", event_id="evt_specimen")
        assert signed(client, refund, secret=SECRET).json()["result"] == "issued"

        documents = db.query(models.Invoice).order_by(models.Invoice.issued_at, models.Invoice.sequence).all()
        assert [d.kind for d in documents] == [invoicing.KIND_INVOICE, invoicing.KIND_CREDIT_NOTE]
        sent = [a for mail in mailer.OUTBOX for a in (mail.attachments or [])]
        assert [(name, data) for name, data, _ in sent] == [(invoicing.filename(d), d.pdf) for d in documents]
        db.close()
    finally:
        invoicing.render_pdf = real_render
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()

    os.makedirs(out_dir, exist_ok=True)
    for document in documents:
        path = os.path.join(out_dir, invoicing.filename(document))
        with open(path, "wb") as f:
            f.write(document.pdf)
        print(f"{document.number}  {path}  {len(document.pdf)} bytes  sha256 {hashlib.sha256(document.pdf).hexdigest()}")


if __name__ == "__main__":
    default = os.path.join(REPOSITORY, "frontend", "payment_scanid", f"invoices-{date.today().isoformat()}")
    main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else default)
