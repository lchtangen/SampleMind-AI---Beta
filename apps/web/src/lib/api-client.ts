/**
 * SampleMind AI — Typed API client
 *
 * Thin wrapper around fetch that:
 *  - Points to the FastAPI backend (NEXT_PUBLIC_API_URL or localhost:8000)
 *  - Injects Authorization header when a JWT token is present
 *  - Throws a typed ApiError on non-2xx responses
 */

const BASE_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
    /\/$/,
    ""
  );

// ---------------------------------------------------------------------------
// Error type
// ---------------------------------------------------------------------------

export class ApiError extends Error {
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

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("samplemind_token");
}

export function setToken(token: string): void {
  localStorage.setItem("samplemind_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("samplemind_token");
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

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
 * Multipart file upload helper (skips Content-Type so browser sets boundary).
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
