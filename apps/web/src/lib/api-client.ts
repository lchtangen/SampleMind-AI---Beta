/**
 * @fileoverview Typed API client for the SampleMind AI web frontend.
 *
 * Provides a thin wrapper around the native `fetch` API tailored to the
 * FastAPI backend. Key features:
 *
 * - **Base URL resolution** — reads `NEXT_PUBLIC_API_URL` (defaults to
 *   `http://localhost:8000`) and strips trailing slashes.
 * - **JWT injection** — automatically attaches a `Bearer` token from
 *   `localStorage` (key: `samplemind_token`) when present.
 * - **Typed errors** — non-2xx responses throw {@link ApiError} with
 *   HTTP status, status text, and an optional `detail` message parsed
 *   from the JSON body.
 * - **Multipart uploads** — {@link apiUpload} skips `Content-Type` so
 *   the browser auto-sets the correct `multipart/form-data` boundary.
 *
 * @example
 * ```ts
 * import { apiFetch } from "@/lib/api-client";
 *
 * const summary = await apiFetch<LibrarySummary>("/api/v1/analytics/summary");
 * ```
 *
 * @module lib/api-client
 */

/**
 * Base URL for all API requests.
 * Resolved from the `NEXT_PUBLIC_API_URL` env var, falling back to localhost.
 */
const BASE_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
    /\/$/,
    ""
  );

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

/**
 * Custom error class thrown when the FastAPI backend returns a non-2xx response.
 *
 * @example
 * ```ts
 * try {
 *   await apiFetch("/api/v1/missing");
 * } catch (err) {
 *   if (err instanceof ApiError && err.status === 404) { ... }
 * }
 * ```
 */
export class ApiError extends Error {
  /**
   * @param status    - HTTP status code (e.g. 401, 404, 500).
   * @param statusText - HTTP status text (e.g. "Not Found").
   * @param message    - Optional detail message extracted from the response body.
   */
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    message?: string
  ) {
    super(message ?? `API error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Token helpers (client-side only)
// ---------------------------------------------------------------------------

/**
 * Retrieve the stored JWT token from localStorage.
 * Returns `null` during SSR (no `window`).
 */
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("samplemind_token");
}

/** Persist a JWT token to localStorage for subsequent API requests. */
export function setToken(token: string): void {
  localStorage.setItem("samplemind_token", token);
}

/** Remove the stored JWT token (e.g. on logout). */
export function clearToken(): void {
  localStorage.removeItem("samplemind_token");
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

/**
 * Generic JSON fetch wrapper targeting the FastAPI backend.
 *
 * Automatically:
 * - Prepends {@link BASE_URL} to the provided path.
 * - Sets `Content-Type: application/json`.
 * - Injects `Authorization: Bearer <token>` when a JWT is stored.
 * - Throws {@link ApiError} on non-2xx responses.
 * - Returns `undefined` (cast to `T`) for 204 No Content responses.
 *
 * @typeParam T - Expected shape of the parsed JSON response.
 * @param path - API path starting with `/` (e.g. `/api/v1/analytics/summary`).
 * @param init - Optional `RequestInit` overrides (method, body, headers, etc.).
 * @returns Parsed JSON body typed as `T`.
 * @throws {ApiError} On non-2xx HTTP responses.
 *
 * @example
 * ```ts
 * const data = await apiFetch<LibrarySummary>("/api/v1/analytics/summary");
 * ```
 */
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let message: string | undefined;
    try {
      const body = await response.json();
      message = body?.detail ?? body?.message;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(response.status, response.statusText, message);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

/**
 * Multipart file upload helper.
 *
 * Unlike {@link apiFetch}, this function omits the `Content-Type` header so
 * the browser automatically sets the `multipart/form-data` boundary.
 *
 * @typeParam T - Expected shape of the parsed JSON response.
 * @param path     - API path (e.g. `/api/v1/ai/faiss/audio`).
 * @param formData - `FormData` instance containing the file(s) to upload.
 * @returns Parsed JSON body typed as `T`.
 * @throws {ApiError} On non-2xx HTTP responses.
 *
 * @example
 * ```ts
 * const form = new FormData();
 * form.append("file", audioFile);
 * const results = await apiUpload<FAISSSearchResponse>("/api/v1/ai/faiss/audio", form);
 * ```
 */
export async function apiUpload<T>(
  path: string,
  formData: FormData
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    let message: string | undefined;
    try {
      const body = await response.json();
      message = body?.detail ?? body?.message;
    } catch {
      // ignore
    }
    throw new ApiError(response.status, response.statusText, message);
  }

  return response.json() as Promise<T>;
}
