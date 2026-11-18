// Cliente de la API: todas las pantallas llaman al backend con apiFetch().
// La sesión viaja en cookies HttpOnly: este código nunca ve los tokens (AGENTS.md §5.7).
const REFRESH_PATH = '/api/v1/auth/refresh';
// Estas dos rutas no se reintentan: si fallan, no tiene sentido renovar la sesión
const NO_RETRY = new Set([REFRESH_PATH, '/api/v1/auth/login']);

// Ir al login. Está en un objeto para poder reemplazarlo en los tests
export const navigation = { toLogin: () => window.location.assign('index.html') };

// Promesa de la renovación en curso (null si no hay ninguna)
let pendingRefresh = null;

// ─── Enviar una petición ────────────────────────────────────────────────────
// Agrega las cookies y convierte el objeto `json` en texto JSON
function send(path, { json, headers, ...options } = {}) {
  return fetch(path, {
    credentials: 'same-origin',
    ...options,
    headers: { 'Content-Type': 'application/json', ...headers },
    body: json === undefined ? options.body : JSON.stringify(json),
  });
}

// ─── Renovar la sesión ──────────────────────────────────────────────────────
// Si varias peticiones vencen a la vez, comparten una sola renovación (el token se rota en cada uso)
function refreshSession() {
  pendingRefresh ??= send(REFRESH_PATH, { method: 'POST' }).finally(() => {
    pendingRefresh = null;
  });
  return pendingRefresh;
}

// ─── Petición con renovación automática ─────────────────────────────────────
// Si el backend responde 401 (sesión vencida), renueva y repite la petición una vez.
// Si la renovación también falla, manda al login.
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

// ─── Mensaje de error ───────────────────────────────────────────────────────
// Saca el texto del formato de error único: { errors: [ { message } ] } (AGENTS.md §4)
export async function errorMessage(response) {
  try {
    const body = await response.json();
    return body.errors[0].message;
  } catch {
    return 'Ocurrió un error inesperado. Intenta de nuevo.';
  }
}
