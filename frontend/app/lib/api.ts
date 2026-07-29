/**
 * Shared HTTP client — the only module that calls fetch().
 *
 * Every backend response follows the envelope:
 *   { message, code, data, error }
 *
 * apiFetch() unwraps that envelope:
 *   - On success → returns envelope.data (typed as T)
 *   - On failure → throws an Error with the backend's message or first error string
 */

import { API_URL } from "./config";
import { getAccessToken, refreshAccessToken} from "./auth";
import type { ApiEnvelope } from "./types";

export interface ApiFetchOptions {
  method?: string;
  body?: unknown;
  /** Attach Authorization: Bearer header when true */
  auth?: boolean;
}

export class ApiError extends Error {
  status: number;
  errors: Record<string, unknown>;

  constructor(message: string, status: number, errors: Record<string, unknown> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errors = errors;
  }
}

export async function apiFetch<T = Record<string, unknown>>(
  path: string,
  options: ApiFetchOptions = {}
): Promise<T> {
  const headers: Record<string, string> = {}
  const isFormData = options.body instanceof FormData;
  if (!isFormData) {  
    headers["Content-Type"] = "application/json";
  }

  if (options.auth) {
    let token = getAccessToken();
    if (!token){
      token = await refreshAccessToken();
    }
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    credentials: "include",
    body: isFormData ? (options.body as FormData) : options.body ? JSON.stringify(options.body) : undefined,
  });

  const json: ApiEnvelope<T> | null = await res.json().catch(() => null);

  if (!res.ok) {
    const message =
      json?.message || `Request failed (${res.status})`;
    throw new ApiError(message, res.status, json?.error ?? {});
  }

  // Unwrap the envelope — callers get data directly
  return json!.data;
}