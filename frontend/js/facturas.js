// Pantalla de facturas (facturas.html): lista con filtros por estado y fechas.
import { startPage } from './shared/page.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
// "Nueva factura" lleva a la página del formulario (no es un modal)
await startPage({
  current: 'facturas',
  title: 'Facturas',
  subtitle: 'Documentos de venta internos',
  actions: [{ id: 'btn-nueva-factura', label: 'Nueva factura', icon: 'plus' }],
});
document
  .getElementById('btn-nueva-factura')
  ?.addEventListener('click', () => window.location.assign('factura-nueva.html'));
