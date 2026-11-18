// Pantalla de reportes (reportes.html): filtros por fecha, pestañas y exportación.
import { startPage } from './shared/page.js';
import { setupTabs, showAlert } from './shared/ui.js';

// ─── Iniciar la pantalla ────────────────────────────────────────────────────
await startPage({
  current: 'reportes',
  title: 'Reportes',
  subtitle: 'Análisis y estadísticas del negocio',
  actions: [
    { id: 'btn-pdf', label: 'PDF', icon: 'download', variant: 'secondary' },
    { id: 'btn-excel', label: 'Excel', icon: 'download', variant: 'secondary' },
  ],
});

// ─── Pestañas ───────────────────────────────────────────────────────────────
setupTabs(document.getElementById('tabs-reportes'));

// ─── Botones de exportar y consultar ────────────────────────────────────────
const pending = 'Los reportes en PDF y Excel quedan disponibles en SIGEM-012.';
for (const id of ['btn-pdf', 'btn-excel']) {
  document.getElementById(id)?.addEventListener('click', () => showAlert(pending, 'info'));
}
document.getElementById('form-periodo').addEventListener('submit', (event) => {
  event.preventDefault();
  showAlert('Aún no hay facturas en el período seleccionado.', 'info');
});
