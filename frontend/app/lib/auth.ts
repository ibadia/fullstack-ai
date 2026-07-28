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

export function getAccessToken(): string | null {
  return memoryAccessToken;
}

export function storeTokens(tokens: AuthTokens): void {
  memoryAccessToken = tokens.access;
}

export function clearTokens(): void {
  memoryAccessToken = null;
}

// ─── Auth operations ─────────────────────────────────────────────

/**
 * Log in with email + password.
 * Backend will automatically set an HttpOnly cookie for refresh token.
 */
export async function login(email: string, password: string): Promise<AuthTokens> {
  const data = await apiFetch<AuthData>("/auth/token/", {
    method: "POST",
    body: { email, password },
  });
  return data.token;
}

/**
 * Create a new account.
 * Backend will automatically set an HttpOnly cookie for refresh token.
 */
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