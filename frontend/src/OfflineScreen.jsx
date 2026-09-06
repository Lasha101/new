// The « hors ligne » screen.
//
// Shown over the app when the device reports no connection, or when a request
// has just failed for a transport reason. It is an OVERLAY, not a replacement:
// the dashboard underneath stays mounted, so a tunnel does not throw away a
// half-filled form or a queue waiting to send.
//
// Deliberately nothing more than a message: no offline OCR, no queued uploads
// held on disk, no push, no background sync. A document waiting on a phone is a
// document stored on a phone.
//
// Built from the design system's own classes (.sid-card, .sid-empty, .sid-btn,
// .sid-spinner); the only new rule is the full-screen positioning, in
// mobile-pwa.css.

export default function OfflineScreen({ onRetry }) {
    return (
        <div className="sid-offline" role="alert" aria-live="assertive">
            <div className="sid-card sid-offline__card">
                <div className="sid-empty">
                    <strong>Vous êtes hors ligne</strong>
                    ScanID a besoin d'une connexion pour analyser vos documents. Aucune donnée
                    n'est conservée sur cet appareil : rien ne sera envoyé tant que la connexion
                    ne sera pas rétablie.
                </div>
                <p className="sid-offline__hint">
                    Vérifiez votre réseau mobile ou votre connexion Wi-Fi, puis réessayez.
                </p>
                <button type="button" className="sid-btn sid-offline__retry" onClick={onRetry}>
                    Réessayer
                </button>
            </div>
        </div>
    );
}
