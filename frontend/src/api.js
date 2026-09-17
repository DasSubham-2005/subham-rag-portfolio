export const API = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");
export const asset = (url) =>
  !url ? "" : url.startsWith("http") ? url : `${API}${url}`;
export async function api(path, options = {}) {
  const { token, body, ...rest } = options;
  const headers = {
    ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(rest.headers || {}),
  };
  const response = await fetch(`${API}${path}`, {
    ...rest,
    headers,
    body:
      body instanceof FormData || typeof body === "string"
        ? body
        : body
          ? JSON.stringify(body)
          : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(
      data.detail || data.message || `Request failed (${response.status})`,
    );
  return data;
}
