// Arranque común de todas las pantallas internas (todas menos el login).
import { currentUser, logout } from './auth.js';
import { renderSidebar, renderTopBar } from './layout.js';
import { setupChips, setupModals } from './ui.js';

// ─── Iniciar una pantalla ───────────────────────────────────────────────────
// 1. Pregunta al backend quién inició sesión (si nadie, auth.js manda al login).
// 2. Dibuja el menú lateral y la barra superior.
// 3. Activa los modales y los botones de filtro de la página.
export async function startPage({ current, title, subtitle, actions }) {
  const user = await currentUser();
  if (!user) return null;

  renderSidebar(document.getElementById('sidebar'), { current, user, onLogout: logout });
  renderTopBar(document.getElementById('topbar'), { title, subtitle, user, actions });
  setupModals();
  setupChips();
  return user;
}
