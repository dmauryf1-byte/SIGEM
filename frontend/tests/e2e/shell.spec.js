import { expect, test } from '@playwright/test';

async function login(page, username = 'e2e', password = process.env.E2E_PASSWORD) {
  await page.goto('/');
  await page.getByLabel('Usuario').fill(username);
  await page.getByLabel('Contraseña').fill(password);
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();
}

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

  test('credenciales malas muestran el error del servidor', async ({ page }) => {
    await login(page, 'no-existe', 'una-clave-cualquiera');
    await expect(page.getByRole('alert')).toHaveText('Usuario o contraseña incorrectos');
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByLabel('Contraseña')).toHaveValue('');
  });
});

test.describe('sesión', () => {
  test('sin sesión, el dashboard devuelve al login', async ({ page }) => {
    await page.goto('/dashboard.html');
    await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  });

  test('login real muestra el marco con el usuario de la sesión', async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/dashboard\.html$/);

    const nav = page.getByRole('navigation', { name: 'Módulos' });
    await expect(nav.locator('[aria-current="page"]')).toHaveText('Inicio');
    await expect(nav.locator('.sidebar-item')).toHaveCount(8); // Vendedor: sin "Usuarios"
    await expect(nav.getByText('Usuarios')).toHaveCount(0);
    await expect(page.locator('.sidebar-user-name')).toHaveText('Prueba E2E');
    await expect(page.locator('.sidebar-user-role')).toHaveText('Vendedor');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('las cookies de sesión no son legibles desde JavaScript', async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/dashboard\.html$/);
    expect(await page.evaluate(() => document.cookie)).toBe('');
  });

  test('Cerrar sesión vuelve al login y no deja volver al dashboard', async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/dashboard\.html$/);

    await page.getByRole('link', { name: 'Cerrar sesión' }).click();
    await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();

    await page.goto('/dashboard.html');
    await expect(page.getByRole('heading', { name: 'Iniciar sesión' })).toBeVisible();
  });

  test('estilos calculados coinciden con DESIGN.md', async ({ page }) => {
    await login(page);
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
});
