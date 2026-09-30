import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/plus-jakarta-sans'
import App from './App'
import './styles/global.scss'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Missing #root element in index.html')
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
