/**
 * Shared TypeScript types matching the backend's APIResponse envelope.
 *
 * The backend always returns:
 *   { message: string, code: number, data: T, error: Record<string, unknown> }
 */

// ---------- API envelope ----------

export interface ApiEnvelope<T = Record<string, unknown>> {
  message: string;
  code: number;
  data: T;
  error: Record<string, unknown>;
}

// ---------- Auth ----------

export interface AuthTokens {
  access: string;
}

export interface UserInfo {
  id: number;
  name: string;
  email: string;
  is_staff: boolean;
}

/** Shape returned by both POST /auth/token/ and POST /auth/signup/ */
export interface AuthData {
  user: UserInfo;
  token: AuthTokens;
}

// ---------- Health ----------

export interface HealthResult {
  ok: boolean;
  detail: string;
}
