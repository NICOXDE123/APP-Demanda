// Proyecta: comportamiento común sin scripts en línea (la CSP solo permite 'self').
document.addEventListener('DOMContentLoaded', () => {
  const preview = document.getElementById('vista-previa');
  const estadoPreview = document.getElementById('estado-previa');
  let esperaPreview;
  const mensajePreview = (texto, pendiente = true) => {
    if (estadoPreview) estadoPreview.textContent = texto;
    preview?.classList.toggle('preview-desactualizada', pendiente);
    preview?.setAttribute('aria-busy', String(pendiente));
  };
  const actualizarPreview = () => {
    if (preview?.closest('dialog')?.open) preview.dispatchEvent(new Event('actualizar-previa'));
  };
  document.getElementById('alta')?.addEventListener('input', () => {
    mensajePreview('Cálculo anterior; actualización pendiente.');
    clearTimeout(esperaPreview);
    esperaPreview = setTimeout(actualizarPreview, 400);
  });
  document.getElementById('alta')?.addEventListener('change', () => {
    mensajePreview('Cálculo anterior; actualización pendiente.');
    clearTimeout(esperaPreview);
    esperaPreview = setTimeout(actualizarPreview, 400);
  });
  document.querySelector('[data-reintentar-previa]')?.addEventListener('click', actualizarPreview);
  preview?.addEventListener('htmx:beforeRequest', () => mensajePreview('Actualizando vista previa…'));
  preview?.addEventListener('htmx:afterSwap', () => mensajePreview('Vista previa actualizada; no se ha guardado nada.', false));
  const falloPreview = () => {
    mensajePreview('No se pudo actualizar. El cálculo mostrado es anterior; comprueba tu conexión y reintenta.');
    preview?.setAttribute('aria-busy', 'false');
  };
  preview?.addEventListener('htmx:sendError', falloPreview);
  preview?.addEventListener('htmx:responseError', falloPreview);
  // Menú colapsable en pantallas chicas (sin el JS de Bootstrap).
  document.querySelectorAll('[data-toggle-target]').forEach((boton) => {
    boton.addEventListener('click', () => {
      const destino = document.querySelector(boton.dataset.toggleTarget);
      const abierto = destino.classList.toggle('show');
      boton.setAttribute('aria-expanded', String(abierto));
    });
  });
  document.querySelectorAll('[data-dialog-open]').forEach((boton) => {
    boton.addEventListener('click', () => {
      const dialog = document.getElementById(boton.getAttribute('aria-controls'));
      if (dialog && !dialog.open) { dialog.showModal(); actualizarPreview(); }
    });
  });
  document.querySelectorAll('dialog[data-dialog-open-on-load]').forEach((dialog) => {
    dialog.showModal();
    dialog.querySelector('[data-error-summary]')?.focus();
    actualizarPreview();
  });
  document.querySelectorAll('[data-dialog-close]').forEach((boton) => {
    boton.addEventListener('click', () => boton.closest('dialog')?.close());
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
  document.querySelectorAll('[data-error-summary]').forEach((resumen) => {
    if (!resumen.closest('dialog')) resumen.focus();
    resumen.querySelectorAll('a[href^="#"]').forEach((enlace) => enlace.addEventListener('click', (event) => {
      const campo = document.getElementById(enlace.hash.slice(1));
      if (!campo) return;
      event.preventDefault();
      for (let padre = campo.parentElement; padre; padre = padre.parentElement) {
        if (padre.tagName === 'DETAILS') padre.open = true;
      }
      campo.focus();
      campo.scrollIntoView({ block: 'center' });
    }));
  });
  document.querySelector('[data-revisar-conflicto]')?.addEventListener('change', (event) => {
    const control = event.target;
    const formulario = [...document.forms].find((form) => form.getAttribute('action') === control.dataset.accion);
    const version = formulario?.querySelector('[name="version"]');
    if (!version) return;
    if (!version.dataset.anterior) version.dataset.anterior = version.value;
    version.value = control.checked ? control.dataset.version : version.dataset.anterior;
  });
  document.querySelectorAll('form[method="post"]:not([data-sin-bloqueo])').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (event.defaultPrevented) return;
      if (form.dataset.enviando) { event.preventDefault(); return; }
      form.dataset.enviando = '1';
      form.setAttribute('aria-busy', 'true');
      const estado = document.createElement('span');
      estado.className = 'small ms-2'; estado.setAttribute('role', 'status'); estado.textContent = 'Guardando…';
      form.append(estado);
      form.querySelectorAll('button:not([type="button"])').forEach((boton) => { boton.disabled = true; });
    });
  });
  window.addEventListener('pageshow', () => {
    document.querySelectorAll('form[data-enviando]').forEach((form) => {
      delete form.dataset.enviando; form.removeAttribute('aria-busy');
      form.querySelectorAll('button').forEach((boton) => { boton.disabled = false; });
    });
  });
  // Gráfico del dashboard: datos en JSON dentro de un <script type="application/json">.
  const datos = document.getElementById('datos-grafico');
  if (datos && window.Chart) {
    const d = JSON.parse(datos.textContent);
    const clp = (v) => '$' + Math.round(v).toLocaleString('es-CL');
    const colores = getComputedStyle(document.documentElement);
    const configuracion = {
      data: {
        labels: d.meses,
        datasets: [
          { type: 'bar', label: 'Backlog contractual', data: d.backlog, backgroundColor: colores.getPropertyValue('--grafico-backlog').trim(), stack: 'f' },
          { type: 'bar', label: 'MAB (trama)', data: d.mab, backgroundColor: colores.getPropertyValue('--grafico-mab').trim(), stack: 'f' },
          { type: 'line', label: 'Meta (línea discontinua)', data: d.meta, borderColor: colores.getPropertyValue('--grafico-meta').trim(), pointRadius: 3, borderDash: [7, 4] },
        ],
      },
      options: {
        maintainAspectRatio: false,
        animation: false,
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, title: { display: true, text: 'Millones de CLP' }, ticks: { callback: (v) => (v / 1e6).toLocaleString('es-CL') } } },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${clp(c.parsed.y)}` } } },
      },
    };
    let grafico;
    const aplicarTemaGrafico = () => {
      // Recrear evita conservar opciones compartidas del tema anterior en las barras.
      const visibles = grafico?.data.datasets.map((_, i) => grafico.isDatasetVisible(i));
      grafico?.destroy();
      const estilo = getComputedStyle(document.documentElement);
      const color = (nombre) => estilo.getPropertyValue(nombre).trim();
      const texto = color('--bs-body-color'), fondo = color('--bs-body-bg');
      configuracion.data.datasets[0].backgroundColor = color('--grafico-backlog');
      const trama = document.createElement('canvas'); trama.width = trama.height = 8;
      const ctx = trama.getContext('2d');
      ctx.fillStyle = color('--grafico-mab'); ctx.fillRect(0, 0, 8, 8);
      ctx.strokeStyle = texto; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(0, 8); ctx.lineTo(8, 0); ctx.stroke();
      configuracion.data.datasets[1].backgroundColor = document.getElementById('grafico').getContext('2d').createPattern(trama, 'repeat');
      configuracion.data.datasets[1].borderColor = texto; configuracion.data.datasets[1].borderWidth = 1;
      configuracion.data.datasets[2].borderColor = color('--grafico-meta');
      configuracion.data.datasets[2].backgroundColor = color('--grafico-meta');
      for (const eje of Object.values(configuracion.options.scales)) {
        eje.ticks ??= {}; eje.grid ??= {};
        eje.ticks.color = texto; eje.grid.color = color('--grafico-grilla');
        if (eje.title) eje.title.color = texto;
      }
      Object.assign(configuracion.options.plugins.tooltip, { backgroundColor: fondo, titleColor: texto, bodyColor: texto, borderColor: texto, borderWidth: 1 });
      grafico = new Chart(document.getElementById('grafico'), configuracion);
      visibles?.forEach((visible, i) => grafico.setDatasetVisibility(i, visible));
      grafico.update('none');
    };
    aplicarTemaGrafico();
    document.addEventListener('proyecta:tema', aplicarTemaGrafico);
    document.querySelectorAll('[data-serie]').forEach((control) => control.addEventListener('change', () => {
      grafico.setDatasetVisibility(Number(control.dataset.serie), control.checked);
      grafico.update();
      document.getElementById('estado-grafico').textContent = `${control.parentElement.textContent.trim()}: ${control.checked ? 'visible' : 'oculta'}. La tabla mantiene todos los valores.`;
    }));
  }
});
