/* Interacciones accesibles compartidas; las reglas y los datos de la demo siguen en el HTML. */
const PAGE_COPY = {
  dash: ['Panorama de la cartera', 'Ingresos y capacidad', 'Revisa la proyección y abre un indicador para explorar sus registros. MAB: ingreso mensual ponderado por probabilidad y confiabilidad.'],
  pipe: ['Seguimiento comercial', 'Oportunidades y demandas', 'Selecciona un registro para revisar sus cifras, perfiles y seguimiento. Desliza la tabla para ver todas las columnas.'],
  audit: ['Control de cambios', 'Auditoría y trazabilidad', 'Consulta quién cambió cada dato, su motivo y el impacto en la proyección.'],
  params: ['Configuración de cálculo', 'Parámetros y vigencias', 'Define desde cuándo se aplican los parámetros y registra el motivo del cambio.']
};

function enhanceWorkspace(previous, previousAction) {
  const ws = document.getElementById('workspace');
  const copy = PAGE_COPY[S.module];
  ws.insertAdjacentHTML('afterbegin', `<header class="page-intro"><div><span class="page-eyebrow">${copy[0]}</span><h1>${copy[1]}</h1><p>${copy[2]}</p></div><span class="demo-tag">Demo · Cambios temporales</span></header>`);
  document.querySelectorAll('.nav-link').forEach(button => {
    if (button.classList.contains('active')) button.setAttribute('aria-current', 'page');
  });
  document.querySelectorAll('.sub-pill, .side-tab').forEach(button => button.setAttribute('aria-pressed', String(button.classList.contains('active'))));
  ws.querySelectorAll('table').forEach((table, index) => {
    table.querySelectorAll('thead th').forEach(th => th.scope = 'col');
    if (!table.parentElement.classList.contains('table-wrap')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrap';
      table.before(wrapper);
      wrapper.append(table);
    }
    const wrapper = table.parentElement;
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', `${copy[1]}: tabla ${index + 1}. Desplazamiento horizontal disponible.`);
  });
  ws.querySelectorAll('tr[onclick], svg g[onclick]').forEach(item => {
    item.tabIndex = 0;
    if (item.tagName.toLowerCase() === 'g') {
      item.setAttribute('role', 'button');
      item.setAttribute('aria-label', item.querySelector('title')?.textContent || 'Seleccionar mes');
    } else {
      item.setAttribute('aria-label', `${item.textContent.trim().replace(/\s+/g, ' ')}. Abrir detalle.`);
      if (item.classList.contains('selected')) item.setAttribute('aria-current', 'true');
    }
    item.addEventListener('keydown', event => {
      if (event.target === item && ['Enter', ' '].includes(event.key)) {
        event.preventDefault();
        item.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      }
    });
  });
  ws.querySelectorAll('.dot[title]').forEach(dot => {
    const text = document.createElement('span');
    text.className = 'quality-text';
    text.textContent = dot.title;
    dot.setAttribute('aria-hidden', 'true');
    dot.after(text);
  });
  ws.querySelectorAll('.err-text').forEach(el => el.setAttribute('role', 'alert'));
  ws.querySelectorAll('svg').forEach(svg => svg.setAttribute('aria-label', 'Forecast mensual en CLP. Cifras disponibles en la tabla siguiente.'));
  // Las vistas se regeneran: conservar el foco del control que originó el cambio.
  if (previous && !previous.isConnected) {
    const replacement = Array.from(document.querySelectorAll('[onclick]')).find(el => el.getAttribute('onclick') === previousAction);
    if (replacement) replacement.focus({ preventScroll: true });
    else ws.focus({ preventScroll: true });
  }
  const count = S.module === 'pipe' ? getPipelineRecords().length : getBaseFilteredRecords(false).length;
  document.getElementById('workspace-status').textContent = `${copy[1]}. ${count} registros para los filtros actuales.`;
}

