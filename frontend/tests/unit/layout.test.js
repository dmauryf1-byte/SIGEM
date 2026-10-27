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

  it('deshabilita los ítems sin pantalla: sin href y con aria-disabled', () => {
    renderSidebar(container, { current: 'dashboard', user: ADMIN });
    const clientes = [...container.querySelectorAll('nav .sidebar-item')].find(
      (a) => a.textContent === 'Clientes',
    );
    expect(clientes.getAttribute('aria-disabled')).toBe('true');
    expect(clientes.hasAttribute('href')).toBe(false);
    const inicio = container.querySelector('[aria-current="page"]');
    expect(inicio.getAttribute('href')).toBe('dashboard.html');
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
});
