/**
 * Health service — checks backend availability.
 *
 * Note: The /healthcheck/ endpoint returns plain text, not the standard
 * API envelope, so we use raw fetch here instead of apiFetch.
 */

import { API_URL } from "./config";
import type { HealthResult } from "./types";

export async function checkBackendHealth(): Promise<HealthResult> {
  try {
    const res = await fetch(`${API_URL}/healthcheck/`);
    const text = await res.text();
    return { ok: res.ok, detail: text };
  } catch (err) {
    return {
      ok: false,
      detail: err instanceof Error ? err.message : "Unknown error",
    };
  }
}
