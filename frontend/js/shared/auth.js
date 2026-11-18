// Sesión del usuario: quién está conectado y cómo cerrar sesión.
import { apiFetch, navigation } from './api.js';

// ─── Usuario actual ─────────────────────────────────────────────────────────
// Devuelve { name, role, username } o null (y en ese caso manda al login)
export async function currentUser() {
  const response = await apiFetch('/api/v1/auth/me');
  if (!response.ok) {
    navigation.toLogin();
    return null;
  }
  const user = await response.json();
  return { name: user.full_name, role: user.role, username: user.username };
}

// ─── Cerrar sesión ──────────────────────────────────────────────────────────
// Le pide al backend que borre las cookies y vuelve al login pase lo que pase
export async function logout() {
  try {
    await apiFetch('/api/v1/auth/logout', { method: 'POST' });
  } finally {
    navigation.toLogin();
  }
}
