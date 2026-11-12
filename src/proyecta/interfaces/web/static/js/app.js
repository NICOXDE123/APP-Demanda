// Proyecta: comportamiento común sin scripts en línea (la CSP solo permite 'self').
document.addEventListener('DOMContentLoaded', () => {
  // Menú colapsable en pantallas chicas (sin el JS de Bootstrap).
  document.querySelectorAll('[data-toggle-target]').forEach((boton) => {
    boton.addEventListener('click', () => {
      const destino = document.querySelector(boton.dataset.toggleTarget);
      const abierto = destino.classList.toggle('show');
      boton.setAttribute('aria-expanded', String(abierto));
    });
  });
  // Mostrar u ocultar bloques según el tipo de registro del alta.
  const tipo = document.getElementById('tipo');
  if (tipo) {
    const sync = () => document.querySelectorAll('[data-solo-tipo]').forEach((el) => {
      el.hidden = !el.dataset.soloTipo.split(' ').includes(tipo.value);
    });
    tipo.addEventListener('change', sync);
    sync();
  }
  // Confirmación de acciones que cambian el estado.
  document.querySelectorAll('form[data-confirmar]').forEach((f) => f.addEventListener('submit', (e) => {
    if (!window.confirm(f.dataset.confirmar)) e.preventDefault();
  }));
  // Gráfico del dashboard: datos en JSON dentro de un <script type="application/json">.
  const datos = document.getElementById('datos-grafico');
  if (datos && window.Chart) {
    const d = JSON.parse(datos.textContent);
    const clp = (v) => '$' + Math.round(v).toLocaleString('es-CL');
    new Chart(document.getElementById('grafico'), {
      data: {
        labels: d.meses,
        datasets: [
          { type: 'bar', label: 'Backlog contractual', data: d.backlog, backgroundColor: '#0b4f4a', stack: 'f' },
          { type: 'bar', label: 'MAB', data: d.mab, backgroundColor: '#5fb3a8', stack: 'f' },
          { type: 'line', label: 'Meta', data: d.meta, borderColor: '#c2410c', backgroundColor: '#c2410c', pointRadius: 2 },
        ],
      },
      options: {
        maintainAspectRatio: false,
        scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: (v) => '$' + (v / 1e6).toLocaleString('es-CL') + ' M' } } },
        plugins: { tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${clp(c.parsed.y)}` } } },
      },
    });
  }
});
