// Pantalla de vendedores (vendedores.html): lista y formulario de nuevo vendedor.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
await startPage({
  current: 'vendedores',
  title: 'Vendedores',
  subtitle: 'Vendedores registrados',
  actions: [{ label: 'Nuevo vendedor', icon: 'plus', modal: 'modal-vendedor' }],
});

// ─── Formulario ─────────────────────────────────────────────────────────────
setupPendingForm(
  'form-vendedor',
  'Datos válidos. Guardar vendedores queda disponible cuando se conecte su API (SIGEM-007).',
);
