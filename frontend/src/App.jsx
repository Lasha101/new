import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { getDocumentType, filterByDocumentType, buildExportQuery, downloadFilename, resultCellValue, DOC_TYPE_FILTER_OPTIONS, DOC_TYPE_PASSPORT, PASSPORT_COLUMN_ORDER } from './resultsHelpers.js';

// Use the build-time environment variable if it exists,
// otherwise fall back to '/api' for local development.
const API_URL = import.meta.env.VITE_API_URL || '/api';

// --- STYLES COMPONENT ---
// Only what the design system does not cover: the dashboard grid, the job
// monitor, the sort controls, the password toggle and a few utilities.
// Surfaces, buttons, inputs, tables, badges, chips, alerts and empty states all
// come from scanid-app.css, imported globally in main.jsx — the rules that used
// to duplicate them here were removed so the two cannot fight.
const GlobalStyles = () => (
    <style>{`
        /* 'clip' (not 'hidden') so no scroll container is created and
           position: sticky keeps working on the header and sidebar. */
        html, body { max-width: 100%; overflow-x: clip; }

        /* DASHBOARD GRID — two columns: on the passports tab the welcome card
           (nav) and the « Ajouter un Passeport » card share row 1 (left/right);
           every other section spans the entire screen width. Vertical rhythm
           comes from the sections' own margins, hence row-gap: 0. */
        .dashboard-layout { display: grid; grid-template-columns: 260px minmax(0, 1fr); column-gap: 1.4rem; row-gap: 0; }
        /* Grid items refuse to shrink below their content's minimum width by
           default (min-width: auto), so a wide table would push the content
           column past the viewport, where it cannot be reached. min-width: 0
           lets the column fit the screen; wide content then scrolls inside
           .sid-table-wrap as designed. */
        .dashboard-content, .dashboard-nav { grid-column: 1 / -1; min-width: 0; }
        /* Passports tab: flatten the intermediate wrappers so the sections —
           which live in different subtrees — become items of this same grid
           and can share a row. Nav goes row 1 left, the uploader (first
           .sid-card) row 1 right, everything else keeps DOM order and
           spans the full width. */
        .passports-layout .dashboard-nav { grid-column: 1; grid-row: 1; }
        .dashboard-content.passports-view, .passports-view > div, .passports-view > div > div { display: contents; }
        .passports-view > div > *, .passports-view > div > div > * { grid-column: 1 / -1; min-width: 0; }
        .passports-view > div > div > .sid-card:first-child { grid-column: 2; grid-row: 1; }
        /* Narrow screens: stack the two row-1 cards like everything else. */
        @media (max-width: 768px) {
            .passports-layout .dashboard-nav, .passports-view > div > div > .sid-card:first-child { grid-column: 1 / -1; grid-row: auto; }
        }
        /* Very narrow screens: the logo and the logout button together exceed
           the viewport, so let the top bar wrap. */
        @media (max-width: 380px) {
            .sid-topbar { flex-wrap: wrap; gap: 0.5rem; padding: 0.7rem 1rem; }
        }

        /* NAVIGATION SIDEBAR */
        .dashboard-nav h3 { margin-top: 0; margin-bottom: 0.25rem; }
        .dashboard-nav .credit-display { margin-bottom: 1.25rem; font-size: 0.85rem; color: var(--sid-text); }

        .nav-menu { display: flex; flex-direction: column; gap: 0.4rem; }
        .nav-button {
            text-align: left;
            padding: 0.7rem 1rem;
            border: none;
            background-color: transparent;
            border-radius: 10px;
            cursor: pointer;
            font-family: var(--sid-font-head);
            font-size: 0.92rem;
            font-weight: 600;
            width: 100%;
            min-height: 44px;
            color: var(--sid-text);
            transition: all 0.18s;
        }
        .nav-button:hover { background-color: #e6eef8; color: var(--sid-ink); }
        .nav-button.active { background-color: var(--sid-navy); color: #fff; }
        .nav-button:focus-visible { outline: none; box-shadow: var(--sid-focus); }

        /* PASSWORD FIELD */
        .password-container { position: relative; }
        .password-container .sid-input { padding-right: 44px; }
        .password-toggle-btn { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: var(--sid-text); padding: 6px; display: flex; border-radius: 8px; }
        .password-toggle-btn:hover { color: var(--sid-cyan-dark); }
        .password-toggle-btn:focus-visible { outline: none; box-shadow: var(--sid-focus); }

        .sid-dropzone * { pointer-events: none; }

        /* SORT UI ELEMENTS */
        .sid-table thead th.sortable { cursor: pointer; transition: background-color 0.2s; user-select: none; }
        .sid-table thead th.sortable:hover { background-color: var(--sid-navy-3); }
        .header-content { display: flex; align-items: center; justify-content: center; gap: 0.4rem; }
        .sort-checkbox { cursor: pointer; accent-color: var(--sid-cyan); width: 1rem; height: 1rem; flex-shrink: 0; }
        .sort-badge { display: inline-flex; align-items: center; margin-left: 0.35rem; font-size: 0.9em; color: var(--sid-navy); background: var(--sid-cyan); padding: 0 4px; border-radius: 4px; }
        .sort-badge small { font-size: 0.7em; margin-left: 2px; font-weight: 800; }
        .sort-indicator { margin-left: auto; color: rgba(255,255,255,0.55); font-size: 0.8em; }
        .sort-indicator.active { color: #fff; font-weight: bold; }

        /* Selection and action cells sit outside the uppercase/centred body. */
        .sid-table th.checkbox-cell, .sid-table td.checkbox-cell { width: 1%; padding-right: 0.4rem; }
        .sid-table tbody tr.selected-row { background-color: rgba(14, 165, 233, .1); }

        /* FILTERS */
        .filter-bar { display: flex; gap: 0.8rem; align-items: center; flex-wrap: wrap; }
        /* Without a floor, the destination field is squeezed to a few characters
           on a phone instead of wrapping onto its own line. */
        .filter-bar .form-group { min-width: 12rem; }

        /* JOB MONITOR */
        .job-list { list-style-type: none; padding: 0; margin: 0; max-height: 400px; overflow-y: auto; }
        .job-item { padding: 0.9rem; border: 1px solid var(--sid-border); border-radius: 12px; margin-bottom: 0.7rem; background: #fff; }
        .job-item:last-child { margin-bottom: 0; }
        .job-header { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
        /* Long unbreakable file names must wrap instead of widening the page. */
        .job-details { min-width: 0; overflow-wrap: anywhere; }
        .job-actions { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }

        /* PROGRESS BARS — the track comes from .sid-progress; these carry state. */
        .progress-fill { height: 100%; transition: width 0.6s ease; border-radius: 999px; }
        .progress-processing { background-image: linear-gradient(45deg,rgba(255,255,255,.25) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.25) 50%,rgba(255,255,255,.25) 75%,transparent 75%,transparent); background-size: 1rem 1rem; animation: progress-bar-stripes 1s linear infinite; }
        .progress-complete { background: var(--sid-ok); }
        .progress-failed { background: var(--sid-err); }
        .progress-text { font-size: 0.75rem; font-weight: 600; color: var(--sid-text); margin-top: 0.25rem; display: block; text-align: right; }

        @keyframes progress-bar-stripes { 0% { background-position: 1rem 0; } 100% { background-position: 0 0; } }

        /* LANDING PAGE */
        .landing-container { display: flex; justify-content: center; align-items: center; min-height: 70vh; }
        .landing-auth { width: 100%; max-width: 460px; }
        .landing-auth .sid-card { width: 100%; margin: 0; }

        /* FAILURE LIST */
        .failure-list { margin-top: 0.7rem; background-color: var(--sid-err-bg); border: 1px solid #f6c6c2; border-radius: 10px; padding: 0.7rem; }
        .failure-item { display: flex; gap: 0.5rem; color: var(--sid-err); font-size: 0.85rem; margin-bottom: 0.25rem; align-items: flex-start; }
        .failure-item:last-child { margin-bottom: 0; }

        /* Legal links row inside .sid-appfoot */
        .legal-links { display: flex; justify-content: center; gap: 0.5rem 1.5rem; margin-bottom: 0.6rem; flex-wrap: wrap; }

        .mt-1 { margin-top: 1rem; }
        .mb-1 { margin-bottom: 1rem; }
        .mb-2 { margin-bottom: 2rem; }
    `}</style>
);

