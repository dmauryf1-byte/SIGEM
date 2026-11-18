// Pantalla para crear una factura (factura-nueva.html).
import { startPage } from './shared/page.js';
import { setupPendingForm, showAlert } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
// En el menú queda marcada "Facturas" porque esta pantalla es parte de ese módulo
await startPage({
  current: 'facturas',
  title: 'Nueva factura',
  subtitle: 'Crear documento de venta',
});

// ─── Fecha de hoy por defecto ───────────────────────────────────────────────
const fecha = document.getElementById('fecha_factura');
fecha.value = new Date().toLocaleDateString('en-CA'); // en-CA da el formato AAAA-MM-DD

// ─── Agregar producto ───────────────────────────────────────────────────────
// Todavía no hay productos en la base de datos: avisamos en vez de agregar una fila
document.getElementById('btn-agregar-producto').addEventListener('click', () => {
  showAlert('Primero registra productos. Agregarlos a la factura llega en SIGEM-009.', 'warning');
});

// ─── Guardar ────────────────────────────────────────────────────────────────
// Los totales y el descuento de stock los calcula el backend en una sola transacción
// (AGENTS.md §3.1 y §3.5): el navegador nunca calcula dinero.
setupPendingForm(
  'form-factura',
  'Datos válidos. Guardar facturas queda disponible cuando se conecte su API (SIGEM-009).',
);
