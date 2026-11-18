// Pantalla de pagos (pagos.html): resumen de recaudo, lista y formulario de pago.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
await startPage({
  current: 'pagos',
  title: 'Pagos',
  subtitle: 'Pagos registrados',
  actions: [{ label: 'Registrar pago', icon: 'plus', modal: 'modal-pago' }],
});

// ─── Formulario ─────────────────────────────────────────────────────────────
// El backend revisa que el pago no supere el saldo pendiente (AGENTS.md §3.4)
setupPendingForm(
  'form-pago',
  'Datos válidos. Registrar pagos queda disponible cuando se conecte su API (SIGEM-010).',
);
