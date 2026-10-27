import { apiFetch, errorMessage } from './shared/api.js';

const REQUIRED = {
  username: 'El usuario es obligatorio',
  password: 'La contraseña es obligatoria',
};

const form = document.getElementById('login-form');
const alertBox = document.getElementById('login-alert');
const submitButton = form.querySelector('button[type="submit"]');

function showError(input, message) {
  const error = document.getElementById(`${input.id}-error`);
  error.textContent = message;
  error.hidden = !message;
  input.classList.toggle('error', Boolean(message));
  input.setAttribute('aria-invalid', String(Boolean(message)));
}

function showAlert(message) {
  alertBox.textContent = message;
  alertBox.hidden = !message;
}

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

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showAlert('');
  if (!validate()) return;

  submitButton.disabled = true;
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
