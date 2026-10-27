// Cliente de la API. La sesión viaja en cookies HttpOnly: este código nunca ve los tokens (AGENTS.md §5.7).
const REFRESH_PATH = '/api/v1/auth/refresh';
const NO_RETRY = new Set([REFRESH_PATH, '/api/v1/auth/login']);

// Se puede reemplazar en los tests
export const navigation = { toLogin: () => window.location.assign('index.html') };

let pendingRefresh = null;

function send(path, { json, headers, ...options } = {}) {
  return fetch(path, {
    credentials: 'same-origin',
    ...options,
    headers: { 'Content-Type': 'application/json', ...headers },
    body: json === undefined ? options.body : JSON.stringify(json),
  });
}

function refreshSession() {
  // Varias peticiones que vencen a la vez comparten una renovación: el token se rota en cada uso
  pendingRefresh ??= send(REFRESH_PATH, { method: 'POST' }).finally(() => {
    pendingRefresh = null;
  });
  return pendingRefresh;
}

export async function apiFetch(path, options = {}) {
  const response = await send(path, options);
  if (response.status !== 401 || NO_RETRY.has(path)) return response;

  const refreshed = await refreshSession();
  if (!refreshed.ok) {
    navigation.toLogin();
    return response;
  }
  return send(path, options);
}

export async function errorMessage(response) {
  try {
    const body = await response.json();
    return body.errors[0].message;
  } catch {
    return 'Ocurrió un error inesperado. Intenta de nuevo.';
  }
}
