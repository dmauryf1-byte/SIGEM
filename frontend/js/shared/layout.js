// Sidebar y barra superior del prototipo (App.tsx: Sidebar, TopBar). Todo con createElement/textContent (AGENTS.md §5.7).
import { icon } from './icons.js';

// href null = el módulo aún no tiene pantalla; cada tarea de módulo pone el suyo
export const NAV_ITEMS = [
  { key: 'dashboard', label: 'Inicio', icon: 'home', href: 'dashboard.html' },
  { key: 'clientes', label: 'Clientes', icon: 'users', href: null },
  { key: 'productos', label: 'Productos', icon: 'box', href: null },
  { key: 'vendedores', label: 'Vendedores', icon: 'userCheck', href: null },
  { key: 'proveedores', label: 'Proveedores', icon: 'truck', href: null },
  { key: 'facturas', label: 'Facturas', icon: 'fileText', href: null },
  { key: 'pagos', label: 'Pagos', icon: 'creditCard', href: null },
  { key: 'reportes', label: 'Reportes', icon: 'barChart', href: null },
  { key: 'usuarios', label: 'Usuarios', icon: 'shield', href: null, adminOnly: true },
];

const ADMIN_ROLE = 'Administrador';

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const initial = (name) => name.trim().charAt(0).toUpperCase();

function navLink(item, current) {
  const link = el('a', 'sidebar-item');
  link.append(icon(item.icon), item.label);
  if (!item.href) {
    link.setAttribute('aria-disabled', 'true');
    link.title = 'Disponible próximamente';
  } else {
    link.href = item.href;
  }
  if (item.key === current) {
    link.classList.add('active');
    link.setAttribute('aria-current', 'page');
  }
  return link;
}

export function renderSidebar(container, { current, user, onLogout }) {
  const aside = el('aside', 'sidebar');

  const brand = el('div', 'sidebar-brand');
  const brandText = el('div');
  brandText.append(
    el('div', 'sidebar-name', 'SIGEM'),
    el('div', 'sidebar-tagline', 'Sistema de gestión empresarial'),
  );
  const logo = el('div', 'sidebar-logo', 'S');
  logo.setAttribute('aria-hidden', 'true');
  brand.append(logo, brandText);

  const nav = el('nav', 'sidebar-nav');
  nav.setAttribute('aria-label', 'Módulos');
  // Solo oculta la opción: el backend valida el permiso (AGENTS.md §4)
  const items = NAV_ITEMS.filter((item) => !item.adminOnly || user.role === ADMIN_ROLE);
  nav.append(...items.map((item) => navLink(item, current)));

  const top = el('div', 'sidebar-top');
  top.append(brand, nav);

  const userBox = el('div', 'sidebar-user');
  const userText = el('div', 'sidebar-user-text');
  userText.append(
    el('div', 'sidebar-user-name', user.name),
    el('div', 'sidebar-user-role', user.role),
  );
  const avatar = el('div', 'avatar', initial(user.name));
  avatar.setAttribute('aria-hidden', 'true');
  userBox.append(avatar, userText);

  const logout = el('a', 'sidebar-item logout');
  logout.href = 'index.html';
  logout.append(icon('logOut'), 'Cerrar sesión');
  if (onLogout) {
    logout.addEventListener('click', (event) => {
      event.preventDefault();
      onLogout();
    });
  }

  const footer = el('div', 'sidebar-footer');
  footer.append(userBox, logout);

  aside.append(top, footer);
  container.replaceChildren(aside);
}

export function renderTopBar(container, { title, subtitle, user }) {
  const header = el('header', 'topbar');

  const heading = el('div');
  heading.append(el('h1', 'topbar-title', title));
  if (subtitle) heading.append(el('p', 'topbar-subtitle', subtitle));

  const bell = el('button', 'btn-icon notification-btn');
  bell.type = 'button';
  bell.setAttribute('aria-label', 'Notificaciones');
  bell.append(icon('bell'), el('span', 'notification-dot'));

  const avatar = el('div', 'avatar avatar-light', initial(user.name));
  avatar.setAttribute('aria-hidden', 'true');

  const actions = el('div', 'topbar-actions');
  actions.append(bell, avatar);

  header.append(heading, actions);
  container.replaceChildren(header);
}
