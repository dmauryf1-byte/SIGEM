// Pantalla de proveedores (proveedores.html): lista y formulario de nuevo proveedor.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
await startPage({
  current: 'proveedores',
  title: 'Proveedores',
  subtitle: 'Proveedores registrados',
  actions: [{ label: 'Nuevo proveedor', icon: 'plus', modal: 'modal-proveedor' }],
});

// ─── Formulario ─────────────────────────────────────────────────────────────
setupPendingForm(
  'form-proveedor',
  'Datos válidos. Guardar proveedores queda disponible cuando se conecte su API (SIGEM-008).',
);
