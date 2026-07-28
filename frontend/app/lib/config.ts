/**
 * Centralised configuration — the only file that reads import.meta.env.
 * Every other module imports typed constants from here.
 */

const raw = import.meta.env.VITE_API_URL;
if (!raw) {
  throw new Error(
    "VITE_API_URL is not set. Copy .env.example → .env.local and fill it in."
  );
}

export const API_URL: string = raw;