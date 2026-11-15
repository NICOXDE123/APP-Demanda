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
      if (boton.dataset.toggleTarget === '#filtros-collapse') {
        sessionStorage.setItem('filtros_abiertos', String(abierto));
      }
    });
  });
  const panelFiltros = document.getElementById('filtros-collapse');
  const btnFiltros = document.querySelector('[data-toggle-target="#filtros-collapse"]');
  if (panelFiltros && btnFiltros && sessionStorage.getItem('filtros_abiertos') === 'true') {
    panelFiltros.classList.add('show');
    btnFiltros.setAttribute('aria-expanded', 'true');
  }

  // Manejador de subpestañas del dashboard
  document.querySelectorAll('[data-tab-target]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetSelector = btn.dataset.tabTarget;
      document.querySelectorAll('[data-tab-target]').forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      document.querySelectorAll('#tablero-pestanas-contenido > .tab-pane').forEach((pane) => {
        pane.classList.remove('active');
        pane.classList.add('d-none');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const targetPane = document.querySelector(targetSelector);
      if (targetPane) {
        targetPane.classList.remove('d-none');
        targetPane.classList.add('active');
      }
      sessionStorage.setItem('dashboard_subpestana', targetSelector);
      window.dispatchEvent(new Event('resize'));
    });
  });
  const subpestanaGuardada = sessionStorage.getItem('dashboard_subpestana');
  if (subpestanaGuardada) {
    const btnSubpestana = document.querySelector(`[data-tab-target="${subpestanaGuardada}"]`);
    if (btnSubpestana && !btnSubpestana.classList.contains('active')) {
      btnSubpestana.click();
    }
  }

  // Auto-submit para formularios de filtros sin tener que pulsar Aplicar cada vez
  document.querySelectorAll('form[data-auto-submit]').forEach((form) => {
    form.querySelectorAll('select, input[type="checkbox"], input[type="month"], input[type="date"]').forEach((input) => {
      input.addEventListener('change', () => {
        form.requestSubmit();
      });
    });
    const searchInput = form.querySelector('input[name="q"]');
    if (searchInput) {
      let timer;
      searchInput.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          form.requestSubmit();
        }, 500);
      });
    }
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

    // Vistas propias del gráfico (3m ant + 3m fut, últimos 3m, 6m, 12m, futuro 3m, 6m) sin recargar ni tocar filtros
    const datosSerieCompleta = document.getElementById('datos-serie-completa');
    if (datosSerieCompleta) {
      try {
        const payload = JSON.parse(datosSerieCompleta.textContent);
        const hoyPeriodo = payload.hoy;
        const serie = payload.meses || [];
        const idxHoy = serie.findIndex((m) => m.periodo === hoyPeriodo);

        const actualizarVistaGrafico = (vista) => {
          let slice;
          const idx = idxHoy >= 0 ? idxHoy : 12;
          if (vista === 'ultimos_3m') slice = serie.slice(Math.max(0, idx - 3), idx);
          else if (vista === 'ultimos_6m') slice = serie.slice(Math.max(0, idx - 6), idx);
          else if (vista === 'ultimos_12m') slice = serie.slice(Math.max(0, idx - 12), idx);
          else if (vista === 'futuro_3m') slice = serie.slice(idx, idx + 3);
          else if (vista === 'futuro_6m') slice = serie.slice(idx, idx + 6);
          else slice = serie.slice(Math.max(0, idx - 3), idx + 3);

          if (!slice || slice.length === 0) return;

          // 1. Actualizar gráfico
          configuracion.data.labels = slice.map((m) => m.etiqueta);
          configuracion.data.datasets[0].data = slice.map((m) => m.backlog);
          configuracion.data.datasets[1].data = slice.map((m) => m.mab);
          configuracion.data.datasets[2].data = slice.map((m) => m.meta);
          grafico.update();

          // 2. Actualizar tabla serie mensual
          const cuerpo = document.getElementById('cuerpo-serie-mensual');
          if (cuerpo) {
            cuerpo.innerHTML = slice.map((m) => `
              <tr>
                <td>${m.etiqueta}</td>
                <td class="num">${clp(m.backlog)}</td>
                <td class="num">${clp(m.mab)}</td>
                <td class="num fw-semibold">${clp(m.forecast)}</td>
                <td class="num">${clp(m.meta)}</td>
                <td class="num">${m.hc}</td>
              </tr>
            `).join('');
          }

          // 3. Actualizar pie de tabla (totales)
          const pie = document.getElementById('pie-serie-mensual');
          const totBacklog = slice.reduce((acc, m) => acc + m.backlog, 0);
          const totMab = slice.reduce((acc, m) => acc + m.mab, 0);
          const totForecast = slice.reduce((acc, m) => acc + m.forecast, 0);
          const totMeta = slice.reduce((acc, m) => acc + m.meta, 0);
          if (pie) {
            pie.innerHTML = `
              <tr class="fw-semibold">
                <td><button type="button" class="th-ayuda-btn" data-ayuda-titulo="Totales consolidados de la serie" data-ayuda-def="Consolidado acumulado de ingresos y metas para el horizonte completo analizado." data-ayuda-calc="Suma aritmética directa de los valores mensuales ya redondeados a CLP enteros (RN-88)."><span>Total</span><span class="ayuda-icono" aria-hidden="true">ℹ</span></button></td>
                <td class="num">${clp(totBacklog)}</td>
                <td class="num">${clp(totMab)}</td>
                <td class="num">${clp(totForecast)}</td>
                <td class="num">${clp(totMeta)}</td>
                <td></td>
              </tr>
            `;
          }

          // 4. Actualizar Delta y Cobertura
          const delta = totForecast - totMeta;
          const cob = totMeta > 0 ? Math.round((totForecast * 10000) / totMeta) / 100 : null;
          const textoDelta = document.getElementById('texto-delta-cobertura');
          if (textoDelta) {
            const cobTexto = cob !== null ? `Cobertura ${cob.toLocaleString('es-CL')} %.` : 'Sin meta para calcular cobertura.';
            textoDelta.textContent = `Delta del horizonte: ${clp(delta)}. ${cobTexto}`;
          }

          try {
            sessionStorage.setItem('proyecta_vista_grafico', vista);
          } catch (_) {}
        };

        const selVista = document.getElementById('vista-grafico');
        if (selVista) {
          selVista.addEventListener('change', () => {
            actualizarVistaGrafico(selVista.value);
          });
          const guardado = sessionStorage.getItem('proyecta_vista_grafico');
          if (guardado && guardado !== selVista.value) {
            selVista.value = guardado;
            actualizarVistaGrafico(guardado);
          }
        }
      } catch (err) {
        console.error('Error al inicializar vistas del gráfico:', err);
      }
    }
  }

  // Tooltips interactivos para métricas y grillas ejecutivas (US4, T008).
  let tooltipEl = document.getElementById('proyecta-tooltip');
  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.id = 'proyecta-tooltip';
    tooltipEl.className = 'proyecta-tooltip';
    tooltipEl.setAttribute('role', 'tooltip');
    tooltipEl.setAttribute('aria-hidden', 'true');
    tooltipEl.hidden = true;
    tooltipEl.innerHTML = `
      <div class="proyecta-tooltip__header">
        <div class="proyecta-tooltip__titulo-wrap">
          <span class="ayuda-icono" aria-hidden="true">ℹ</span>
          <strong class="proyecta-tooltip__titulo"></strong>
        </div>
        <button type="button" class="proyecta-tooltip__cerrar" aria-label="Cerrar ayuda">×</button>
      </div>
      <div class="proyecta-tooltip__seccion">
        <span class="proyecta-tooltip__etiqueta">¿Qué significa?</span>
        <p class="proyecta-tooltip__texto proyecta-tooltip__def"></p>
      </div>
      <div class="proyecta-tooltip__seccion">
        <span class="proyecta-tooltip__etiqueta">¿Cómo se calcula?</span>
        <p class="proyecta-tooltip__texto proyecta-tooltip__calc"></p>
      </div>
    `;
    document.body.appendChild(tooltipEl);
  }

  const tituloEl = tooltipEl.querySelector('.proyecta-tooltip__titulo');
  const defEl = tooltipEl.querySelector('.proyecta-tooltip__def');
  const calcEl = tooltipEl.querySelector('.proyecta-tooltip__calc');
  const btnCerrar = tooltipEl.querySelector('.proyecta-tooltip__cerrar');

  let elementoActivo = null;
  let fijado = false;
  let temporizadorOcultar = null;

  const formatearTexto = (texto) => {
    if (!texto) return '';
    const div = document.createElement('div');
    div.textContent = texto;
    let sanitizado = div.innerHTML;
    sanitizado = sanitizado.replace(/`([^`]+)`/g, '<code>$1</code>');
    return sanitizado;
  };

  const posicionarTooltip = (target) => {
    const rect = target.getBoundingClientRect();
    const tooltipRect = tooltipEl.getBoundingClientRect();
    const anchoTooltip = tooltipRect.width || 340;
    const altoTooltip = tooltipRect.height || 180;

    let top = rect.top - altoTooltip - 8;
    if (top < 10) {
      top = rect.bottom + 8;
    }
    let left = rect.left + (rect.width / 2) - (anchoTooltip / 2);
    if (left < 10) left = 10;
    if (left + anchoTooltip > window.innerWidth - 10) {
      left = window.innerWidth - anchoTooltip - 10;
    }

    tooltipEl.style.top = `${Math.round(top)}px`;
    tooltipEl.style.left = `${Math.round(left)}px`;
  };

  const mostrarTooltip = (target, esFijado = false) => {
    clearTimeout(temporizadorOcultar);
    const titulo = target.dataset.ayudaTitulo || target.getAttribute('aria-label') || '';
    const def = target.dataset.ayudaDef || '';
    const calc = target.dataset.ayudaCalc || '';
    if (!def && !calc) return;

    elementoActivo = target;
    fijado = esFijado;
    if (tituloEl) tituloEl.textContent = titulo;
    if (defEl) defEl.innerHTML = formatearTexto(def);
    if (calcEl) calcEl.innerHTML = formatearTexto(calc);

    tooltipEl.hidden = false;
    tooltipEl.setAttribute('aria-hidden', 'false');
    posicionarTooltip(target);
    tooltipEl.classList.add('visible');
  };

  const ocultarTooltip = (forzar = false) => {
    if (fijado && !forzar) return;
    clearTimeout(temporizadorOcultar);
    temporizadorOcultar = setTimeout(() => {
      tooltipEl.classList.remove('visible');
      tooltipEl.setAttribute('aria-hidden', 'true');
      tooltipEl.hidden = true;
      elementoActivo = null;
      fijado = false;
    }, 120);
  };

  btnCerrar?.addEventListener('click', (e) => {
    e.stopPropagation();
    const previo = elementoActivo;
    ocultarTooltip(true);
    previo?.focus();
  });

  tooltipEl.addEventListener('mouseenter', () => clearTimeout(temporizadorOcultar));
  tooltipEl.addEventListener('mouseleave', () => {
    if (!fijado) ocultarTooltip();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !tooltipEl.hidden) {
      const previo = elementoActivo;
      ocultarTooltip(true);
      previo?.focus();
    }
  });

  document.addEventListener('click', (e) => {
    if (!tooltipEl.hidden && !tooltipEl.contains(e.target) && !elementoActivo?.contains(e.target)) {
      ocultarTooltip(true);
    }
  });

  window.addEventListener('resize', () => {
    if (!tooltipEl.hidden && elementoActivo) {
      posicionarTooltip(elementoActivo);
    }
  });

  document.addEventListener('mouseover', (e) => {
    const trigger = e.target.closest('[data-ayuda-titulo]');
    if (trigger && !fijado) {
      mostrarTooltip(trigger, false);
    }
  });

  document.addEventListener('mouseout', (e) => {
    const trigger = e.target.closest('[data-ayuda-titulo]');
    if (trigger && !fijado) {
      ocultarTooltip();
    }
  });

  document.addEventListener('focusin', (e) => {
    const trigger = e.target.closest('[data-ayuda-titulo]');
    if (trigger && !fijado) {
      mostrarTooltip(trigger, false);
    }
  });

  document.addEventListener('focusout', (e) => {
    const trigger = e.target.closest('[data-ayuda-titulo]');
    if (trigger && !fijado) {
      ocultarTooltip();
    }
  });

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-ayuda-kpi, .th-ayuda-btn, .btn-ayuda-seccion, .btn-ayuda-inline');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      if (elementoActivo === btn && fijado) {
        ocultarTooltip(true);
      } else {
        mostrarTooltip(btn, true);
      }
    }
  });
});
