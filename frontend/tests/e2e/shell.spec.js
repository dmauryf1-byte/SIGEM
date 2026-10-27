import { expect, test } from '@playwright/test';

test.describe('login', () => {
  test('la raíz muestra el login de SIGEM sin usuario demo', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/SIGEM/);
    await expect(page.getByRole('heading', { name: 'SIGEM', level: 1 })).toBeVisible();
    await expect(page.locator('.login-logo')).toHaveText('S');
    await expect(page.getByText(/admin/i)).toHaveCount(0);
    await expect(page.getByText(/1234/)).toHaveCount(0);
    await expect(page.getByText(/olvidaste/i)).toHaveCount(0);
    await expect(page.getByText('No es facturación electrónica DIAN.')).toBeVisible();
    expect((await page.locator('.login-wrap').boundingBox()).width).toBe(420);
  });

  test('enviar vacío muestra los dos errores bajo cada campo', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Iniciar sesión' }).click();
    await expect(page.locator('#username-error')).toHaveText('El usuario es obligatorio');
    await expect(page.locator('#password-error')).toHaveText('La contraseña es obligatoria');
    await expect(page.getByLabel('Usuario')).toHaveAttribute('aria-invalid', 'true');
    await expect(page.getByLabel('Usuario')).toBeFocused();
  });

  test('llenar un campo quita solo su error', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Usuario').fill('ana');
    await page.getByRole('button', { name: 'Iniciar sesión' }).click();
    await expect(page.locator('#username-error')).toBeHidden();
    await expect(page.locator('#password-error')).toBeVisible();
  });
});

test.describe('marco de la aplicación', () => {
  test('dashboard muestra sidebar y barra superior con Inicio activo', async ({ page }) => {
    await page.goto('/dashboard.html');
    const nav = page.getByRole('navigation', { name: 'Módulos' });
    await expect(nav.locator('.sidebar-item')).toHaveCount(9);
    await expect(nav.locator('[aria-current="page"]')).toHaveText('Inicio');
    await expect(page.locator('.sidebar-name')).toHaveText('SIGEM');
    await expect(page.getByRole('link', { name: 'Cerrar sesión' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('estilos calculados coinciden con DESIGN.md', async ({ page }) => {
    await page.goto('/dashboard.html');
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toHaveCSS('background-color', 'rgb(30, 41, 59)');
    await expect(sidebar).toHaveCSS('width', '232px');
    await expect(page.locator('.topbar')).toHaveCSS('height', '60px');
    await expect(page.locator('.sidebar-item.active')).toHaveCSS(
      'background-color',
      'rgb(59, 130, 246)',
    );
    await expect(page.locator('.topbar-title')).toHaveCSS('font-family', /DM Sans/);
    await expect(page.locator('.app-content')).toHaveCSS('background-color', 'rgb(241, 245, 249)');
  });

  test('Cerrar sesión vuelve al login', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.getByRole('link', { name: 'Cerrar sesión' }).click();
    await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  });
});
