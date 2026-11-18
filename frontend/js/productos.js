// Pantalla de productos (productos.html): inventario, IVA por producto y formulario.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
await startPage({
  current: 'productos',
  title: 'Productos',
  subtitle: 'Productos e inventario',
  actions: [{ label: 'Nuevo producto', icon: 'plus', modal: 'modal-producto' }],
});

// ─── Formulario ─────────────────────────────────────────────────────────────
// El stock no puede ser negativo (min="0"); el backend también lo valida (AGENTS.md §3.3)
setupPendingForm(
  'form-producto',
  'Datos válidos. Guardar productos queda disponible cuando se conecte su API (SIGEM-006).',
);
