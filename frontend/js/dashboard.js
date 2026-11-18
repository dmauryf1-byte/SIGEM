// Pantalla de inicio (dashboard.html): resumen del negocio.
import { startPage } from './shared/page.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
// El botón "Nueva factura" lleva al formulario de factura
await startPage({
  current: 'dashboard',
  title: 'Dashboard',
  subtitle: 'Resumen general del negocio',
  actions: [{ id: 'btn-nueva-factura', label: 'Nueva factura', icon: 'plus' }],
});
document
  .getElementById('btn-nueva-factura')
  ?.addEventListener('click', () => window.location.assign('factura-nueva.html'));

// Las cifras y gráficas se llenan con datos reales en SIGEM-011 (por ahora se ven en cero)