const columnTranslations = {
    document_type: 'Type', // PASS = passeport, PI = pièce d'identité (derived, see resultsHelpers.js)
    first_name: 'Prénom',
    last_name: 'Nom de famille',
    birth_date: 'Date de Naissance',
    // delivery_date removed
    expiration_date: "Date d'Expiration",
    nationality: 'Nationalité',
    passport_number: 'Numéro de Passeport',
    confidence_score: 'Score de Confiance',
    email: 'Email',
    phone_number: 'Numéro de Téléphone',
    user_name: "Nom d'Utilisateur",
    role: 'Rôle',
    destination: 'Destination',
    actions: 'Actions',
    uploaded_pages_count: 'Pages Traitées',
    page_credits: 'Crédits Pages' // NEW
};

// --- HELPER COMPONENTS & ICONS ---
const EyeIcon = () => (<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>);
const EyeOffIcon = () => (<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>);
const UploadIcon = () => (<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>);
function PasswordInput({ value, onChange, name, placeholder, required = false }) {
    const [showPassword, setShowPassword] = useState(false);
    return (
        <div className="password-container">
            <input type={showPassword ? 'text' : 'password'} name={name} value={value} onChange={onChange} className="sid-input" placeholder={placeholder} required={required} autoComplete="new-password" />
            <button type="button" className="password-toggle-btn" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Cacher le mot de passe' : 'Afficher le mot de passe'}>
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
        </div>
    );
}

const SuccessIcon = () => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>);
const FailureIcon = () => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>);

// --- ProgressBar Component ---
const ProgressBar = ({ progress, status }) => {
    let statusClass = 'progress-processing';
    let label = `${progress}% - Traitement`;

    if (status === 'complete') {
        statusClass = 'progress-complete';
        label = 'Terminé';
    } else if (status === 'failed') {
        statusClass = 'progress-failed';
        label = 'Échoué';
    } else if (progress === 0) {
        label = "Démarrage..."; 
    } else if (progress < 15) {
        label = `${progress}% - Upload`;
    } else if (progress < 75) {
        label = `${progress}% - OCR`;
    } else {
        label = `${progress}% - Sauvegarde`;
    }

    return (
        <div style={{ marginTop: '0.5rem' }}>
            <div className="sid-progress">
                <div 
                    className={`progress-fill ${statusClass}`} 
                    style={{ width: `${progress > 0 ? progress : 5}%` }}
                >
                </div>
            </div>
            <span className="progress-text">{label}</span>
        </div>
    );
};

// --- MAIN APP COMPONENT ---
export default function App() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [view, setView] = useState('login');
    const logout = useCallback(() => { localStorage.removeItem('token'); setToken(null); setUser(null); window.history.pushState({}, '', '/'); setView('login'); }, []);
    const fetchUser = useCallback(async () => {
        const currentToken = localStorage.getItem('token');
        if (currentToken) {
            try {
                const response = await fetch(`${API_URL}/users/me`, { headers: { 'Authorization': `Bearer ${currentToken}` } });
                if (response.ok) { const data = await response.json(); setUser(data); setView('dashboard'); } else { logout(); }
            } catch (error) { console.error("Échec de la récupération de l'utilisateur:", error); logout(); }
        } else {
            setView('login');
        }
    }, [logout]);
    useEffect(() => {
        fetchUser();
        const handlePopState = () => fetchUser();
        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [fetchUser]);
    const renderView = () => {
        switch (view) {
            case 'login': return <Login setToken={setToken} fetchUser={fetchUser} onShowRegistration={() => setView('signup')} />;
            case 'signup': return <SelfRegistrationPage onBackToLogin={() => setView('login')} />;
            case 'dashboard': return <Dashboard user={user} logout={logout} token={token} fetchUser={fetchUser} />;
            default: return <Login setToken={setToken} fetchUser={fetchUser} onShowRegistration={() => setView('signup')} />;
        }
    };
    return (
        <>
            <GlobalStyles />
            <header className="sid-topbar">
                <h1 className="sid-logo">Scan<span>ID</span></h1>
                {user && (
                    <div className="sid-topbar-right">
                        {/* The credits counter the dashboard used to show in its sidebar. */}
                        <span className="sid-credits">Crédits : {user.page_credits}</span>
                        <button onClick={logout} className="sid-btn-ghost">Déconnexion</button>
                    </div>
                )}
            </header>
            <div className="sid-page"><main>{renderView()}</main></div>
        </>
    );
}

// --- PAGE & VIEW COMPONENTS ---
function Login({ setToken, fetchUser, onShowRegistration }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        const formData = new URLSearchParams({ username, password });
        try {
            const response = await fetch(`${API_URL}/token`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: formData, });
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                setToken(data.access_token);
                fetchUser();
            } else {
                if (response.status === 429) {
                    setError("Trop de tentatives de connexion. Veuillez réessayer dans une minute.");
                } else {
                    const errorData = await response.json();
                    setError(errorData.detail || 'Échec de la connexion.');
                }
            }
        } catch (err) {
            setError('Une erreur est survenue. Veuillez réessayer.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <div className="landing-container">
                <div className="landing-auth">
                    <div className="sid-card">
                        <h2>Connexion</h2>
                        {error && <p className="sid-alert sid-alert--err">{error}</p>}
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="sid-label">Nom d'utilisateur</label>
                                <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="sid-input" placeholder="Entrez votre identifiant" required />
                            </div>
                            <div className="form-group">
                                <label className="sid-label">Mot de passe</label>
                                <PasswordInput name="password" value={password} onChange={e => setPassword(e.target.value)} required={true} placeholder="Entrez votre mot de passe" />
                            </div>
                            <button type="submit" className="sid-btn" style={{ width: '100%', marginTop: '1rem' }} disabled={isLoading}>
                                {isLoading ? 'Connexion...' : 'Se connecter'}
                            </button>
                        </form>
                        <button type="button" onClick={onShowRegistration} className="sid-btn-outline" style={{ width: '100%', marginTop: '0.75rem' }}>
                            Créer un compte
                        </button>
                    </div>
                </div>
            </div>
            <footer className="sid-appfoot">
                <div className="legal-links">
                    <a href="#">Mentions Légales</a>
                    <a href="#">Politique de Confidentialité</a>
                    <a href="#">CGU</a>
                    <a href="#">Contact</a>
                </div>
                <p>&copy; {new Date().getFullYear()} Gestionnaire de Voyages - Tous droits réservés.</p>
            </footer>
        </div>
    );
}

