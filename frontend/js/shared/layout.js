// Menú lateral y barra superior del prototipo (App.tsx: Sidebar y TopBar).
// Todo se crea con createElement y textContent para evitar XSS (AGENTS.md §5.7).
import { icon } from './icons.js';

// ─── Opciones del menú ──────────────────────────────────────────────────────
// key = nombre de la pantalla, label = texto que se ve, href = página que abre
export const NAV_ITEMS = [
  { key: 'dashboard', label: 'Inicio', icon: 'home', href: 'dashboard.html' },
  { key: 'clientes', label: 'Clientes', icon: 'users', href: 'clientes.html' },
  { key: 'productos', label: 'Productos', icon: 'box', href: 'productos.html' },
  { key: 'vendedores', label: 'Vendedores', icon: 'userCheck', href: 'vendedores.html' },
  { key: 'proveedores', label: 'Proveedores', icon: 'truck', href: 'proveedores.html' },
  { key: 'facturas', label: 'Facturas', icon: 'fileText', href: 'facturas.html' },
  { key: 'pagos', label: 'Pagos', icon: 'creditCard', href: 'pagos.html' },
  { key: 'reportes', label: 'Reportes', icon: 'barChart', href: 'reportes.html' },
  { key: 'usuarios', label: 'Usuarios', icon: 'shield', href: 'usuarios.html', adminOnly: true },
];

const ADMIN_ROLE = 'Administrador';

// ─── Ayudantes ──────────────────────────────────────────────────────────────
// Crea una etiqueta con clase y texto en una sola línea
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// Primera letra del nombre, para el círculo del avatar
const initial = (name) => name.trim().charAt(0).toUpperCase();

// Un enlace del menú; si es la pantalla actual, se pinta azul (activo)
function navLink(item, current) {
  const link = el('a', 'sidebar-item');
  link.href = item.href;
  link.append(icon(item.icon), item.label);
  if (item.key === current) {
    link.classList.add('active');
    link.setAttribute('aria-current', 'page');
  }
  return link;
}

// ─── Menú lateral ───────────────────────────────────────────────────────────
export function renderSidebar(container, { current, user, onLogout }) {
  const aside = el('aside', 'sidebar');

  // Logo "S" con el nombre SIGEM
  const brand = el('div', 'sidebar-brand');
  const brandText = el('div');
  brandText.append(
    el('div', 'sidebar-name', 'SIGEM'),
    el('div', 'sidebar-tagline', 'Sistema de gestión empresarial'),
  );
  const logo = el('div', 'sidebar-logo', 'S');
  logo.setAttribute('aria-hidden', 'true');
  brand.append(logo, brandText);

  // Lista de módulos. "Usuarios" solo lo ve el Administrador.
  // Esto solo oculta la opción: el permiso real lo valida el backend (AGENTS.md §4)
  const nav = el('nav', 'sidebar-nav');
  nav.setAttribute('aria-label', 'Módulos');
  const items = NAV_ITEMS.filter((item) => !item.adminOnly || user.role === ADMIN_ROLE);
  nav.append(...items.map((item) => navLink(item, current)));

  const top = el('div', 'sidebar-top');
  top.append(brand, nav);

  // Parte de abajo: usuario conectado y botón de cerrar sesión
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

// ─── Botón de la barra superior ─────────────────────────────────────────────
// action = { label, icon, id, variant: 'primary' | 'secondary', modal: 'id-del-modal' }
function actionButton(action) {
  const button = el('button', action.variant === 'secondary' ? 'btn-secondary' : 'btn-primary');
  button.type = 'button';
  if (action.id) button.id = action.id;
  // data-open hace que ui.js abra ese modal al hacer clic
  if (action.modal) button.dataset.open = action.modal;
  if (action.icon) button.append(icon(action.icon, 16));
  button.append(action.label);
  return button;
}

// ─── Barra superior ─────────────────────────────────────────────────────────
export function renderTopBar(container, { title, subtitle, user, actions = [] }) {
  const header = el('header', 'topbar');

  // Título y subtítulo de la pantalla
  const heading = el('div');
  heading.append(el('h1', 'topbar-title', title));
  if (subtitle) heading.append(el('p', 'topbar-subtitle', subtitle));

  // Campana de notificaciones con el punto rojo
  const bell = el('button', 'btn-icon notification-btn');
  bell.type = 'button';
  bell.setAttribute('aria-label', 'Notificaciones');
  bell.append(icon('bell'), el('span', 'notification-dot'));

  const avatar = el('div', 'avatar avatar-light', initial(user.name));
  avatar.setAttribute('aria-hidden', 'true');

  // Botones propios de la pantalla (ej. "+ Nuevo cliente") + campana + avatar
  const actionsBox = el('div', 'topbar-actions');
  actionsBox.append(...actions.map(actionButton), bell, avatar);

  header.append(heading, actionsBox);
  container.replaceChildren(header);
}
