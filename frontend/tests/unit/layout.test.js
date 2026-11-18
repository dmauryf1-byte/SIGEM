import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NAV_ITEMS, renderSidebar, renderTopBar } from '../../js/shared/layout.js';

const ADMIN = { name: 'Administrador', role: 'Administrador' };
const SELLER = { name: 'Ana Gómez', role: 'Vendedor' };

let container;
beforeEach(() => {
  container = document.createElement('div');
});

const labels = () => [...container.querySelectorAll('nav .sidebar-item')].map((a) => a.textContent);

describe('renderSidebar', () => {
  it('muestra los ítems en el orden de DESIGN.md, con Usuarios para Administrador', () => {
    renderSidebar(container, { current: 'dashboard', user: ADMIN });
    expect(labels()).toEqual([
      'Inicio',
      'Clientes',
      'Productos',
      'Vendedores',
      'Proveedores',
      'Facturas',
      'Pagos',
      'Reportes',
      'Usuarios',
    ]);
  });

  it('oculta Usuarios si el rol no es Administrador', () => {
    renderSidebar(container, { current: 'dashboard', user: SELLER });
    expect(labels()).not.toContain('Usuarios');
    expect(labels()).toHaveLength(NAV_ITEMS.length - 1);
  });

  it('marca activo solo el ítem actual', () => {
    renderSidebar(container, { current: 'dashboard', user: ADMIN });
    const active = container.querySelectorAll('[aria-current="page"]');
    expect(active).toHaveLength(1);
    expect(active[0].textContent).toBe('Inicio');
    expect(container.querySelectorAll('.sidebar-item.active')).toHaveLength(1);
  });

  it('cada ítem enlaza a su pantalla', () => {
    renderSidebar(container, { current: 'dashboard', user: ADMIN });
    const hrefs = [...container.querySelectorAll('nav .sidebar-item')].map((a) =>
      a.getAttribute('href'),
    );
    expect(hrefs).toEqual(NAV_ITEMS.map((item) => `${item.key}.html`));
  });

  it('pinta el nombre del usuario como texto, sin crear elementos', () => {
    const evil = '<img src=x onerror="alert(1)">';
    renderSidebar(container, { current: 'dashboard', user: { name: evil, role: 'Vendedor' } });
    expect(container.querySelector('img')).toBeNull();
    expect(container.querySelector('.sidebar-user-name').textContent).toBe(evil);
    expect(container.querySelector('.sidebar .avatar').textContent).toBe('<');
  });

  it('incluye Cerrar sesión hacia el login', () => {
    renderSidebar(container, { current: 'dashboard', user: ADMIN });
    const logout = container.querySelector('.sidebar-item.logout');
    expect(logout.textContent).toBe('Cerrar sesión');
    expect(logout.getAttribute('href')).toBe('index.html');
  });

  it('Cerrar sesión llama a onLogout en vez de navegar', () => {
    const onLogout = vi.fn();
    renderSidebar(container, { current: 'dashboard', user: ADMIN, onLogout });
    const click = new MouseEvent('click', { cancelable: true });

    container.querySelector('.sidebar-item.logout').dispatchEvent(click);

    expect(onLogout).toHaveBeenCalledOnce();
    expect(click.defaultPrevented).toBe(true);
  });
});

describe('renderTopBar', () => {
  it('pinta título, subtítulo e inicial del usuario como texto', () => {
    renderTopBar(container, { title: 'Dashboard', subtitle: '<b>x</b>', user: ADMIN });
    expect(container.querySelector('.topbar-title').textContent).toBe('Dashboard');
    expect(container.querySelector('.topbar-subtitle').textContent).toBe('<b>x</b>');
    expect(container.querySelector('b')).toBeNull();
    expect(container.querySelector('.avatar-light').textContent).toBe('A');
  });

  it('omite el subtítulo si no se pasa', () => {
    renderTopBar(container, { title: 'Dashboard', user: ADMIN });
    expect(container.querySelector('.topbar-subtitle')).toBeNull();
  });

  it('pinta los botones de la pantalla antes de la campana', () => {
    renderTopBar(container, {
      title: 'Clientes',
      user: ADMIN,
      actions: [
        { label: 'Nuevo cliente', icon: 'plus', modal: 'modal-cliente' },
        { id: 'btn-pdf', label: 'PDF', variant: 'secondary' },
      ],
    });
    const [nuevo, pdf, bell] = container.querySelectorAll('.topbar-actions button');
    expect(nuevo.className).toBe('btn-primary');
    expect(nuevo.textContent).toBe('Nuevo cliente');
    expect(nuevo.dataset.open).toBe('modal-cliente');
    expect(nuevo.querySelector('svg')).not.toBeNull();
    expect(pdf.className).toBe('btn-secondary');
    expect(pdf.id).toBe('btn-pdf');
    expect(bell.getAttribute('aria-label')).toBe('Notificaciones');
  });
});
