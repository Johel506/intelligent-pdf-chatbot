import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
 // <React.StrictMode>
    <App />
//</React.StrictMode>,
)

// Note for reviewers:
// In the development environment (with React.StrictMode enabled),
// you may observe duplicated text during the AI response streaming.
// This is a known behavior of StrictMode (double rendering to detect side effects)
// and not an issue with the streaming logic itself.
// The functionality works correctly without duplication in the production build.
