
export type HttpResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string };

export function getApiBaseUrl() {
  return "http://localhost:8000";
}

export function parseApiError(data: unknown, status: number): string {
  if (
    data &&
    typeof data === "object" &&
    "detail" in data &&
    typeof data.detail === "string"
  ) {
    return data.detail;
  }

  return `HTTP ${status}`;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<HttpResult<T>> {
  try {
    const res = await fetch(`${getApiBaseUrl()}${path}`, {
      method,
      headers: body !== undefined
        ? { "Content-Type": "application/json" }
        : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      let error = `HTTP ${res.status}`;

      try {
        error = parseApiError(await res.json(), res.status);
      } catch {
        // Response was not JSON.
      }

      return { ok: false, error };
    }

    if (res.status === 204) {
      return { ok: true, data: undefined as T };
    }

    return { ok: true, data: (await res.json()) as T };
  } catch (e) {
    return {
      ok: false,
      error: e instanceof Error ? e.message : "Request failed",
    };
  }
}

export function httpGetJson<T>(path: string) {
  return request<T>("GET", path);
}

export function httpPostJson<TOut, TIn>(
  path: string,
  payload: TIn,
) {
  return request<TOut>("POST", path, payload);
}

export function httpDeleteJson<T>(
  path: string
) {
  return request<T>("DELETE", path);
}
