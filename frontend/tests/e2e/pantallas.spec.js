import { expect, test } from '@playwright/test';

// Pantallas que ve un Vendedor: [archivo, ítem activo del menú, título de la barra superior]
const SCREENS = [
  ['clientes', 'Clientes', 'Clientes'],
  ['productos', 'Productos', 'Productos'],
  ['vendedores', 'Vendedores', 'Vendedores'],
  ['proveedores', 'Proveedores', 'Proveedores'],
  ['facturas', 'Facturas', 'Facturas'],
  ['factura-nueva', 'Facturas', 'Nueva factura'],
  ['pagos', 'Pagos', 'Pagos'],
  ['reportes', 'Reportes', 'Reportes'],
];

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Usuario').fill('e2e');
  await page.getByLabel('Contraseña').fill(process.env.E2E_PASSWORD);
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();
  await expect(page).toHaveURL(/dashboard\.html$/);
});

for (const [file, navLabel, title] of SCREENS) {
  test(`${file}: abre con el marco y el menú en ${navLabel}`, async ({ page }) => {
    await page.goto(`/${file}.html`);
    await expect(page.getByRole('heading', { name: title, level: 1 })).toBeVisible();
    const nav = page.getByRole('navigation', { name: 'Módulos' });
    await expect(nav.locator('[aria-current="page"]')).toHaveText(navLabel);
  });
}

test('el menú navega entre pantallas', async ({ page }) => {
  await page.getByRole('navigation', { name: 'Módulos' }).getByText('Clientes').click();
  await expect(page).toHaveURL(/clientes\.html$/);
});

test('Nuevo cliente: valida obligatorios y avisa que falta la API', async ({ page }) => {
  await page.goto('/clientes.html');
  await page.getByRole('button', { name: 'Nuevo cliente' }).click();
  const modal = page.getByRole('dialog', { name: 'Nuevo cliente' });
  await expect(modal).toBeVisible();

  await modal.getByRole('button', { name: 'Guardar cliente' }).click();
  await expect(modal.getByText('El nombre es obligatorio')).toBeVisible();

  await modal.getByLabel('Nombre', { exact: false }).first().fill('Ferretería El Clavo');
  await modal.getByLabel('Tipo de documento').selectOption('NIT');
  await modal.getByLabel('Número de documento').fill('900123456');
  await modal.getByLabel('Teléfono').fill('3101234567');
  await modal.getByLabel('Dirección').fill('Calle 10 # 20-30');
  await modal.getByRole('button', { name: 'Guardar cliente' }).click();

  await expect(modal).toBeHidden();
  await expect(page.getByRole('status')).toContainText('SIGEM-005');
});

test('Productos: el stock negativo se rechaza en el formulario', async ({ page }) => {
  await page.goto('/productos.html');
  await page.getByRole('button', { name: 'Nuevo producto' }).click();
  await page.getByLabel('Stock inicial').fill('-3');
  await page.getByRole('button', { name: 'Guardar producto' }).click();
  await expect(page.getByText('El stock no puede ser negativo')).toBeVisible();
});

test('Reportes: las pestañas cambian el panel visible', async ({ page }) => {
  await page.goto('/reportes.html');
  await page.getByRole('tab', { name: 'Inventario' }).click();
  await expect(page.getByRole('heading', { name: 'Inventario de productos' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Tabla de ventas por cliente' })).toBeHidden();
});

test('Facturas avisa que no es factura electrónica DIAN', async ({ page }) => {
  await page.goto('/facturas.html');
  await expect(page.getByRole('note')).toHaveText(/no es factura electrónica DIAN/);
});

test('un Vendedor que abre usuarios.html vuelve al inicio', async ({ page }) => {
  await page.goto('/usuarios.html');
  await expect(page).toHaveURL(/dashboard\.html$/);
});
