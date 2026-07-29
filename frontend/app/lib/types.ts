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

export interface ReceiptData {
  id: number;
  status: "pending" | "processing" | "done" | "failed";
  extracted_data: Record<string, unknown> | null;
  total_amount: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ReceiptSummary {
  total_count: number;
  total_sum: number;
}