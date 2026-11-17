// Demo mode swaps the real HTTP client for an in-memory mock (see ./mockApi.js).
export const DEMO_MODE = process.env.REACT_APP_DEMO_MODE === "true";

// Base URL of the Flask API (no trailing slash).
export const API_URL = (process.env.REACT_APP_API_URL || "http://127.0.0.1:5000").replace(/\/$/, "");
