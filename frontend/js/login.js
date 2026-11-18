// Pantalla de inicio de sesión (index.html).
import { apiFetch, errorMessage } from './shared/api.js';

// ─── Mensajes de los campos obligatorios ────────────────────────────────────
const REQUIRED = {
  username: 'El usuario es obligatorio',
  password: 'La contraseña es obligatoria',
};

// ─── Elementos de la página ─────────────────────────────────────────────────
const form = document.getElementById('login-form');
const alertBox = document.getElementById('login-alert');
const submitButton = form.querySelector('button[type="submit"]');

// Muestra (o borra) el error rojo debajo de un campo
function showError(input, message) {
  const error = document.getElementById(`${input.id}-error`);
  error.textContent = message;
  error.hidden = !message;
  input.classList.toggle('error', Boolean(message));
  input.setAttribute('aria-invalid', String(Boolean(message)));
}

// Muestra el aviso rojo de arriba (ej. "Usuario o contraseña incorrectos")
function showAlert(message) {
  alertBox.textContent = message;
  alertBox.hidden = !message;
}

// ─── Validar antes de enviar ────────────────────────────────────────────────
// Revisa que usuario y contraseña no estén vacíos; pone el cursor en el primero que falte
function validate() {
  let firstInvalid = null;
  for (const [name, message] of Object.entries(REQUIRED)) {
    const input = form.elements[name];
    const empty = input.value.trim() === '';
    showError(input, empty ? message : '');
    if (empty && !firstInvalid) firstInvalid = input;
  }
  firstInvalid?.focus();
  return !firstInvalid;
}

// ─── Enviar el login ────────────────────────────────────────────────────────
// Si el backend acepta, vamos al dashboard; si no, mostramos su mensaje de error
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showAlert('');
  if (!validate()) return;

  submitButton.disabled = true; // evita doble clic mientras responde el servidor
  try {
    const response = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      json: {
        username: form.elements.username.value.trim(),
        password: form.elements.password.value,
      },
    });
    if (response.ok) {
      window.location.assign('dashboard.html');
      return;
    }
    showAlert(await errorMessage(response));
    form.elements.password.value = '';
    form.elements.password.focus();
  } catch {
    showAlert('No se pudo conectar con el servidor. Intenta de nuevo.');
  } finally {
    submitButton.disabled = false;
  }
});
