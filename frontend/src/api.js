const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

/**
 * Thin wrapper around fetch(). It does not duplicate any validation or
 * business logic - the Flask API is the single source of truth for that.
 * This just calls it and normalizes errors into a JS Error with a
 * user-facing message pulled from the API's {success, error} envelope.
 */
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Could not reach the API. Is the Flask server running?");
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // Non-JSON response (shouldn't happen against this API, but don't crash).
  }

  if (!response.ok) {
    throw new Error(body?.error || `Request failed (${response.status})`);
  }

  return body;
}

export function getUsers({ search = "", page = 1, limit = 8 } = {}) {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (search.trim()) params.set("search", search.trim());
  return request(`/users?${params.toString()}`);
}

export function createUser(data) {
  return request("/users", { method: "POST", body: JSON.stringify(data) });
}

export function getUser(id) {
  return request(`/users/${id}`);
}
