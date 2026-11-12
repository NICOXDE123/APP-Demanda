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
          border:control.borderColor,controlBg:control.backgroundColor,mab:root.getPropertyValue('--grafico-mab').trim(),card:card.backgroundColor}})()`);
      const ratios = { secondary: contrast(colors.secondary, colors.body), nav: contrast(colors.nav, colors.navBg),
        border: contrast(colors.border, colors.controlBg), mab: contrast(colors.mab, colors.card) };
      assert.ok(ratios.secondary >= 4.5, JSON.stringify(colors)); assert.ok(ratios.nav >= 4.5);
      assert.ok(ratios.border >= 3); assert.ok(ratios.mab >= 3);
      const barra = await ev("({actual:Chart.getChart(document.querySelector('canvas')).getDatasetMeta(0).data[0].options.backgroundColor,esperado:getComputedStyle(document.documentElement).getPropertyValue('--grafico-backlog').trim(),dataset:Chart.getChart(document.querySelector('canvas')).data.datasets[0].backgroundColor})");
      assert.equal(barra.actual, barra.esperado, 'La barra usa el color del tema: ' + JSON.stringify(barra));
      assert.ok(await ev("Chart.getChart(document.querySelector('canvas')).getDatasetMeta(1).data[0].options.backgroundColor instanceof CanvasPattern"), 'La MAB se representa con trama');
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
    assert.equal(await ev("Chart.getChart(document.querySelector('canvas')).options.scales.y.ticks.color"), '#dee2e6');
    await shot('dashboard-oscuro');
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