function SelfRegistrationPage({ onBackToLogin }) {
    const [formData, setFormData] = useState({ first_name: '', last_name: '', email: '', phone_number: '', user_name: '', password: '' });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
    const handleSubmit = async (e) => {
        e.preventDefault(); setError(''); setSuccess('');
        try {
            const response = await fetch(`${API_URL}/users/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
            if (response.ok) { setSuccess('Inscription réussie ! Vous allez être redirigé vers la page de connexion.'); setTimeout(() => { window.history.pushState({}, '', '/'); window.location.reload(); }, 2000); } else { const detail = (await response.json()).detail; setError(typeof detail === 'string' ? detail : "Échec de l'inscription. Veuillez vérifier les champs saisis."); }
        } catch (err) { setError("Une erreur est survenue lors de l'inscription."); }
    };
    if (success) return <div className="sid-card"><p className="sid-alert sid-alert--ok">{success}</p></div>
    return (<div className="sid-card"><h2>Créer un nouveau compte</h2>{error && <p className="sid-alert sid-alert--err">{error}</p>}<form onSubmit={handleSubmit}><div className="form-group"><label className="sid-label">Prénom</label><input type="text" name="first_name" value={formData.first_name} onChange={handleChange} className="sid-input" required /></div><div className="form-group"><label className="sid-label">Nom de famille</label><input type="text" name="last_name" value={formData.last_name} onChange={handleChange} className="sid-input" required /></div><div className="form-group"><label className="sid-label">Email</label><input type="email" name="email" value={formData.email} onChange={handleChange} className="sid-input" required /></div><div className="form-group"><label className="sid-label">Numéro de téléphone</label><input type="text" name="phone_number" value={formData.phone_number} onChange={handleChange} className="sid-input" required /></div><div className="form-group"><label className="sid-label">Nom d'utilisateur</label><input type="text" name="user_name" value={formData.user_name} onChange={handleChange} className="sid-input" required /></div><div className="form-group"><label className="sid-label">Mot de passe</label><PasswordInput name="password" value={formData.password} onChange={handleChange} required={true} /></div><button type="submit" className="sid-btn" style={{ width: '100%' }}>S'inscrire</button></form><button type="button" onClick={onBackToLogin} className="sid-btn-outline" style={{ width: '100%', marginTop: '0.75rem' }}>Retour à la connexion</button></div>);
}

// Static field configurations, at module scope so their identity is stable:
// CrudForm resets its form state when `fields` changes, and a per-render
// object would wipe in-progress edits on every background refresh (SSE
// credit updates re-render the dashboard).
const passportFields = { first_name: 'text', last_name: 'text', birth_date: 'date', expiration_date: 'date', nationality: 'text', passport_number: 'text', destination: 'text', confidence_score: 'number' };

const userFields = {
    first_name: 'text',
    last_name: 'text',
    email: 'email',
    phone_number: 'text',
    user_name: 'text',
    password: 'password',
    role: 'text',
    uploaded_pages_count: 'number',
    page_credits: 'number'
};

function Dashboard({ user, token, fetchUser }) {
    const [activeTab, setActiveTab] = useState('passports');
    const [filterableUsers, setFilterableUsers] = useState([]);
    const [userSpecificDestinations, setUserSpecificDestinations] = useState([]);

    // --- SSE CONNECTION EFFECT ---
    useEffect(() => {
        if (!token) return;

        // Establish SSE connection
        // We pass the token in the query string because EventSource doesn't support headers
        const eventSource = new EventSource(`${API_URL}/events?token=${token}`);

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // On credit_update, refresh user data
                if (data.type === 'credit_update') {
                    fetchUser();
                } else if (data.type === 'job_progress' || data.type === 'job_update') {
                    // Forward job events to the job monitor without threading
                    // props through the whole component tree.
                    window.dispatchEvent(new CustomEvent('ocr-job-event', { detail: data }));
                }
            } catch (err) {
                console.error("Error parsing SSE message:", err);
            }
        };

        eventSource.onerror = (err) => {
            // Connection lost or error, EventSource auto-retries by default, but logging helps
            // console.warn("SSE Connection lost, retrying...", err);
        };

        // Cleanup on unmount
        return () => {
            eventSource.close();
        };
    }, [token, fetchUser]);

    const fetchAdminData = useCallback(async () => {
        if (user.role !== 'admin') return;
        try {
            const filterableUsersRes = await fetch(`${API_URL}/admin/filterable-users`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (filterableUsersRes.ok) setFilterableUsers(await filterableUsersRes.json());
        } catch (error) { console.error("Échec de la récupération des données admin:", error); }
    }, [user, token]);

    const fetchUserDestinations = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/destinations/`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) {
                setUserSpecificDestinations(await response.json());
            }
        } catch (error) {
            console.error("Échec de la récupération des destinations de l'utilisateur:", error);
        }
    }, [token]);

    useEffect(() => {
        fetchAdminData();
        fetchUserDestinations();
    }, [fetchAdminData, fetchUserDestinations]);

    const renderTabContent = () => {
        const passportFilterConfig = user.role === 'admin'
            ? [{ name: 'user_filter', placeholder: 'Filtrer par Utilisateur', options: filterableUsers, getOptionValue: (o) => o.id, getOptionLabel: (o) => `${o.first_name} ${o.last_name} (${o.user_name})` }]
            : [{
                name: 'destination_filter',
                placeholder: 'Filtrer par Destination',
                options: userSpecificDestinations.map(d => ({ destination: d })),
                getOptionValue: (o) => o.destination,
                getOptionLabel: (o) => o.destination
              }];

        switch (activeTab) {
            case 'passports': 
                return <PassportsPage 
                        token={token} 
                        user={user} 
                        fetchUser={fetchUser} // Pass fetchUser down
                        adminUsers={filterableUsers} 
                        userDestinations={userSpecificDestinations}
                        fields={passportFields}
                        filterConfig={passportFilterConfig}
                       />;
            case 'account': return <AccountEditor user={user} token={token} fetchUser={fetchUser} />;
            case 'admin_manage':
                return <AdminManagementPage
                        token={token}
                        user={user}
                        userFields={userFields}
                       />;
            default: return null;
        }
    };

    return (
        <div className={`dashboard-layout${activeTab === 'passports' ? ' passports-layout' : ''}`}>
            <nav className="dashboard-nav sid-card">
                <h3>Bienvenue, {user.first_name}!</h3>
                <div className="credit-display">
                    <span style={{ display: 'block' }}>Pages Traitées : {user.uploaded_pages_count}</span>
                </div>
                <div className="nav-menu">
                    <button onClick={() => setActiveTab('passports')} className={`nav-button ${activeTab === 'passports' ? 'active' : ''}`}>Passeports</button>
                    {user.role === 'admin' && (
                        <button onClick={() => setActiveTab('admin_manage')} className={`nav-button ${activeTab === 'admin_manage' ? 'active' : ''}`}>Administration</button>
                    )}
                    <button onClick={() => setActiveTab('account')} className={`nav-button ${activeTab === 'account' ? 'active' : ''}`}>Mon Compte</button>
                </div>
            </nav>
            <div className={`dashboard-content sid-card${activeTab === 'passports' ? ' passports-view' : ''}`}>{renderTabContent()}</div>
        </div>
    );
}

function PassportsPage({ token, user, fetchUser, adminUsers, userDestinations, fields, filterConfig }) {
    // ToolsAndExportPanel removed and logic merged into CrudManager
    return (
        <div>
            <CrudManager 
                title="Mes Passeports" 
                endpoint="passports" 
                token={token} 
                user={user} 
                fetchUser={fetchUser} // Pass fetchUser down to CrudManager
                fields={fields} 
                filterConfig={filterConfig} 
                // Pass data needed for the export panel
                adminUsers={adminUsers}
                userDestinations={userDestinations}
            />
        </div>
    );
}

function AdminManagementPage({ token, user, userFields }) {
    return (
        <div>
             <CrudManager title="Gérer les Utilisateurs" endpoint="admin/users" token={token} user={user} fields={userFields} />
        </div>
    );
}

function AccountEditor({ user, token, fetchUser }) {
    const [formData, setFormData] = useState({ 
        first_name: '', 
        last_name: '', 
        email: '', 
        phone_number: '', 
        password: '',
        uploaded_pages_count: 0,
        page_credits: 0
    });
    const [message, setMessage] = useState('');

    useEffect(() => { 
        if (user) {
            setFormData({ 
                first_name: user.first_name, 
                last_name: user.last_name, 
                email: user.email, 
                phone_number: user.phone_number, 
                password: '',
                uploaded_pages_count: user.uploaded_pages_count,
                page_credits: user.page_credits
            }); 
        }
    }, [user]);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
    
    const handleSubmit = async (e) => {
        e.preventDefault(); 
        setMessage(''); 
        const payload = { ...formData };
        if (!payload.password) delete payload.password;
        if (user.role === 'admin') {
            // '|| 0' so a cleared field never becomes NaN -> null in JSON,
            // which would corrupt the stored counters.
            payload.uploaded_pages_count = parseInt(payload.uploaded_pages_count, 10) || 0;
            payload.page_credits = parseInt(payload.page_credits, 10) || 0;
        }
        const response = await fetch(`${API_URL}/users/me`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify(payload) });
        if (response.ok) { setMessage('Compte mis à jour avec succès !'); fetchUser(); } else { setMessage('Échec de la mise à jour du compte.'); }
    };
    
    return (
        <div>
            <h2>Modifier Mon Compte</h2>
            {message && <p className="sid-alert sid-alert--ok">{message}</p>}
            <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="form-group"><label className="sid-label">Prénom</label><input type="text" name="first_name" value={formData.first_name} onChange={handleChange} className="sid-input" /></div>
                    <div className="form-group"><label className="sid-label">Nom de famille</label><input type="text" name="last_name" value={formData.last_name} onChange={handleChange} className="sid-input" /></div>
                    <div className="form-group"><label className="sid-label">Email</label><input type="email" name="email" value={formData.email} onChange={handleChange} className="sid-input" /></div>
                    <div className="form-group"><label className="sid-label">Numéro de téléphone</label><input type="text" name="phone_number" value={formData.phone_number} onChange={handleChange} className="sid-input" /></div>
                    <div className="form-group">
                        <label className="sid-label">{columnTranslations['uploaded_pages_count']}</label>
                        <input type="number" name="uploaded_pages_count" value={formData.uploaded_pages_count} onChange={handleChange} className="sid-input" readOnly={user.role !== 'admin'} disabled={user.role !== 'admin'} style={{ backgroundColor: user.role !== 'admin' ? '#eef2f7' : undefined }} />
                    </div>
                    <div className="form-group">
                        <label className="sid-label">{columnTranslations['page_credits']}</label>
                        <input type="number" name="page_credits" value={formData.page_credits} onChange={handleChange} className="sid-input" readOnly={user.role !== 'admin'} disabled={user.role !== 'admin'} style={{ backgroundColor: user.role !== 'admin' ? '#eef2f7' : undefined }} />
                    </div>
                </div>
                <div className="form-group"><label className="sid-label">Nouveau mot de passe (optionnel)</label><PasswordInput name="password" value={formData.password} onChange={handleChange} placeholder="Laisser vide pour conserver le mot de passe actuel" /></div>
                <button type="submit" className="sid-btn" style={{ marginTop: '1rem' }}>Enregistrer les modifications</button>
            </form>
        </div>
    );
}

