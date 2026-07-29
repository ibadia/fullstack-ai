/**
 * Auth service — handles login, signup, and token management.
 *
 * Pattern:
 * - Access token: Saved in-memory (JS variable). Safest route to prevent XSS sniffing.
 * - Refresh token: Saved in HttpOnly cookie by backend. JS has no access to it.
 */

import { apiFetch } from "./api";
import type { AuthData, AuthTokens } from "./types";

// ─── Token storage (In-memory) ───────────────────────────────────

let memoryAccessToken: string | null = null;
let memoryRefreshToken: string | null = null;

export function getAccessToken(): string | null {
  return memoryAccessToken;
}

export function storeTokens(tokens: AuthTokens): void {
  memoryAccessToken = tokens.access;
  memoryRefreshToken = tokens.refresh;
}

export function clearTokens(): void {
  memoryAccessToken = null;
  memoryRefreshToken = null;
}

// ─── Auth operations ─────────────────────────────────────────────

/**
 * Log in with email + password.
 * Backend will give you token which has both access token and refresh token
 */
export async function login(email: string, password: string): Promise<AuthTokens> {
  const data = await apiFetch<AuthData>("/auth/token/", {
    method: "POST",
    body: { email, password },
  });
  return data.token;
}

export async function signup(
  email: string,
  password: string,
  confirmPassword: string
): Promise<AuthTokens> {
  const data = await apiFetch<AuthData>("/auth/signup/", {
    method: "POST",
    body: { email, password, confirm_password: confirmPassword },
  });
  return data.token;
}

/**
 * Attempts to get a fresh access token using the stored refresh token.
 * Used after a page reload wipes the in-memory access token.
 */
export async function refreshAccessToken(): Promise<string | null> {
  if (!memoryRefreshToken) return null;

  try {
    const data = await apiFetch<AuthData>("/auth/token/refresh/", {
      method: "POST",
      body: { refresh: memoryRefreshToken },
    });
    memoryAccessToken = data.token.access;
    return memoryAccessToken;
  } catch {
    clearTokens();
    return null;
  }
}