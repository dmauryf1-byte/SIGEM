// shortcut: solo valida campos vacíos; el inicio de sesión real llega en SIGEM-004
const REQUIRED = {
  username: 'El usuario es obligatorio',
  password: 'La contraseña es obligatoria',
};

function showError(input, message) {
  const error = document.getElementById(`${input.id}-error`);
  error.textContent = message;
  error.hidden = !message;
  input.classList.toggle('error', Boolean(message));
  input.setAttribute('aria-invalid', String(Boolean(message)));
}

const form = document.getElementById('login-form');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  let firstInvalid = null;
  for (const [name, message] of Object.entries(REQUIRED)) {
    const input = form.elements[name];
    const empty = input.value.trim() === '';
    showError(input, empty ? message : '');
    if (empty && !firstInvalid) firstInvalid = input;
  }
  firstInvalid?.focus();
});
