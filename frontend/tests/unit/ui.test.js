import { beforeEach, describe, expect, it } from 'vitest';
import {
  setupChips,
  setupModals,
  setupPendingForm,
  setupTabs,
  validateForm,
} from '../../js/shared/ui.js';

// Arma el DOM con createElement (las reglas del proyecto no permiten innerHTML)
function input(id, attrs = {}) {
  const node = document.createElement('input');
  node.id = id;
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'required') node.required = value;
    else node.setAttribute(key, value);
  }
  const error = document.createElement('div');
  error.id = `${id}-error`;
  error.hidden = true;
  return [node, error];
}

let form;
beforeEach(() => {
  document.body.replaceChildren();
  form = document.createElement('form');
  document.body.append(form);
});

describe('validateForm', () => {
  it('marca los obligatorios vacíos con su mensaje y enfoca el primero', () => {
    const [nombre, nombreError] = input('nombre', { required: true, 'data-error': 'Falta' });
    const [ciudad] = input('ciudad');
    form.append(nombre, nombreError, ciudad);

    expect(validateForm(form)).toBe(false);
    expect(nombreError.textContent).toBe('Falta');
    expect(nombreError.hidden).toBe(false);
    expect(nombre.getAttribute('aria-invalid')).toBe('true');
    expect(document.activeElement).toBe(nombre);
    expect(ciudad.getAttribute('aria-invalid')).toBe('false');
  });

  it('rechaza correos mal escritos y números bajo el mínimo', () => {
    const [email, emailError] = input('email', { type: 'email' });
    const [stock, stockError] = input('stock', {
      type: 'number',
      min: '0',
      'data-min-error': 'El stock no puede ser negativo',
    });
    email.value = 'no-es-correo';
    stock.value = '-1';
    form.append(email, emailError, stock, stockError);

    expect(validateForm(form)).toBe(false);
    expect(emailError.textContent).toBe('El correo no es válido');
    expect(stockError.textContent).toBe('El stock no puede ser negativo');
  });

  it('acepta el formulario correcto y borra errores anteriores', () => {
    const [nombre, nombreError] = input('nombre', { required: true });
    form.append(nombre, nombreError);
    validateForm(form);

    nombre.value = 'Ferretería';
    expect(validateForm(form)).toBe(true);
    expect(nombreError.hidden).toBe(true);
    expect(nombre.classList.contains('error')).toBe(false);
  });
});

describe('modales y formularios pendientes', () => {
  function buildModal() {
    const opener = document.createElement('button');
    opener.dataset.open = 'modal-x';
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'modal-x';
    overlay.hidden = true;
    const [nombre, nombreError] = input('nombre', { required: true });
    form.id = 'form-x';
    form.append(nombre, nombreError);
    overlay.append(form);
    const alertBox = document.createElement('div');
    alertBox.id = 'page-alert';
    alertBox.hidden = true;
    document.body.append(opener, overlay, alertBox);
    return { opener, overlay, nombre, alertBox };
  }

  it('data-open abre el modal y Escape lo cierra', () => {
    const { opener, overlay, nombre } = buildModal();
    setupModals(document.body);

    opener.click();
    expect(overlay.hidden).toBe(false);
    expect(document.activeElement).toBe(nombre);

    document.body.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(overlay.hidden).toBe(true);
  });

  it('con datos válidos cierra el modal y muestra el aviso', () => {
    const { overlay, nombre, alertBox } = buildModal();
    overlay.hidden = false;
    setupPendingForm('form-x', 'Se conecta en SIGEM-005');

    nombre.value = 'Ana';
    form.dispatchEvent(new Event('submit', { cancelable: true }));

    expect(overlay.hidden).toBe(true);
    expect(alertBox.hidden).toBe(false);
    expect(alertBox.textContent).toBe('Se conecta en SIGEM-005');
    expect(nombre.value).toBe('');
  });

  it('con datos inválidos no cierra el modal', () => {
    const { overlay, alertBox } = buildModal();
    overlay.hidden = false;
    setupPendingForm('form-x', 'x');

    form.dispatchEvent(new Event('submit', { cancelable: true }));

    expect(overlay.hidden).toBe(false);
    expect(alertBox.hidden).toBe(true);
  });
});

describe('chips y pestañas', () => {
  it('solo un chip del grupo queda activo', () => {
    const group = document.createElement('div');
    group.className = 'chips';
    const chips = ['Todos', 'Activo'].map((label, i) => {
      const chip = document.createElement('button');
      chip.className = i === 0 ? 'chip active' : 'chip';
      chip.textContent = label;
      return chip;
    });
    group.append(...chips);
    document.body.append(group);
    setupChips(document.body);

    chips[1].click();

    expect(chips[0].classList.contains('active')).toBe(false);
    expect(chips[1].classList.contains('active')).toBe(true);
    expect(chips[1].getAttribute('aria-pressed')).toBe('true');
  });

  it('la pestaña elegida muestra su panel y oculta los demás', () => {
    const tablist = document.createElement('div');
    const panels = ['a', 'b'].map((id) => {
      const tab = document.createElement('button');
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', id);
      tablist.append(tab);
      const panel = document.createElement('div');
      panel.id = id;
      document.body.append(panel);
      return panel;
    });
    document.body.append(tablist);
    setupTabs(tablist);

    tablist.querySelectorAll('[role="tab"]')[1].click();

    expect(panels[0].hidden).toBe(true);
    expect(panels[1].hidden).toBe(false);
  });
});
