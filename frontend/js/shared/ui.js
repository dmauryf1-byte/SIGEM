// Piezas de interfaz que usan todas las pantallas: modales, validación de formularios,
// avisos, botones de filtro y pestañas. Nada de innerHTML: solo textContent (AGENTS.md §5.7).

// ─── Modales (ventanas emergentes) ──────────────────────────────────────────
// Guardamos qué botón abrió el modal para devolverle el foco al cerrarlo (accesibilidad)
let lastTrigger = null;

export function openModal(id) {
  const overlay = document.getElementById(id);
  lastTrigger = document.activeElement;
  overlay.hidden = false;
  // Ponemos el cursor en el primer campo para que se pueda escribir de una vez
  overlay.querySelector('input, select, textarea, button')?.focus();
}

export function closeModal(overlay) {
  overlay.hidden = true;
  const form = overlay.querySelector('form');
  if (form) clearForm(form);
  lastTrigger?.focus();
}

// Conecta los botones con data-open="id" (abren) y data-close (cierran)
export function setupModals(root = document) {
  root.addEventListener('click', (event) => {
    const opener = event.target.closest('[data-open]');
    if (opener) openModal(opener.dataset.open);

    const closer = event.target.closest('[data-close]');
    if (closer) closeModal(closer.closest('.modal-overlay'));

    // Clic en el fondo oscuro (fuera de la caja) también cierra
    if (event.target.classList.contains('modal-overlay')) closeModal(event.target);
  });

  // La tecla Escape cierra el modal que esté abierto
  root.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const open = root.querySelector('.modal-overlay:not([hidden])');
    if (open) closeModal(open);
  });
}

// ─── Validación de formularios ──────────────────────────────────────────────
// Escribe (o borra) el mensaje rojo debajo de un campo
function showFieldError(input, message) {
  const error = document.getElementById(`${input.id}-error`);
  if (error) {
    error.textContent = message;
    error.hidden = !message;
  }
  input.classList.toggle('error', Boolean(message));
  input.setAttribute('aria-invalid', String(Boolean(message)));
}

// Revisa un solo campo y devuelve el mensaje de error ('' si está bien)
function fieldError(input) {
  const value = input.value.trim();
  if (input.required && value === '') return input.dataset.error || 'Este campo es obligatorio';
  if (value !== '' && input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return 'El correo no es válido';
  }
  if (value !== '' && input.min !== '' && Number(value) < Number(input.min)) {
    return input.dataset.minError || `El valor mínimo es ${input.min}`;
  }
  return '';
}

// Valida todo el formulario. Devuelve true si no hay errores.
// Ojo: esto solo ayuda al usuario; la validación real la hace el backend.
export function validateForm(form) {
  let firstInvalid = null;
  for (const input of form.querySelectorAll('input, select, textarea')) {
    const message = fieldError(input);
    showFieldError(input, message);
    if (message && !firstInvalid) firstInvalid = input;
  }
  firstInvalid?.focus();
  return !firstInvalid;
}

// Deja el formulario vacío y sin mensajes de error
export function clearForm(form) {
  form.reset();
  for (const input of form.querySelectorAll('input, select, textarea')) showFieldError(input, '');
}

// Al enviar el formulario: valida y, si todo está bien, llama a onValid
export function setupForm(form, onValid) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (validateForm(form)) onValid(form);
  });
}

// ─── Aviso de la página ─────────────────────────────────────────────────────
// Usa el <div id="page-alert"> de cada pantalla. type: success | error | warning | info
export function showAlert(message, type = 'info') {
  const box = document.getElementById('page-alert');
  box.className = `alert alert-${type} page-alert`;
  box.textContent = message;
  box.hidden = false;
}

// Formularios que todavía no tienen API: validan y avisan en qué tarea se conectan
export function setupPendingForm(formId, message) {
  const form = document.getElementById(formId);
  setupForm(form, () => {
    const overlay = form.closest('.modal-overlay');
    if (overlay) closeModal(overlay);
    showAlert(message, 'info');
  });
}

// ─── Botones de filtro (Todos / Activo / Inactivo) ──────────────────────────
// Al hacer clic en uno, ese queda azul y los demás del mismo grupo vuelven a blanco
export function setupChips(root = document) {
  for (const group of root.querySelectorAll('.chips')) {
    group.addEventListener('click', (event) => {
      const chip = event.target.closest('.chip');
      if (!chip) return;
      for (const other of group.querySelectorAll('.chip')) {
        other.classList.toggle('active', other === chip);
        other.setAttribute('aria-pressed', String(other === chip));
      }
    });
  }
}

// ─── Pestañas (pantalla de Reportes) ────────────────────────────────────────
// Cada botón role="tab" muestra el panel que indica su aria-controls y oculta los demás
export function setupTabs(tablist) {
  const tabs = [...tablist.querySelectorAll('[role="tab"]')];
  tablist.addEventListener('click', (event) => {
    const selected = event.target.closest('[role="tab"]');
    if (!selected) return;
    for (const tab of tabs) {
      const isSelected = tab === selected;
      tab.classList.toggle('active', isSelected);
      tab.setAttribute('aria-selected', String(isSelected));
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !isSelected;
    }
  });
}
