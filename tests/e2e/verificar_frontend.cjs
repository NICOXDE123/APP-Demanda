/* Requiere la demo local: node tests/e2e/verificar_frontend.cjs (Node 22+, Chrome/Edge). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

async function main() {
  const base = process.env.PROYECTA_URL || 'http://127.0.0.1:8000';
  const browser = process.env.PROYECTA_BROWSER || [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  ].find((file) => fs.existsSync(file));
  assert.ok(browser, 'Define PROYECTA_BROWSER con Chrome o Edge.');
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'proyecta-escritorio-'));
  const proc = spawn(browser, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--remote-debugging-port=0', `--user-data-dir=${path.join(out, 'profile')}`, 'about:blank'],
  { windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
  let socket;
  try {
    const endpoint = await new Promise((resolve, reject) => {
      let stderr = '';
      const timer = setTimeout(() => reject(new Error('No inició el navegador.')), 20000);
      proc.on('error', reject);
      proc.stderr.on('data', (data) => {
        stderr += data;
        const match = stderr.match(/DevTools listening on (ws:\/\/\S+)/);
        if (match) { clearTimeout(timer); resolve(match[1]); }
      });
    });
    const pages = await (await fetch(`${endpoint.replace('ws:', 'http:').split('/devtools/')[0]}/json`)).json();
    socket = new WebSocket(pages.find((page) => page.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
    let id = 0;
    const pending = new Map(), errors = [];
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.id) {
        const task = pending.get(data.id);
        if (task) { clearTimeout(task.timer); pending.delete(data.id); data.error ? task.reject(data.error) : task.resolve(data.result); }
      }
      if (data.method === 'Runtime.exceptionThrown') errors.push(data.params.exceptionDetails.exception?.description || data.params.exceptionDetails.text);
    };
    const call = (method, params = {}) => new Promise((resolve, reject) => {
      const requestId = ++id;
      const timer = setTimeout(() => reject(new Error(`Timeout ${method}`)), 20000);
      pending.set(requestId, { resolve, reject, timer });
      socket.send(JSON.stringify({ id: requestId, method, params }));
    });
    const ev = async (expression) => {
      const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description);
      return result.result.value;
    };
    const until = async (expression) => {
      for (let i = 0; i < 100; i++) {
        if (await ev(expression)) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      throw new Error(`No se cumplió: ${expression}`);
    };
    const go = async (route) => {
      await call('Page.navigate', { url: base + route });
      await until(`document.readyState === 'complete' && location.href === ${JSON.stringify(base + route)}`);
      await ev("document.documentElement.style.scrollBehavior='auto'");
    };
    const key = async (key, code, n, text) => {
      await call('Input.dispatchKeyEvent', { type: 'keyDown', key, code, windowsVirtualKeyCode: n,
        ...(text ? { text, unmodifiedText: text } : {}) });
      await call('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode: n });
    };
    const shot = async (name) => {
      await ev('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
      const data = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
      fs.writeFileSync(path.join(out, name + '.png'), Buffer.from(data.data, 'base64'));
    };
    const contrast = (a, b) => {
      const luminance = (value) => {
        const rgb = value.startsWith('#') ? value.slice(1).match(/../g).map((x) => parseInt(x, 16)) : value.match(/[\d.]+/g).slice(0, 3).map(Number);
        const linear = rgb.map((x) => x / 255).map((x) => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4);
        return linear[0] * .2126 + linear[1] * .7152 + linear[2] * .0722;
      };
      const x = luminance(a), y = luminance(b);
      return (Math.max(x, y) + .05) / (Math.min(x, y) + .05);
    };
    const checkContrast = async () => {
      const colors = await ev(`(()=>{const root=getComputedStyle(document.documentElement),card=getComputedStyle(document.querySelector('.card')),control=getComputedStyle(document.querySelector('.form-control'));
        return {theme:document.documentElement.dataset.bsTheme,secondary:getComputedStyle(document.querySelector('.text-secondary')).color,body:getComputedStyle(document.body).backgroundColor,
          nav:getComputedStyle(document.querySelector('.nav-link')).color,navBg:getComputedStyle(document.querySelector('nav')).backgroundColor,
          border:control.borderColor,controlBg:control.backgroundColor,mab:root.getPropertyValue('--grafico-mab').trim(),mabBorde:root.getPropertyValue('--grafico-trama').trim(),card:card.backgroundColor}})()`);
      const ratios = { secondary: contrast(colors.secondary, colors.body), nav: contrast(colors.nav, colors.navBg),
        border: contrast(colors.border, colors.controlBg), mab: Math.max(contrast(colors.mab, colors.card), contrast(colors.mabBorde, colors.card)) };
      assert.ok(ratios.secondary >= 4.5, JSON.stringify(colors)); assert.ok(ratios.nav >= 4.5);
      assert.ok(ratios.border >= 3); assert.ok(ratios.mab >= 3);
      assert.ok(await ev("Chart.getChart(document.querySelector('canvas')).getDatasetMeta(0).data[0].options.backgroundColor instanceof CanvasGradient"), 'Backlog usa un gradiente');
      assert.ok(await ev("Chart.getChart(document.querySelector('canvas')).getDatasetMeta(1).data[0].options.backgroundColor instanceof CanvasPattern"), 'La MAB se representa con trama');
      assert.ok(await ev("Chart.getChart(document.querySelector('canvas')).data.datasets[2].pointBorderColor === getComputedStyle(document.documentElement).getPropertyValue('--grafico-punto-borde').trim()"), 'Los puntos de meta usan el tema actual');
      assert.notEqual(colors.body, colors.card, 'Las tarjetas se separan del fondo en ambos temas');
      const kpi = await ev(`(()=>{const el=document.querySelector('.kpi .valor'),s=getComputedStyle(el); return {size:parseFloat(s.fontSize),fits:el.scrollWidth<=el.clientWidth}})()`);
      assert.ok(kpi.size >= 24 && kpi.fits, 'Las cifras son protagonistas y caben en la tarjeta');
      const tab = await ev("(()=>{const s=getComputedStyle(document.querySelector('.nav-tabs .active')); return {text:s.color,bg:s.backgroundColor}})()");
      assert.ok(contrast(tab.text, tab.bg) >= 4.5, `Contraste de la pestaña activa: ${JSON.stringify(tab)}`);
      console.log(`Contraste ${colors.theme}: ${JSON.stringify(ratios)}`);
    };
    await call('Page.enable'); await call('Runtime.enable'); await call('Network.enable');
    await call('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
    await call('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'dark' }] });
    await go('/login');
    assert.equal(await ev('document.documentElement.dataset.bsTheme'), 'dark', 'Tema del sistema en primera visita');
    await ev(`document.querySelector('#email').value='operaciones@example.test'; document.querySelector('#password').value=${JSON.stringify(process.env.PROYECTA_DEMO_PASSWORD || 'proyecta-demo')}; document.querySelector('form').requestSubmit()`);
    await until("location.pathname==='/' && !!document.querySelector('#datos-grafico') && document.readyState==='complete'");
    await until("!!Chart.getChart(document.querySelector('canvas'))");
    const changeTheme = async (value) => ev(`document.querySelector('[data-tema]').value=${JSON.stringify(value)}; document.querySelector('[data-tema]').dispatchEvent(new Event('change'))`);
    await changeTheme('light');
    await checkContrast();
    assert.equal(await ev('document.documentElement.dataset.bsTheme'), 'light');
    await ev("document.querySelector('.nav-link').focus()"); await key('Tab', 'Tab', 9);
    assert.equal(await ev('getComputedStyle(document.activeElement).outlineStyle'), 'solid');
    assert.ok(await ev("document.querySelector('.nav-link[aria-current=page]').textContent==='Dashboard'"));
    await shot('dashboard-claro');
    await ev("document.querySelector('[data-serie=\"1\"]').focus()"); await key(' ', 'Space', 32, ' ');
    assert.equal(await ev("Chart.getChart(document.querySelector('canvas')).isDatasetVisible(1)"), false);
    await changeTheme('dark');
    assert.equal(await ev("Chart.getChart(document.querySelector('canvas')).isDatasetVisible(1)"), false, 'Cambiar tema conserva la selección de series');
    await key(' ', 'Space', 32, ' ');
    await checkContrast();
    assert.ok(await ev("Chart.getChart(document.querySelector('canvas')).options.scales.y.ticks.color === getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color').trim()"));
    await shot('dashboard-oscuro');
    await ev("document.querySelector('#grafico').scrollIntoView({block:'center'})");
    await shot('grafico-oscuro');
    await changeTheme('light');
    await ev("document.querySelector('#grafico').scrollIntoView({block:'center'})");
    await shot('grafico-claro');
    await ev('scrollTo(0, 0)');
    for (const width of [1280, 1366, 1920]) {
      await call('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
      for (const theme of ['light', 'dark']) {
        await changeTheme(theme);
        await checkContrast();
        assert.ok(await ev('document.documentElement.scrollWidth <= innerWidth'), `Sin desborde a ${width}px`);
        assert.ok(await ev("[...document.querySelectorAll('.kpi .valor')].every(el => el.scrollWidth <= el.clientWidth)"), 'Todas las cifras caben');
        await shot(`dashboard-${theme}-${width}`);
      }
    }
    await call('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
    await go('/parametros');
    assert.equal(await ev('document.documentElement.dataset.bsTheme'), 'dark', 'Preferencia persistida');
    await changeTheme('sistema');
    await call('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }] });
    await until("document.documentElement.dataset.bsTheme==='light'");
    await go('/registros?q=software&meses=3');
    const href = await ev("document.querySelector('tbody a').getAttribute('href')");
    await go(href);
    assert.equal(await ev("document.querySelector('.nav-link[aria-current=location]').textContent"), 'Registros');
    assert.equal(await ev("document.querySelector('[aria-label=\"Migas de pan\"] a').getAttribute('href')"), '/registros?q=software&meses=3');
    await go('/registros?activos=1');
    for (const theme of ['light', 'dark']) {
      await changeTheme(theme);
      const badges = await ev("[...document.querySelectorAll('.estado-badge')].map(el=>({color:getComputedStyle(el).color,bg:getComputedStyle(el).backgroundColor,text:el.textContent}))");
      assert.ok(badges.length > 0, 'Los registros muestran estados con texto');
      for (const badge of badges) assert.ok(contrast(badge.color, badge.bg) >= 4.5, `Contraste del estado ${badge.text} en ${theme}`);
      await shot(`registros-${theme}`);
      await go('/auditoria');
      await shot(`auditoria-${theme}`);
      await go('/registros?activos=1');
    }
    await changeTheme('light');
    await ev("document.querySelector('[data-dialog-open]').focus()"); await key('Enter', 'Enter', 13, '\r');
    await until("document.querySelector('dialog').open && document.querySelector('#estado-previa').textContent.includes('actualizada')");
    const before = await ev("document.querySelector('#vista-previa').textContent");
    await call('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
    await ev("document.querySelector('[name=p1_tarifa]').value='30.000'; document.querySelector('[name=p1_tarifa]').dispatchEvent(new Event('input',{bubbles:true}))");
    await until("document.querySelector('#estado-previa').textContent.includes('No se pudo actualizar')");
    assert.equal(await ev("document.querySelector('#vista-previa').textContent"), before);
    await call('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
    await ev("document.querySelector('[data-reintentar-previa]').click()");
    await until("document.querySelector('#estado-previa').textContent.includes('actualizada')");
    assert.notEqual(await ev("document.querySelector('#vista-previa').textContent"), before);
    await shot('alta-claro');
    await key('Escape', 'Escape', 27);
    assert.equal(await ev('document.activeElement.textContent'), 'Nuevo registro');
    await ev("document.querySelector('[data-dialog-open]').click(); document.querySelector('#servicio').value='Borrador sintético UX'; for (const n of ['cliente_id','sector_id','manager_id']) document.getElementById(n).selectedIndex=1; document.querySelector('[name=p1_hc]').value=''; document.querySelector('#alta').requestSubmit()");
    await until("location.pathname==='/registros' && !!document.querySelector('[data-error-summary]')");
    await until("document.activeElement.hasAttribute('data-error-summary')");
    await ev("document.querySelector('[data-error-summary] a').click()");
    assert.equal(await ev('document.activeElement.id'), 'p1_hc');
    assert.equal(await ev('document.activeElement.getAttribute("aria-invalid")'), 'true');
    await shot('alta-error');
    await key('Escape', 'Escape', 27);
    await changeTheme('dark');
    await ev("document.querySelector('[data-dialog-open]').click()");
    await shot('alta-error-oscuro');
    // Entrega 3: distribución, sincronización del HC y controles maestro-detalle.
    await call('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
    await go('/');
    await ev("document.querySelector('#tab-financiero-btn').click()");
    await until("!!Chart.getChart(document.querySelector('#grafico-hc'))");
    await ev("document.querySelector('#vista-grafico').value='default'; document.querySelector('#vista-grafico').dispatchEvent(new Event('change'))");
    for (const theme of ['light', 'dark']) {
      await changeTheme(theme);
      const franjas = await ev(`(() => {
        const chart=Chart.getChart(document.querySelector('#grafico'));
        const opciones=chart.options.plugins.periodosTemporales;
        const estilo=getComputedStyle(document.documentElement);
        const auxiliar=document.createElement('canvas').getContext('2d');
        return ['anterior','actual','posterior'].map(tipo=>{
          const i=opciones.periodos.findIndex(p=>tipo==='anterior'?p<opciones.actual:tipo==='actual'?p===opciones.actual:p>opciones.actual);
          if(i<0) return {tipo,indice:i};
          auxiliar.fillStyle=estilo.getPropertyValue('--periodo-'+tipo+'-fondo').trim();
          auxiliar.fillRect(0,0,1,1);
          const ratio=chart.currentDevicePixelRatio;
          return {tipo,indice:i,esperado:[...auxiliar.getImageData(0,0,1,1).data],
            real:[...chart.ctx.getImageData(Math.round(chart.scales.x.getPixelForValue(i)*ratio),Math.round((chart.chartArea.top+10)*ratio),1,1).data]};
        });
      })()`);
      assert.ok(franjas.every(f=>f.indice>=0), 'La vista mixta incluye meses anteriores, actual y posteriores');
      for (const franja of franjas) assert.deepEqual(franja.real, franja.esperado, `Fondo ${franja.tipo} en ${theme}`);
      assert.equal(new Set(franjas.map(f=>JSON.stringify(f.real))).size, 3, 'Tres colores temporales distintos');
      await ev("document.querySelector('.finanzas-grid').scrollIntoView({block:'start'})");
      await shot(`grafico-periodos-${theme}`);
    }
    await ev("document.querySelector('#vista-grafico').value='ultimos_12m'; document.querySelector('#vista-grafico').dispatchEvent(new Event('change'))");
    assert.ok(await ev("(()=>{const o=Chart.getChart(document.querySelector('#grafico')).options.plugins.periodosTemporales;return o.periodos.length===12&&o.periodos.every(p=>p<o.actual)})()"), 'Los doce meses anteriores se clasifican como anteriores, incluso al cambiar de año');
    await ev("document.querySelector('#vista-grafico').value='futuro_3m'; document.querySelector('#vista-grafico').dispatchEvent(new Event('change'))");
    assert.ok(await ev("(()=>{const o=Chart.getChart(document.querySelector('#grafico')).options.plugins.periodosTemporales;return o.periodos[0]===o.actual&&o.periodos.slice(1).every(p=>p>o.actual)})()"), 'El horizonte futuro conserva el mes actual y distingue los siguientes');
    assert.deepEqual(await ev("Chart.getChart(document.querySelector('#grafico-hc')).data.datasets[0].data"),
      await ev("[...document.querySelectorAll('#cuerpo-serie-mensual tr')].map(fila=>Number(fila.cells[5].textContent))"), 'Dotación sincronizada con el horizonte de la tabla');
    for (const theme of ['light', 'dark']) {
      await changeTheme(theme);
      assert.equal(await ev("Chart.getChart(document.querySelector('#grafico-hc')).data.labels.length"), 3);
      await ev("document.querySelector('.finanzas-grid').scrollIntoView({block:'start'})");
      await shot(`entrega3-financiero-${theme}`);
      await ev("document.querySelector('#tab-operativo-btn').click()");
      assert.ok(await ev("document.querySelector('#alertas-operativas').getBoundingClientRect().top < document.querySelector('#lideres').getBoundingClientRect().top"), 'Alertas antes del cumplimiento por líder');
      await ev("document.querySelector('#alertas-operativas').scrollIntoView({block:'start'})");
      await shot(`entrega3-operativo-${theme}`);
      await ev("document.querySelector('#tab-financiero-btn').click()");
    }
    await go('/parametros');
    await ev("document.querySelector('#historial-parametros-btn').focus()");
    await key('End', 'End', 35);
    assert.equal(await ev("document.querySelector('#historial-metas').hidden"), false);
    assert.equal(await ev("document.querySelector('#historial-parametros').hidden"), true);
    await key('Home', 'Home', 36);
    assert.equal(await ev("document.querySelector('#historial-parametros').hidden"), false);
    const primero = await ev("document.querySelector('[data-meta-lider]').selectedIndex");
    await ev("const lider=document.querySelector('[data-meta-lider]'); lider.selectedIndex=(lider.selectedIndex+1)%lider.options.length; lider.dispatchEvent(new Event('change'))");
    assert.ok(await ev("document.querySelector('[data-meta-nombre]').textContent === document.querySelector('[data-meta-lider]').selectedOptions[0].textContent"));
    assert.notEqual(await ev("document.querySelector('[data-meta-lider]').selectedIndex"), primero);
    for (const theme of ['light', 'dark']) {
      await changeTheme(theme);
      await ev("document.querySelector('.parametros-grid').scrollIntoView({block:'start'})");
      await shot(`entrega3-parametros-${theme}`);
    }
    await go('/auditoria');
    const primerDetalle = await ev("document.querySelector('[data-audit-panel]:not([hidden])').id");
    await ev("document.querySelectorAll('[data-audit-select]')[1].focus()");
    await key('Enter', 'Enter', 13, '\r');
    assert.notEqual(await ev("document.querySelector('[data-audit-panel]:not([hidden])').id"), primerDetalle);
    assert.equal(await ev("document.querySelectorAll('[data-audit-panel]:not([hidden])').length"), 1);
    assert.equal(await ev("document.querySelectorAll('[data-audit-select][aria-expanded=true]').length"), 1);
    await ev("document.querySelectorAll('.audit-row')[2].cells[0].click()");
    assert.ok(await ev("document.querySelectorAll('[data-audit-select]')[2].getAttribute('aria-expanded')==='true'"));
    for (const theme of ['light', 'dark']) {
      await changeTheme(theme);
      await ev("document.querySelector('.auditoria-grid').scrollIntoView({block:'start'})");
      await shot(`entrega3-auditoria-${theme}`);
    }
    await go('/auditoria?codigo=OPD-SIN-COINCIDENCIAS');
    assert.ok(await ev("document.querySelector('main').textContent.includes('Sin eventos con estos filtros')"));
    await call('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    for (const route of ['/', '/auditoria', '/parametros']) {
      await go(route);
      assert.ok(await ev('document.documentElement.scrollWidth <= innerWidth'), `Sin desborde móvil: ${route}`);
    }
    await call('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
    await go('/?q=sin-coincidencias-auditoria');
    assert.ok(await ev("document.querySelector('[role=status]').textContent.includes('No hay registros')"));
    await go('/registros/no-es-uuid');
    assert.ok(await ev("document.querySelector('main').textContent.includes('El enlace del registro no es válido')"));
    for (const resource of ['/static/favicon.svg', '/static/favicon.ico']) {
      const response = await fetch(base + resource); assert.equal(response.status, 200, resource);
    }
    assert.deepEqual(errors, [], 'Sin excepciones JavaScript');
    console.log(`Verificación de escritorio correcta. Capturas: ${out}`);
  } finally {
    if (socket) socket.close(); proc.kill();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
