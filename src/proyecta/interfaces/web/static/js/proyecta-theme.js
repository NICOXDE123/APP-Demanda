// Interacciones de presentación: sin escrituras ni endpoints nuevos.
document.addEventListener('DOMContentLoaded', () => {
  const seleccionarEvento = (boton) => {
    document.querySelectorAll('[data-audit-select]').forEach((control) => {
      const activo = control === boton;
      control.setAttribute('aria-expanded', String(activo));
      control.closest('tr').classList.toggle('is-selected', activo);
    });
    document.querySelectorAll('[data-audit-panel]').forEach((panel) => {
      panel.hidden = panel.id !== boton.getAttribute('aria-controls');
    });
  };
  document.querySelectorAll('[data-audit-select]').forEach((boton) => {
    boton.addEventListener('click', () => seleccionarEvento(boton));
    boton.closest('tr').addEventListener('click', (event) => {
      if (!event.target.closest('a, button')) {
        seleccionarEvento(boton); boton.focus({ preventScroll: true });
      }
    });
  });
  const historial = [...document.querySelectorAll('[data-historial-target]')];
  const seleccionarHistorial = (boton) => {
    historial.forEach((control) => {
      const activo = control === boton;
      control.setAttribute('aria-selected', String(activo));
      control.tabIndex = activo ? 0 : -1;
      document.getElementById(control.dataset.historialTarget).hidden = !activo;
    });
  };
  historial.forEach((boton, indice) => {
    boton.addEventListener('click', () => seleccionarHistorial(boton));
    boton.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const destino = event.key === 'Home' ? 0 : event.key === 'End' ? historial.length - 1
        : (indice + (event.key === 'ArrowRight' ? 1 : -1) + historial.length) % historial.length;
      seleccionarHistorial(historial[destino]); historial[destino].focus();
    });
  });
  const lider = document.querySelector('[data-meta-lider]');
  const nombreLider = document.querySelector('[data-meta-nombre]');
  const actualizarLider = () => {
    if (lider && nombreLider) nombreLider.textContent = lider.selectedOptions[0]?.textContent || 'Selecciona un líder';
  };
  lider?.addEventListener('change', actualizarLider);
  actualizarLider();

  const canvas = document.getElementById('grafico-hc');
  if (!canvas || !window.Chart) return;
  let valores = {
    meses: [...document.querySelectorAll('#cuerpo-serie-mensual tr')].map((fila) => fila.cells[0].textContent),
    hc: [...document.querySelectorAll('#cuerpo-serie-mensual tr')].map((fila) => Number(fila.cells[5].textContent)),
  };
  let dotacion;
  const etiquetas = {
    id: 'etiquetasDotacion',
    afterDatasetsDraw(chart) {
      const ctx = chart.ctx;
      ctx.save();
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color').trim();
      ctx.font = '500 12px system-ui'; ctx.textAlign = 'center';
      chart.getDatasetMeta(0).data.forEach((barra, i) => {
        ctx.fillText(Number(chart.data.datasets[0].data[i]).toLocaleString('es-CL'), barra.x, barra.y - 8);
      });
      ctx.restore();
    },
  };
  const pintarDotacion = () => {
    const estilo = getComputedStyle(document.documentElement);
    const color = (nombre) => estilo.getPropertyValue(nombre).trim();
    dotacion?.destroy();
    dotacion = new Chart(canvas, {
      type: 'bar',
      data: { labels: valores.meses, datasets: [{ label: 'HC al cierre', data: valores.hc,
        backgroundColor: valores.hc.map((_, i) => color(i === valores.hc.length - 1 ? '--dato-primario' : '--dato-pastel')),
        borderColor: color('--dato-primario'), borderWidth: 1, borderRadius: 6, maxBarThickness: 70 }] },
      plugins: [etiquetas],
      options: { maintainAspectRatio: false, animation: false, layout: { padding: { top: 24 } },
        scales: { x: { grid: { display: false }, border: { display: false }, ticks: { color: color('--bs-secondary-color') } },
          y: { beginAtZero: true, display: false, grace: '15%' } },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.parsed.y.toLocaleString('es-CL')} HC al cierre` } } } },
    });
    canvas.setAttribute('aria-label', 'Headcount al cierre: ' + valores.meses.map((mes, i) => `${mes}: ${valores.hc[i]} HC`).join('; ') + '. Detalle en la tabla mensual.');
  };
  pintarDotacion();
  document.addEventListener('proyecta:tema', pintarDotacion);
  document.addEventListener('proyecta:serie', (event) => { valores = event.detail; pintarDotacion(); });
});
