// One place for the DOM handles the suites depend on.
//
// The app has no test ids, and its <label> elements are not associated with
// their inputs (no htmlFor/id, no nesting), so getByLabel does not work here.
// The selectors below therefore lean on French placeholder text, French button
// text and the existing class names. If a later package adds test ids or fixes
// the label association, change these constants and the suites follow.

export const SELECTORS = {
    // Login screen
    loginForm: '.landing-auth .form-container',
    usernameInput: '.landing-auth input[type="text"]',
    passwordInput: '.landing-auth input[name="password"]',
    errorMessage: '.error-message',

    // Shell
    appHeader: '.app-header',
    logoutButton: '.app-header .btn-danger',
    creditBadge: '.credit-badge',
    navButtons: '.dashboard-nav .nav-button',

    // Upload card
    uploadCard: '.drop-zone',
    fileInput: '.drop-zone input[type="file"]',
    destinationInput: 'input[list="destination-datalist-ocr"]',

    // OCR job monitor
    jobMonitor: '.job-monitor',
    jobItem: '.job-monitor .job-item',
    jobProgressText: '.job-monitor .progress-text',

    // Results table. When the export preview is open the app renders a second
    // .table-container above this one, so the results table is always the LAST
    // one on the page — use resultsTable()/resultsRows() from upload.js rather
    // than these selectors directly.
    tableContainer: '.table-container',
    typeFilter: 'select[name="document_type_filter"]',

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
    noData: 'Aucune donnée trouvée.',
    jobDone: 'Terminé',
    jobFailed: 'Échoué',
};

/** Progress labels that mean the job will not change again (see ProgressBar). */
export const TERMINAL_JOB_LABELS = [TEXT.jobDone, TEXT.jobFailed];
