import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

// Self-hosted fonts (Fontsource, npm) — no runtime request to Google, so no
// visitor IP leaves the server. The paths below are the real files shipped by
// @fontsource 5.x: one stylesheet per weight at the package root.
// Only the weights the design system actually uses are imported.
import '@fontsource/space-grotesk/400.css'
import '@fontsource/space-grotesk/500.css'
import '@fontsource/space-grotesk/600.css'
import '@fontsource/space-grotesk/700.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/400-italic.css'

// The design system, imported once and globally, after the fonts it references.
import './scanid-app.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
