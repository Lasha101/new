// One place for the DOM handles the suites depend on.
//
// The app has no test ids, and its <label> elements are not associated with
// their inputs (no htmlFor/id, no nesting), so getByLabel does not work here.
// The selectors below therefore lean on French placeholder text, French button
// text and the existing class names. If a later package adds test ids or fixes
// the label association, change these constants and the suites follow.
//
// Package A moved the app onto the scanid-app.css design system, so the class
// names here are the .sid-* ones. Only the handles changed; every assertion in
// the baseline suite is the one it had before.

export const SELECTORS = {
    // Login screen
    loginForm: '.landing-auth .sid-card',
    usernameInput: '.landing-auth input[type="text"]',
    passwordInput: '.landing-auth input[name="password"]',
    errorMessage: '.sid-alert--err',

    // Shell
    appHeader: '.sid-topbar',
    logoutButton: '.sid-topbar-right .sid-btn-ghost',
    creditBadge: '.sid-credits',
    navButtons: '.dashboard-nav .nav-button',

    // Upload card. The picker lives inside the drop zone; the camera input sits
    // beside it so `capture` does not take the photo library away from the
    // picker (Package B — see SCANID-HANDOVER.md).
    uploadCard: '.sid-dropzone',
    fileInput: '.sid-dropzone input[type="file"]',
    cameraInput: '.sid-capture input[type="file"]',
    cameraButton: '.sid-capture__button',
    photoGuideLink: '.sid-capture__guide',
    destinationInput: 'input[list="destination-datalist-ocr"]',

    // Upload queue (Package B)
    queue: '.sid-queue',
    queueItem: '.sid-queue__item',
    queueChip: '.sid-queue__item .sid-chip',
    queueError: '.sid-queue__error',
    retryFailed: '.sid-queue__head .sid-btn-outline',

    // PWA
    offlineScreen: '.sid-offline',
    sessionExpired: '.sid-session-expired',

    // OCR job monitor
    jobMonitor: '.job-monitor',
    jobItem: '.job-monitor .job-item',
    jobProgressText: '.job-monitor .progress-text',

    // Results screen. The table and the mobile card list are both always
    // mounted inside .sid-results; CSS alone decides which one is shown
    // (720 px). Use resultsRows() from upload.js, which picks the visible one,
    // rather than these selectors directly.
    results: '.sid-results',
    tableContainer: '.sid-results .sid-table-wrap',
    cardList: '.sid-results .sid-card-list',
    cardItem: '.sid-results .sid-card-item',
    typeFilter: '.sid-seg[data-name="document_type_filter"]',

    // Design-system pieces the Package A suites assert on.
    topbar: '.sid-topbar',
    logo: '.sid-logo',
    badge: '.sid-badge',
    chip: '.sid-chip',
    downloadGroup: '.sid-download-group',
    emptyState: '.sid-empty',
    appFooter: '.sid-appfoot',

    // Export panel
    exportPanel: '.filter-bar',
    previewTable: '.preview-table',
};

export const TEXT = {
    loginHeading: 'Connexion',
    loginSubmit: 'Se connecter',
    loginLoading: 'Connexion...',
    usernamePlaceholder: "Entrez votre identifiant",
    passwordPlaceholder: 'Entrez votre mot de passe',
    badCredentials: "Nom d'utilisateur ou mot de passe incorrect",
    rateLimited: 'Trop de tentatives de connexion. Veuillez réessayer dans une minute.',
    logout: 'Déconnexion',
    startAnalysis: "Lancer l'analyse",
    uploading: 'Envoi en cours…',
    downloadCsv: 'Télécharger CSV',
    downloadExcel: 'Télécharger Excel',
    preview: 'Aperçu',
    noData: 'Aucun document pour l’instant — importez votre premier passeport ou votre première CNI ci-dessus.',
    filterAll: 'Tous',
    jobDone: 'Terminé',
    jobFailed: 'Échoué',
};

/** Progress labels that mean the job will not change again (see ProgressBar). */
export const TERMINAL_JOB_LABELS = [TEXT.jobDone, TEXT.jobFailed];
