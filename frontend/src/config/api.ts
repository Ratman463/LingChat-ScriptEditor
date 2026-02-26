// API configuration for different environments

// Always use localhost:8000 for the backend API
// - In development: Vite proxy forwards /api requests to localhost:8000
// - In Electron: The backend runs on localhost:8000
// Note: import.meta.env.DEV doesn't work correctly in Electron builds
const API_BASE_URL = 'http://localhost:8000'

export const apiBaseUrl = API_BASE_URL