function presentDraftErrors(errors) {
  const box = document.getElementById('modal-box');
  box.querySelectorAll('.field-error').forEach(el => el.remove());
  box.querySelectorAll('[aria-invalid]').forEach(el => {
    el.removeAttribute('aria-invalid');
    el.removeAttribute('aria-describedby');
  });
  const fields = Array.from(box.querySelectorAll('.fld input'));
  const links = errors.map((message, index) => {
    const needles = message.startsWith('El nombre') ? ['DRAFT.name=']
      : message.startsWith('El cliente') ? ['DRAFT.client=']
      : message.startsWith('La fecha') ? ['onDraftDatesChange']
      : message.startsWith('Probabilidad') ? ['DRAFT.prob=']
      : message.startsWith('Indica') ? ['DRAFT.directReason=']
      : message.includes('nombre') ? ['.role=']
      : message.includes('HC') ? ['.hc=']
      : message.includes('dedicación') ? ['.ded='] : ['.rates['];
    const matches = fields.filter(el => needles.some(needle => (el.getAttribute('oninput') || '').includes(needle)));
    matches.forEach((el, fieldIndex) => {
      if (!el.id) el.id = `draft-field-${fields.indexOf(el)}`;
      const hint = document.createElement('small');
      hint.className = 'field-error';
      hint.id = `draft-error-${index}-${fieldIndex}`;
      hint.textContent = message;
      el.setAttribute('aria-invalid', 'true');
      el.setAttribute('aria-describedby', hint.id);
      el.after(hint);
    });
    return `<li>${matches[0] ? `<a href="#${matches[0].id}" onclick="document.getElementById('${matches[0].id}').focus();return false">${esc(message)}</a>` : esc(message)}</li>`;
  });
  const summary = document.getElementById('draft-err-box');
  summary.tabIndex = -1;
  summary.innerHTML = errors.length ? `<strong>Completa los datos para guardar</strong><ul>${links.join('')}</ul>` : '';
  document.getElementById('btn-save-rec').setAttribute('aria-describedby', 'draft-err-box');
}

const dialogs = [
  { overlay: document.getElementById('modal-overlay'), panel: document.getElementById('modal-box'), className: 'open', open: false },
  { overlay: document.getElementById('login-modal'), panel: document.querySelector('.login-box'), className: 'active', open: false }
];
const focusable = panel => Array.from(panel.querySelectorAll('button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [tabindex="0"]')).filter(el => el.getClientRects().length);
function syncDialogs() {
  let restoreFocus;
  dialogs.forEach(dialog => {
    const open = dialog.overlay.classList.contains(dialog.className);
    const heading = dialog.panel.querySelector('h2, h3');
    if (heading) {
      heading.id = `${dialog.overlay.id}-title`;
      heading.tabIndex = -1;
      dialog.panel.setAttribute('aria-labelledby', heading.id);
    }
    if (open && !dialog.open) {
      dialog.trigger = document.activeElement;
      dialog.panel.setAttribute('role', 'dialog');
      dialog.panel.setAttribute('aria-modal', 'true');
      dialog.panel.tabIndex = -1;
      if (heading) {
        heading.focus();
      } else dialog.panel.focus();
    }
    if (open && dialog.open && !dialog.panel.contains(document.activeElement)) (heading || dialog.panel).focus();
    if (!open && dialog.open && dialog.trigger?.isConnected) restoreFocus = dialog.trigger;
    dialog.open = open;
    dialog.panel.querySelectorAll('.err-text').forEach(el => el.setAttribute('role', 'alert'));
  });
  const active = dialogs.find(dialog => dialog.open);
  document.body.style.overflow = active ? 'hidden' : '';
  Array.from(document.body.children).forEach(el => {
    if (!['SCRIPT', 'LINK', 'STYLE'].includes(el.tagName)) el.inert = Boolean(active && el !== active.overlay && el.id !== 'toast');
  });
  if (restoreFocus) restoreFocus.focus();
}
dialogs.forEach(dialog => new MutationObserver(syncDialogs).observe(dialog.overlay, { attributes: true, attributeFilter: ['class'], childList: true, subtree: true }));
document.addEventListener('keydown', event => {
  const dialog = dialogs.find(item => item.open);
  if (!dialog) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    dialog.overlay.classList.remove(dialog.className);
  } else if (event.key === 'Tab') {
    const controls = focusable(dialog.panel);
    const index = controls.indexOf(document.activeElement);
    if (!controls.length) { event.preventDefault(); dialog.panel.focus(); }
    else if (event.shiftKey && index <= 0) { event.preventDefault(); controls.at(-1).focus(); }
    else if (!event.shiftKey && (index === -1 || index === controls.length - 1)) { event.preventDefault(); controls[0].focus(); }
  }
});
document.getElementById('role-switcher').setAttribute('aria-label', 'Perfil de demostración');
document.getElementById('theme-btn').setAttribute('aria-label', 'Cambiar entre tema claro y oscuro');
refreshWorkspace();
