import { currentUser, logout } from './shared/auth.js';
import { renderSidebar, renderTopBar } from './shared/layout.js';

const user = await currentUser();

if (user) {
  renderSidebar(document.getElementById('sidebar'), {
    current: 'dashboard',
    user,
    onLogout: logout,
  });
  renderTopBar(document.getElementById('topbar'), {
    title: 'Dashboard',
    subtitle: 'Resumen general del negocio',
    user,
  });
}
