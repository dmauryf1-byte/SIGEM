// Pantalla de clientes (clientes.html): lista, búsqueda y formulario de nuevo cliente.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
// El botón "Nuevo cliente" abre el modal con id "modal-cliente"
await startPage({
  current: 'clientes',
  title: 'Clientes',
  subtitle: 'Clientes registrados',
  actions: [{ label: 'Nuevo cliente', icon: 'plus', modal: 'modal-cliente' }],
});

// ─── Formulario ─────────────────────────────────────────────────────────────
// Valida los campos; guardar en la base de datos llega con la API de clientes
setupPendingForm(
  'form-cliente',
  'Datos válidos. Guardar clientes queda disponible cuando se conecte su API (SIGEM-005).',
);