function OcrUploader({ token, onUpload, isUploading, onCancelUpload }) {
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const [destination, setDestination] = useState('');
    const [destinations, setDestinations] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        const fetchDestinations = async () => {
            try {
                const response = await fetch(`${API_URL}/destinations/`, { headers: { 'Authorization': `Bearer ${token}` } });
                if (response.ok) { setDestinations(await response.json()); }
            } catch (error) { console.error("Échec de la récupération des destinations:", error); }
        };
        fetchDestinations();
    }, [token]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) { setFile(e.target.files[0]); setError(''); }
    };

    const handleDragEnter = (e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); };
    const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); e.dataTransfer.dropEffect = 'copy'; setIsDragging(true); };
    const handleDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); };
    const handleDrop = (e) => {
        e.preventDefault(); e.stopPropagation(); setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const droppedFile = e.dataTransfer.files[0];
            const fileType = droppedFile.type;
            if (fileType === 'application/pdf' || fileType.startsWith('image/')) { setFile(droppedFile); setError(''); } else { setError('Type de fichier non supporté. Veuillez télécharger une image ou un PDF.'); }
        }
    };

    const triggerFileInput = () => { if (fileInputRef.current) { fileInputRef.current.click(); } };
    const handleReset = () => { setFile(null); setDestination(''); setError(''); };
    const handleSubmit = (e) => {
        e.preventDefault();
        if (!file) { setError('Veuillez sélectionner un fichier à télécharger.'); return; }
        const formData = new FormData();
        formData.append('file', file);
        if (destination) { formData.append('destination', destination); }
        onUpload(formData, file);
    };

    return (
        <div className="sid-card">
            <h3 style={{ marginTop: 0 }}>Ajouter un Passeport</h3>
            <p className="mb-2">Glissez votre document ci-dessous pour lancer l'extraction automatique.</p>
            {error && <p className="sid-alert sid-alert--err">{error}</p>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label className="sid-label">Destination (Optionnel)</label>
                    <input type="text" name="destination" value={destination} onChange={(e) => setDestination(e.target.value)} className="sid-input" list="destination-datalist-ocr" placeholder="Ex: Voyage Japon 2024" autoComplete="off" />
                    <datalist id="destination-datalist-ocr">{destinations.map(dest => <option key={dest} value={dest} />)}</datalist>
                </div>
                <div className="form-group">
                    <label className="sid-label">Document (Image ou PDF)</label>
                    <div className={`sid-dropzone ${isDragging ? 'is-dragover' : ''}`} onDragEnter={handleDragEnter} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop} onClick={triggerFileInput}>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/png, image/jpeg, image/jpg, application/pdf" style={{ display: 'none' }} />
                        <UploadIcon />
                        <strong>{file ? `Fichier prêt : ${file.name}` : "Cliquez ou glissez votre fichier ici"}</strong>
                        {!file && <small>PNG, JPG ou PDF jusqu'à 10Mo</small>}
                    </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.6rem', flexWrap: 'wrap' }}>
                    <button type="button" onClick={isUploading ? onCancelUpload : handleReset} className="sid-btn-outline">{isUploading ? "Annuler l'envoi" : 'Annuler'}</button>
                    {/* Disabled while uploading: a double-click used to create two jobs and burn double credits. */}
                    <button type="submit" className="sid-btn" disabled={!file || isUploading}>{isUploading ? 'Envoi en cours…' : "Lancer l'analyse"}</button>
                </div>
            </form>
        </div>
    );
}

// Processing-state chips, keyed by the job.status values the backend writes
// (backend/crud.py): 'processing', 'complete', 'failed'. No new status is
// introduced — 'queued' is only the fallback for a job whose status has not
// arrived yet.
const JOB_STATUS_CHIP = { processing: 'processing', complete: 'done', failed: 'failed' };
const JOB_STATUS_LABEL = { processing: 'En cours', complete: 'Terminé', failed: 'Échoué' };

