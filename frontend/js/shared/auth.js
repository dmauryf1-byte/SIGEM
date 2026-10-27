import { apiFetch, navigation } from './api.js';

// Usuario de la sesión, o null (apiFetch ya mandó al login si la sesión terminó)
export async function currentUser() {
  const response = await apiFetch('/api/v1/auth/me');
  if (!response.ok) {
    navigation.toLogin();
    return null;
  }
  const user = await response.json();
  return { name: user.full_name, role: user.role, username: user.username };
}

export async function logout() {
  try {
    await apiFetch('/api/v1/auth/logout', { method: 'POST' });
  } finally {
    navigation.toLogin();
  }
}
