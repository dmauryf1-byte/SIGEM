// Pantalla de usuarios (usuarios.html): solo para el Administrador.
import { startPage } from './shared/page.js';
import { setupPendingForm } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
const user = await startPage({
  current: 'usuarios',
  title: 'Usuarios',
  subtitle: 'Gestión de accesos al sistema',
  actions: [{ label: 'Nuevo usuario', icon: 'plus', modal: 'modal-usuario' }],
});

// ─── Permiso ────────────────────────────────────────────────────────────────
// Un Vendedor no debe ver esta pantalla: lo devolvemos al inicio.
// (Es solo para la vista: el backend también bloquea estas operaciones, AGENTS.md §4)
if (user && user.role !== 'Administrador') window.location.assign('dashboard.html');

// ─── Formulario ─────────────────────────────────────────────────────────────
setupPendingForm(
  'form-usuario',
  'Datos válidos. Hoy los usuarios se crean por consola; la pantalla se conecta en SIGEM-017.',
);