function OcrJobMonitor({ token, refreshTrigger, onJobComplete, uploadingFile, uploadProgress, fetchUser, containerRef }) {
    const [jobs, setJobs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const knownCompletedRef = useRef(new Set());
    const jobsRef = useRef([]);
    useEffect(() => { jobsRef.current = jobs; }, [jobs]);

    const fetchJobs = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/ocr/jobs/`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) {
                const data = await response.json();
                // Merge monotonically: an in-flight poll response must not
                // roll back a fresher SSE job_progress patch.
                setJobs(prevJobs => data.map(job => {
                    const prev = prevJobs.find(p => p.id === job.id);
                    return (prev && job.status === 'processing' && (prev.progress || 0) > (job.progress || 0))
                        ? { ...job, progress: prev.progress } : job;
                }));
                let hasNewCompletion = false;
                data.forEach(job => {
                    if (job.status === 'complete' || job.status === 'failed') {
                        if (!knownCompletedRef.current.has(job.id)) {
                            knownCompletedRef.current.add(job.id);
                            hasNewCompletion = true;
                        }
                    }
                });
                if (hasNewCompletion) {
                    onJobComplete();
                    if (fetchUser) fetchUser(); // Update credits async when job finishes!
                }
                return data;
            } else { console.error('Échec de la récupération des jobs OCR.'); }
        } catch (err) { console.error('Une erreur est survenue lors de la récupération des jobs.', err); } finally { setIsLoading(false); }
        return null;
    }, [token, onJobComplete, fetchUser]);
    
    // Adaptive polling: 2s while a job is active (or an upload is in flight),
    // 15s when idle — an idle dashboard no longer hammers the same process
    // that runs the OCR jobs.
    useEffect(() => {
        let cancelled = false;
        let timer = null;
        const tick = async () => {
            // Decide the next interval from the list this tick just fetched —
            // jobsRef alone would be one render stale.
            const data = await fetchJobs();
            if (cancelled) return;
            const list = data || jobsRef.current;
            const active = !!uploadingFile || list.some(job => job.status === 'processing');
            timer = setTimeout(tick, active ? 2000 : 15000);
        };
        tick();
        return () => { cancelled = true; if (timer) clearTimeout(timer); };
    }, [fetchJobs, uploadingFile]);
    useEffect(() => { if (refreshTrigger > 0) { fetchJobs(); } }, [refreshTrigger, fetchJobs]);

    // Live job updates pushed over SSE: progress patches the job row directly
    // (no poll lag); completion triggers an immediate refetch. Polling above
    // stays as fallback if the SSE connection is down.
    useEffect(() => {
        const onJobEvent = (event) => {
            const data = event.detail || {};
            if (data.type === 'job_progress' && data.job_id) {
                setJobs(prevJobs => prevJobs.map(job => job.id === data.job_id ? { ...job, progress: data.progress } : job));
            } else if (data.type === 'job_update') {
                fetchJobs();
            }
        };
        window.addEventListener('ocr-job-event', onJobEvent);
        return () => window.removeEventListener('ocr-job-event', onJobEvent);
    }, [fetchJobs]);

    const handleRemoveJob = async (jobIdToRemove) => {
        if (!window.confirm("Voulez-vous vraiment supprimer ce job ?")) return;
        try {
            const response = await fetch(`${API_URL}/ocr/jobs/${jobIdToRemove}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) { setJobs(prevJobs => prevJobs.filter(job => job.id !== jobIdToRemove)); } else { setError("Échec de la suppression du job."); }
        } catch (err) { setError("Une erreur est survenue lors de la suppression du job."); }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        return new Date(dateString).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    };

    let displayJobs = [...jobs];
    if (uploadingFile) {
        const isRealJobPresent = jobs.length > 0 && jobs[0].file_name === uploadingFile.name;
        if (!isRealJobPresent) {
            // Real upload progress (0-100% of bytes sent) mapped onto the 0-14%
            // "Upload" segment of the bar, instead of a frozen 0%.
            displayJobs.unshift({ id: 'temp-virtual-id', file_name: uploadingFile.name, created_at: new Date().toISOString(), status: 'processing', progress: Math.min(14, Math.round((uploadProgress || 0) * 0.14)), successes: [], failures: [] });
        }
    }

    if (isLoading && !uploadingFile && jobs.length === 0) return null;
    if (error) return <p className="sid-alert sid-alert--err">{error}</p>;

    return (
        <div className="job-monitor sid-card" ref={containerRef}>
            <h3 style={{ marginTop: 0 }}>Fichiers en cours de traitement</h3>
            {displayJobs.length === 0 ? (
                <p className="sid-alert sid-alert--info">Aucun document récent.</p>
            ) : (
                <ul className="job-list">
                    {displayJobs.map(job => (
                        <li key={job.id} className="job-item">
                            <div className="job-header">
                                <div className="job-details">
                                    <strong style={{ display: 'block', marginBottom: '0.25rem' }}>{job.file_name}</strong>
                                    <small style={{ color: 'var(--sid-muted-strong)' }}>{formatDate(job.created_at)}</small>
                                </div>
                                <div className="job-actions">
                                    {/* Chip driven by job.status, the value the API already sends. */}
                                    <span className={`sid-chip sid-chip--${JOB_STATUS_CHIP[job.status] || 'queued'}`}>{JOB_STATUS_LABEL[job.status] || JOB_STATUS_LABEL.processing}</span>
                                     {job.id !== 'temp-virtual-id' && ( <button onClick={() => handleRemoveJob(job.id)} className="sid-btn-ghost" style={{ padding: '0.25rem 0.5rem' }} aria-label="Supprimer ce job">X</button> )}
                                </div>
                            </div>
                            <ProgressBar progress={job.progress} status={job.status} />
                            {job.failures.length > 0 && (
                                <div className="failure-list">
                                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--sid-err)' }}>Échecs détectés ({job.failures.length}):</div>
                                    {job.failures.map((failure, index) => (
                                        <div key={index} className="failure-item"><FailureIcon /><span><b>Page {failure.page_number}</b> : {failure.detail}</span></div>
                                    ))}
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

// --- MAIN COMPONENTS (DEFINED BEFORE USE TO AVOID REFERENCE ERRORS) ---

function CrudForm({ item, isCreating, onSave, onCancel, fields, endpoint, token }) {
    const [formData, setFormData] = useState(item);
    const [destinations, setDestinations] = useState([]);
    const [error, setError] = useState('');
    useEffect(() => {
        const initialData = { ...item };
        Object.entries(fields).forEach(([key, type]) => { if (type === 'datetime-local' && initialData[key]) { initialData[key] = new Date(initialData[key]).toISOString().slice(0, 16); } });
        setFormData(initialData);
    }, [item, fields, endpoint, isCreating]);
    
    useEffect(() => {
        if (endpoint === 'passports') {
            const fetchDestinations = async () => {
                try {
                    const response = await fetch(`${API_URL}/destinations/`, { headers: { 'Authorization': `Bearer ${token}` } });
                    if (response.ok) setDestinations(await response.json());
                } catch (error) { console.error("Échec de la récupération des destinations:", error); }
            };
            fetchDestinations();
        }
    }, [endpoint, token]);

    const handleChange = (e) => { const { name, value, type, checked } = e.target; setFormData({ ...formData, [name]: type === 'checkbox' ? checked : value }); };
    const handleSubmit = async (e) => {
        e.preventDefault(); setError('');
        let url = isCreating ? `${API_URL}/${endpoint}/` : `${API_URL}/${endpoint}/${item.id}`;
        let method = isCreating ? 'POST' : 'PUT';
        let body = { ...formData };
        if (body.confidence_score === '') { body.confidence_score = null; }
        if (endpoint === 'admin/users' && !isCreating && !body.password) delete body.password;

        if (endpoint === 'admin/users') {
            body.uploaded_pages_count = parseInt(body.uploaded_pages_count, 10) || 0;
            body.page_credits = parseInt(body.page_credits, 10) || 0;
        }

        try {
            const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify(body), });
            if (response.ok) { onSave(); return; }
            // The body may be plain text (500) or a 422 whose detail is an
            // array — never let the error path itself throw silently.
            let detail = null;
            try { detail = (await response.json()).detail; } catch { /* non-JSON body */ }
            setError(typeof detail === 'string' ? detail : "Échec de l'enregistrement de l'élément.");
        } catch {
            setError("Une erreur est survenue lors de l'enregistrement.");
        }
    };
    const formFields = { ...fields };
    if (formFields.confidence_score) { delete formFields.confidence_score; }
    return (<form onSubmit={handleSubmit} className="sid-card"><h3>{isCreating ? 'Créer' : 'Modifier'}</h3>{error && <p className="sid-alert sid-alert--err">{error}</p>}<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem 1.5rem' }}>{Object.entries(formFields).map(([key, type]) => (<div className="form-group" key={key}><label className="sid-label">{columnTranslations[key] || key.replace(/_/g, ' ')}</label>{key === 'password' ? (<PasswordInput name={key} value={formData[key] || ''} onChange={handleChange} placeholder={!isCreating ? 'Laisser vide pour conserver' : ''} required={isCreating} />) : key === 'destination' ? (<><input type="text" name="destination" value={formData.destination || ''} onChange={handleChange} className="sid-input" list="destination-datalist-form" placeholder="Ex: Voyage 2024" autoComplete="off" /><datalist id="destination-datalist-form">{destinations.map(dest => <option key={dest} value={dest} />)}</datalist></>) : type === 'checkbox' ? (<input type="checkbox" name={key} checked={!!formData[key]} onChange={handleChange} className="sid-checkbox" />) : (<input type={type} name={key} value={formData[key] || ''} onChange={handleChange} className="sid-input" required={key !== 'destination' && type !== 'checkbox' && key !== 'uploaded_pages_count' && key !== 'page_credits'} />)}</div>))}</div><div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.6rem', flexWrap: 'wrap' }}><button type="button" onClick={onCancel} className="sid-btn-outline">Annuler</button><button type="submit" className="sid-btn">Enregistrer</button></div></form>);
}

function PreviewTable({ data }) {
    if (!data || data.length === 0) return <p className="sid-alert sid-alert--info mt-1">Aucune donnée trouvée.</p>;
    const headers = Object.keys(data[0]);
    return (<div className="mt-1"><h3 className="mb-1">Aperçu</h3><div className="sid-table-wrap"><table className="sid-table"><thead><tr>{headers.map(h => <th key={h}>{columnTranslations[h] || h.replace(/_/g, ' ')}</th>)}</tr></thead><tbody>{data.map((row, i) => <tr key={i}>{headers.map(h => <td key={h}>{String(row[h])}</td>)}</tr>)}</tbody></table></div></div>);
}

function ComboBoxFilter({ name, placeholder, options, getOptionValue, getOptionLabel, onChange }) {
    const dataListId = `datalist-${name}-${Math.random()}`;
    // The datalist shows only the human-readable label; the label of the
    // picked option is mapped back to its underlying value (e.g. the user id)
    // before being reported, so the filter query stays unchanged.
    const handleChange = (e) => {
        const typed = e.target.value;
        const match = options.find(option => getOptionLabel(option) === typed);
        onChange(name, match ? getOptionValue(match) : typed);
    };
    return (
        <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <input list={dataListId} name={name} placeholder={placeholder} onChange={handleChange} className="sid-input" autoComplete="off" />
            <datalist id={dataListId}><option value="">-- Aucun --</option>{options.map(option => (<option key={getOptionValue(option)} value={getOptionLabel(option)} />))}</datalist>
        </div>
    );
}

function CrudManager({ title, endpoint, token, user, fetchUser, fields, filterConfig, adminUsers, userDestinations }) {
    const [items, setItems] = useState([]);
    const [editingItem, setEditingItem] = useState(null);
    const [isCreating, setIsCreating] = useState(false);
    const [filters, setFilters] = useState({});
    // Type filter of the results table ('' = Tous, 'PASS', 'PI'); shared with
    // the export panel so the downloads contain exactly the rows on screen.
    const [docTypeFilter, setDocTypeFilter] = useState('');
    const [dynamicDestinations, setDynamicDestinations] = useState([]);
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [isBulkEditingDest, setIsBulkEditingDest] = useState(false);
    const [bulkDestination, setBulkDestination] = useState('');
    const [refreshJobsTrigger, setRefreshJobsTrigger] = useState(0);
    const [uploadingFile, setUploadingFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    // True only while the XHR is actually in flight — uploadingFile lingers
    // 2s after success for the placeholder card, during which cancelling or
    // blocking the submit button would be dishonest.
    const [isUploadInFlight, setIsUploadInFlight] = useState(false);
    const uploadXhrRef = useRef(null);

    // --- SCROLL REF ---
    const jobMonitorRef = useRef(null);
    
    // --- SORTING STATE ---
    const [sortConfig, setSortConfig] = useState([]); // Array of { key, direction }

    // --- INTEGRATED EXPORT PANEL STATE ---
    const [exportFilters, setExportFilters] = useState({ user_id: '', destination: '' });
    const [previewData, setPreviewData] = useState(null);

    const fetchDestinationsForUser = useCallback(async (userId) => {
        const query = userId ? `?user_id=${userId}` : '';
        try {
            const response = await fetch(`${API_URL}/destinations/${query}`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) { setDynamicDestinations(await response.json()); }
        } catch (error) { console.error("Échec de la récupération des destinations:", error); }
    }, [token]);

    useEffect(() => { if (user.role === 'admin' && endpoint === 'passports') { fetchDestinationsForUser(null); } }, [user, endpoint, fetchDestinationsForUser]);

    const handleFilterChange = (filterName, value) => {
        const newFilters = { ...filters, [filterName]: value };
        if (user.role === 'admin' && filterName === 'user_filter') { fetchDestinationsForUser(value || null); newFilters.voyage_filter = ''; }
        setFilters(newFilters);
        // The table filters also narrow the export, so a preview of the previous rows is stale.
        setPreviewData(null);
    };
    const handleDocTypeFilterChange = (value) => {
        setDocTypeFilter(value);
        // Hidden rows must not stay selected, and a preview of the previous
        // filter must not be mistaken for the current export.
        setSelectedIds(new Set()); setIsBulkEditingDest(false); setBulkDestination('');
        setPreviewData(null);
    };
    // Rows currently displayed: the fetched rows narrowed by the type filter.
    const visibleItems = useMemo(() => (endpoint === 'passports' ? filterByDocumentType(items, docTypeFilter) : items), [items, docTypeFilter, endpoint]);

    const fetchData = useCallback(async () => {
        const activeFilters = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
        const query = new URLSearchParams(activeFilters);
        const url = `${API_URL}/${endpoint}/?${query.toString()}`;
        try {
            const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
            if (response.ok) setItems(await response.json()); else console.error("Échec de la récupération des données pour", endpoint);
        } catch (error) { console.error("Erreur lors de la récupération des données:", error); }
        setSelectedIds(new Set()); setIsBulkEditingDest(false); setBulkDestination('');
    }, [endpoint, token, filters]);
    
    useEffect(() => { fetchData(); }, [fetchData]);

    const handleDelete = async (id) => {
        if (window.confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            await fetch(`${API_URL}/${endpoint}/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
            fetchData();
        }
    };
    
    const handleSave = () => { setEditingItem(null); setIsCreating(false); setSelectedIds(new Set()); fetchData(); };
    const handleUpload = (formData, fileObj) => {
        setUploadingFile(fileObj); setSelectedIds(new Set()); setUploadProgress(0); setIsUploadInFlight(true);
        // XMLHttpRequest instead of fetch: fetch cannot report upload progress.
        const xhr = new XMLHttpRequest();
        uploadXhrRef.current = xhr;
        xhr.open('POST', `${API_URL}/passports/upload-and-extract/`);
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        // Stall watchdog instead of a flat total timeout: a slow-but-moving
        // large upload must never be aborted, only one with no bytes moving.
        let lastProgressAt = Date.now();
        const stallWatchdog = setInterval(() => {
            if (Date.now() - lastProgressAt > 60000) {
                clearInterval(stallWatchdog);
                alert('Le téléchargement semble bloqué et a été annulé. Vérifiez votre connexion et réessayez.');
                xhr.abort();
            }
        }, 5000);
        xhr.upload.onprogress = (e) => { lastProgressAt = Date.now(); if (e.lengthComputable) { setUploadProgress(Math.round((e.loaded / e.total) * 100)); } };
        xhr.onload = () => {
            clearInterval(stallWatchdog);
            uploadXhrRef.current = null;
            setIsUploadInFlight(false);
            if (xhr.status >= 200 && xhr.status < 300) {
                setRefreshJobsTrigger(prev => prev + 1);
                // --- SCROLL TO JOB MONITOR ---
                setTimeout(() => {
                    if (jobMonitorRef.current) {
                        jobMonitorRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 100);
                setTimeout(() => { setUploadingFile(null); }, 2000);
            } else {
                let detail = 'Erreur inconnue';
                try { detail = JSON.parse(xhr.responseText).detail || detail; } catch { /* non-JSON error body */ }
                alert(`Erreur de téléchargement: ${detail}`);
                setUploadingFile(null);
            }
        };
        xhr.onerror = () => { clearInterval(stallWatchdog); uploadXhrRef.current = null; setIsUploadInFlight(false); alert('Une erreur inattendue est survenue lors du téléchargement.'); setUploadingFile(null); };
        xhr.onabort = () => { clearInterval(stallWatchdog); uploadXhrRef.current = null; setIsUploadInFlight(false); setUploadingFile(null); };
        xhr.send(formData);
    };
    const handleCancelUpload = () => { if (uploadXhrRef.current) { uploadXhrRef.current.abort(); } };
    const handleJobComplete = useCallback(() => { fetchData(); }, [fetchData]);
    const handleCancel = () => { setEditingItem(null); setIsCreating(false); setSelectedIds(new Set()); }
    const startCreating = () => {
        let newItem = Object.keys(fields).reduce((acc, key) => ({ ...acc, [key]: '' }), {});
        if (endpoint === 'admin/users') { newItem.role = 'user'; newItem.uploaded_pages_count = 0; newItem.page_credits = 0; }
        setEditingItem(newItem); setIsCreating(true);
    };
    const handleToggleSelect = (id) => { setSelectedIds(prev => { const newSet = new Set(prev); if (newSet.has(id)) { newSet.delete(id); } else { newSet.add(id); } return newSet; }); };
    const handleToggleSelectAll = () => { if (selectedIds.size === visibleItems.length) { setSelectedIds(new Set()); } else { setSelectedIds(new Set(visibleItems.map(i => i.id))); } };
    const handleMultiDelete = async () => {
        if (window.confirm(`Êtes-vous sûr de vouloir supprimer ${selectedIds.size} passeports ?`)) {
            const payload = { passport_ids: Array.from(selectedIds) };
            try {
                const response = await fetch(`${API_URL}/passports/delete-multiple`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (response.ok) { fetchData(); } else { const errorData = await response.json(); alert(`Échec de la suppression multiple: ${errorData.detail}`); }
            } catch (err) { alert(`Une erreur est survenue: ${err.message}`); }
        }
    };

    // --- INTEGRATED EXPORT LOGIC ---
    const handleExportFilterChange = (name, value) => { setExportFilters(prev => ({ ...prev, [name]: value })); setPreviewData(null); };
    
    const getServerExportData = async (preview = false, format = 'xlsx') => {
        const query = buildExportQuery({ exportFilters, tableFilters: filters, role: user.role, docTypeFilter, format, preview });
        try {
            const response = await fetch(`${API_URL}/export/data?${query}`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (!response.ok) { const err = await response.json(); alert(`Échec de la récupération des données: ${err.detail}`); return null; }
            return response;
        } catch (error) { alert('Une erreur est survenue lors de la récupération des données.'); return null; }
    };

    const handlePreview = async () => {
        const response = await getServerExportData(true);
        if (response) {
            setPreviewData(await response.json());
        }
    };

    const handleUnifiedExport = async (format = 'xlsx') => {
        if (selectedIds.size > 0) {
            // -- EXPORT SELECTION (file built server-side, CSV or Excel) --
            try {
                const response = await fetch(`${API_URL}/export/data/selection?format=${format}`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ passport_ids: Array.from(selectedIds) }) });
                if (!response.ok) { const err = await response.json(); alert(`Échec de l'exportation: ${err.detail}`); return; }
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a'); link.href = url; link.setAttribute('download', downloadFilename(response.headers.get('content-disposition'), 'selection_passeports', format));
                document.body.appendChild(link); link.click(); document.body.removeChild(link);
            } catch (err) { alert("Une erreur est survenue lors de l'exportation."); }
        } else {
            // -- EXPORT FILTERED (Server-Side, CSV or Excel; honours the type filter) --
            const response = await getServerExportData(false, format);
            if (response) {
                const blob = await response.blob();
                const filename = downloadFilename(response.headers.get('content-disposition'), 'passports_export', format);
                const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
                setPreviewData(null);
            }
        }
    };

    const handleBulkEditSubmit = async (e) => {
        e.preventDefault(); if (!bulkDestination) return;
        const promises = Array.from(selectedIds).map(async (id) => {
            const item = items.find(i => i.id === id); if (!item) return;
            const payload = { first_name: item.first_name, last_name: item.last_name, birth_date: item.birth_date, expiration_date: item.expiration_date, nationality: item.nationality, passport_number: item.passport_number, confidence_score: item.confidence_score, destination: bulkDestination };
            return fetch(`${API_URL}/passports/${id}`, { method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        });
        await Promise.all(promises); fetchData();
    };

    // --- UPDATED SORTING LOGIC ---
    
    // 1. Toggling the Checkbox adds/removes the column from the sort stack
    const handleMultiSortToggle = (key, isChecked) => {
        let newSortConfig = [...sortConfig];
        
        if (isChecked) {
            // Add to end of stack (Last checked = Last priority in array, effectively handled as secondary/tertiary sort)
            if (!newSortConfig.find(s => s.key === key)) {
                newSortConfig.push({ key, direction: 'asc' });
            }
        } else {
            // Remove from stack
            newSortConfig = newSortConfig.filter(s => s.key !== key);
        }
        setSortConfig(newSortConfig);
    };

    // 2. Clicking the Header Text toggles direction (if active) OR sets as Single Sort (if inactive)
    const handleHeaderClick = (key) => {
        const existingSortIndex = sortConfig.findIndex(s => s.key === key);

        if (existingSortIndex !== -1) {
            // It is already active (either single or part of multi-sort).
            // Just toggle direction. Do NOT clear others.
            const newSortConfig = [...sortConfig];
            newSortConfig[existingSortIndex].direction = newSortConfig[existingSortIndex].direction === 'asc' ? 'desc' : 'asc';
            setSortConfig(newSortConfig);
        } else {
            // It is NOT active.
            // Clicking the text means "I want to sort by THIS only".
            // Reset stack to just this one.
            setSortConfig([{ key, direction: 'asc' }]);
        }
    };

    const sortedItems = useMemo(() => {
        let sortableItems = [...visibleItems];
        if (sortConfig.length > 0) {
            sortableItems.sort((a, b) => {
                for (const sort of sortConfig) {
                    const key = sort.key;
                    const direction = sort.direction;
                    
                    let aValue = key === 'document_type' ? getDocumentType(a) : a[key];
                    let bValue = key === 'document_type' ? getDocumentType(b) : b[key];

                    if (aValue === bValue) continue; 
                    if (aValue === null || aValue === undefined || aValue === '') return 1;
                    if (bValue === null || bValue === undefined || bValue === '') return -1;

                    const fieldType = fields[key];
                    if (fieldType === 'number' || typeof aValue === 'number') {
                          const numA = parseFloat(aValue);
                          const numB = parseFloat(bValue);
                          if (numA < numB) return direction === 'asc' ? -1 : 1;
                          if (numA > numB) return direction === 'asc' ? 1 : -1;
                    } 
                    else if (fieldType === 'date' || fieldType === 'datetime-local' || key.includes('date')) {
                          if (aValue < bValue) return direction === 'asc' ? -1 : 1;
                          if (aValue > bValue) return direction === 'asc' ? 1 : -1;
                    }
                    else {
                        const strA = String(aValue).toLowerCase();
                        const strB = String(bValue).toLowerCase();
                        if (strA < strB) return direction === 'asc' ? -1 : 1;
                        if (strA > strB) return direction === 'asc' ? 1 : -1;
                    }
                }
                return 0;
            });
        }
        return sortableItems;
    }, [visibleItems, sortConfig, fields]);

    if (editingItem) return <CrudForm item={editingItem} isCreating={isCreating} onSave={handleSave} onCancel={handleCancel} fields={fields} endpoint={endpoint} token={token} />;

    const displayFields = { ...fields };
    if (endpoint === 'admin/users') delete displayFields.password;
    // Passports: same columns and order as the export files (the derived Type
    // column PASS/PI sits between the document number and the destination),
    // see resultsHelpers.js.
    const displayColumns = endpoint === 'passports' ? PASSPORT_COLUMN_ORDER : Object.keys(displayFields);

    // Use dynamic destinations (if admin looking at a user) or generic user destinations for the bulk list
    const availableBulkDestinations = (user.role === 'admin' && dynamicDestinations.length > 0) ? dynamicDestinations : userDestinations;

    // The row's actions, rendered identically in the table and in the cards.
    const rowActions = (item) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={() => setEditingItem(item)} className="sid-btn-ghost">Modifier</button>
            {endpoint !== 'passports' && ( <button onClick={() => handleDelete(item.id)} className="sid-btn-ghost">Suppr</button> )}
        </div>
    );

    return (
        <div>
            {endpoint === 'passports' && ( <> <OcrUploader token={token} onUpload={handleUpload} isUploading={isUploadInFlight} onCancelUpload={handleCancelUpload} /> <OcrJobMonitor token={token} refreshTrigger={refreshJobsTrigger} onJobComplete={handleJobComplete} uploadingFile={uploadingFile} uploadProgress={uploadProgress} fetchUser={fetchUser} containerRef={jobMonitorRef} /> </> )}
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }} className="mb-1">
                <h2>{title}</h2>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    {endpoint === 'passports' && selectedIds.size > 0 && ( <> {isBulkEditingDest ? ( <form onSubmit={handleBulkEditSubmit} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}><input type="text" className="sid-input" placeholder="Nouvelle destination" value={bulkDestination} onChange={e => setBulkDestination(e.target.value)} list="bulk-dest-list" required style={{ width: '200px' }} /><datalist id="bulk-dest-list">{availableBulkDestinations && availableBulkDestinations.map(d => <option key={d} value={d} />)}</datalist><button type="submit" className="sid-btn">OK</button><button type="button" onClick={() => setIsBulkEditingDest(false)} className="sid-btn-outline">X</button></form> ) : ( <> <button onClick={() => setIsBulkEditingDest(true)} className="sid-btn-outline">Modifier Destination</button> <button onClick={handleMultiDelete} className="sid-btn-outline">Supprimer ({selectedIds.size})</button> </> )} </> )}
                    <button onClick={startCreating} className="sid-btn-outline">{endpoint === 'passports' ? '+ Manuel' : '+ Nouveau'}</button>
                </div>
            </div>

            {/* --- INTEGRATED EXPORT PANEL --- */}
            {endpoint === 'passports' && (
                <div className="sid-card">
                    <h3 style={{ marginTop: 0 }}>Exportation des Données</h3>
                    <div className="filter-bar mb-1">
                        {user.role === 'admin' && ( 
                            <ComboBoxFilter name="user_id" placeholder="Tous les utilisateurs" options={adminUsers || []} getOptionValue={(o) => o.id} getOptionLabel={(o) => `${o.first_name} ${o.last_name}`} onChange={handleExportFilterChange} /> 
                        )}
                        <ComboBoxFilter name="destination" placeholder="Toutes destinations" options={(userDestinations || []).map(d => ({ destination: d }))} getOptionValue={(o) => o.destination} getOptionLabel={(o) => o.destination} onChange={handleExportFilterChange} />
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                         <button onClick={handlePreview} className="sid-btn-ghost" disabled={selectedIds.size > 0}>Aperçu</button>
                         {/* XLSX is the primary of the pair, CSV the outline one. */}
                         <div className="sid-download-group">
                             <button onClick={() => handleUnifiedExport('xlsx')} className="sid-btn">
                                 {selectedIds.size > 0 ? `Exporter Sélection Excel (${selectedIds.size})` : 'Télécharger Excel'}
                             </button>
                             <button onClick={() => handleUnifiedExport('csv')} className="sid-btn-outline">
                                 {selectedIds.size > 0 ? `Exporter Sélection CSV (${selectedIds.size})` : 'Télécharger CSV'}
                             </button>
                         </div>
                    </div>
                    {previewData && selectedIds.size === 0 && ( <PreviewTable data={previewData} /> )}
                </div>
            )}
            {/* --- END EXPORT PANEL --- */}

            {endpoint.includes('users') && !filterConfig && ( <div className="filter-bar mb-1"><div className="form-group" style={{ flex: 1, marginBottom: 0 }}><input type="text" name="name_filter" placeholder="Rechercher (Nom, Email...)" onChange={(e) => handleFilterChange(e.target.name, e.target.value)} className="sid-input" autoComplete="off"/></div></div> )}
            {(filterConfig || endpoint === 'passports') && ( <div className="filter-bar mb-1">{filterConfig && filterConfig.map(filter => ( <ComboBoxFilter key={filter.name} {...filter} onChange={handleFilterChange} /> ))} {user.role === 'admin' && endpoint === 'passports' && ( <ComboBoxFilter key="voyage_filter" name="voyage_filter" placeholder="Filtrer par Destination" options={dynamicDestinations.map(d => ({ destination: d }))} getOptionValue={(o) => o.destination} getOptionLabel={(o) => o.destination} onChange={handleFilterChange} /> )} {endpoint === 'passports' && ( <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', whiteSpace: 'nowrap' }}><span className="sid-label" style={{ margin: 0 }}>Type</span><div className="sid-seg" role="group" aria-label="Filtrer par type de document (PASS = passeport, PI = pièce d'identité)" data-name="document_type_filter">{DOC_TYPE_FILTER_OPTIONS.map(option => ( <button key={option.value} type="button" value={option.value} className={docTypeFilter === option.value ? 'is-active' : ''} aria-pressed={docTypeFilter === option.value} onClick={() => handleDocTypeFilterChange(option.value)}>{option.label}</button> ))}</div></div> )} </div> )}
            {/* Both views are always mounted; only CSS decides which one shows,
                so a resize never unmounts a view and never loses state. */}
            <div className="sid-results">
            <div className="sid-table-wrap">
                <table className="sid-table">
                    <thead>
                        <tr>
                            {endpoint === 'passports' && ( <th className="checkbox-cell"><input type="checkbox" className="sid-checkbox" onChange={handleToggleSelectAll} checked={visibleItems.length > 0 && selectedIds.size === visibleItems.length} aria-label="Sélectionner tout" /></th> )}
                            {displayColumns.map(field => {
                                const sortState = sortConfig.find(s => s.key === field);
                                const sortIndex = sortConfig.findIndex(s => s.key === field);
                                const isChecked = !!sortState;

                                return ( 
                                    <th 
                                        key={field} 
                                        className="sortable" 
                                        onClick={(e) => handleHeaderClick(field)}
                                    >
                                        <div className="header-content">
                                            <input 
                                                type="checkbox" 
                                                className="sort-checkbox" 
                                                checked={isChecked}
                                                onClick={(e) => e.stopPropagation()} // Prevent header click trigger
                                                onChange={(e) => handleMultiSortToggle(field, e.target.checked)}
                                                title="Activer/Désactiver le tri sur cette colonne"
                                            />
                                            <span>{columnTranslations[field] || field.replace(/_/g, ' ')}</span>
                                            
                                            {/* Visual Indicator of Direction & Priority */}
                                            <span className={`sort-indicator ${sortState ? 'active' : ''}`}>
                                                {sortState ? (
                                                    <span className="sort-badge">
                                                        {sortState.direction === 'asc' ? '↑' : '↓'}
                                                        {sortConfig.length > 1 && <small>{sortIndex + 1}</small>}
                                                    </span>
                                                ) : '↕'}
                                            </span>
                                        </div>
                                    </th> 
                                );
                            })}
                            <th>{columnTranslations['actions']}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedItems.length === 0 ? ( <tr><td colSpan={displayColumns.length + 2}><div className="sid-empty">Aucune donnée trouvée.</div></td></tr> ) : sortedItems.map(item => (
                            <tr key={item.id} className={selectedIds.has(item.id) ? 'selected-row' : ''}>
                                {endpoint === 'passports' && ( <td className="checkbox-cell"><input type="checkbox" className="sid-checkbox" onChange={() => handleToggleSelect(item.id)} checked={selectedIds.has(item.id)} aria-label={`Sélectionner ${item.first_name} ${item.last_name}`} /></td> )}
                                {/* Cell values come from resultCellValue — the same function the
                                    card list below uses, so the two views cannot drift. */}
                                {displayColumns.map(field => (
                                    <td key={field} data-field={field}>{field === 'document_type'
                                        ? <span className={`sid-badge sid-badge--${resultCellValue(item, field, fields) === DOC_TYPE_PASSPORT ? 'pp' : 'pi'}`}>{resultCellValue(item, field, fields)}</span>
                                        : resultCellValue(item, field, fields)}</td>
                                ))}
                                <td className="actions-cell">{rowActions(item)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Mobile view of the very same rows and the very same displayColumns.
                Shown below 720 px by CSS alone — see scanid-app.css. */}
            <div className="sid-card-list">
                {sortedItems.length === 0 ? ( <div className="sid-empty">Aucune donnée trouvée.</div> ) : sortedItems.map(item => {
                    const typeValue = endpoint === 'passports' ? resultCellValue(item, 'document_type', fields) : null;
                    return (
                        <div key={item.id} className="sid-card-item">
                            <div className="sid-card-item__head">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                    {endpoint === 'passports' && ( <input type="checkbox" className="sid-checkbox" onChange={() => handleToggleSelect(item.id)} checked={selectedIds.has(item.id)} aria-label={`Sélectionner ${item.first_name} ${item.last_name}`} /> )}
                                    {typeValue !== null && ( <span className={`sid-badge sid-badge--${typeValue === DOC_TYPE_PASSPORT ? 'pp' : 'pi'}`} data-field="document_type">{typeValue}</span> )}
                                </div>
                                {rowActions(item)}
                            </div>
                            {displayColumns.filter(field => field !== 'document_type').map(field => (
                                <div className="sid-card-item__row" key={field}>
                                    <span className="sid-card-item__label">{columnTranslations[field] || field.replace(/_/g, ' ')}</span>
                                    <span className="sid-card-item__value" data-field={field}>{resultCellValue(item, field, fields)}</span>
                                </div>
                            ))}
                        </div>
                    );
                })}
            </div>
            </div>
        </div>
    );
}