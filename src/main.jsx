import React from 'react'
import ReactDOM from 'react-dom/client'
import Devia from '../devia.jsx'

// DEBUG : marqueur de demarrage (si ce log reapparait en plein ecran = vrai reload de page)
console.log("[DEVIA STARTUP] App montee a", new Date().toLocaleTimeString(), "| timestamp:", Date.now());

// DEBUG : detecter un vrai reload / unload de la page
window.addEventListener("beforeunload", () => {
  console.log("[DEVIA STARTUP] !!! La page va se RECHARGER/fermer (beforeunload)");
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Devia />
  </React.StrictMode>
)
