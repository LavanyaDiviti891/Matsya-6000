// Central place that decides where the backend lives. Reads VITE_API_BASE_URL
// / VITE_WS_BASE_URL at build time (Vite env convention) and falls back to
// localhost for local dev. See .env.example for hosted-deployment usage.

const envHttpBase = import.meta.env?.VITE_API_BASE_URL
const envWsBase = import.meta.env?.VITE_WS_BASE_URL

const DEFAULT_HOST = 'localhost:8000'

export const API_BASE_URL = envHttpBase || `http://${DEFAULT_HOST}`
export const WS_BASE_URL = envWsBase || `ws://${DEFAULT_HOST}/ws`
