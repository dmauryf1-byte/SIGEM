import { renderSidebar, renderTopBar } from './shared/layout.js';

// shortcut: usuario fijo hasta SIGEM-004, que lo toma de la sesión
const user = { name: 'Administrador', role: 'Administrador' };

renderSidebar(document.getElementById('sidebar'), { current: 'dashboard', user });
renderTopBar(document.getElementById('topbar'), {
  title: 'Dashboard',
  subtitle: 'Resumen general del negocio',
  user,
});
