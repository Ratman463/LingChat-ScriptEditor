// API configuration for different environments

// In Electron production, use localhost:8000
// In development, Vite proxy handles this
const API_BASE_URL = import.meta.env.DEV ? '' : 'http://localhost:8000'

export const apiBaseUrl = API_BASE_URL