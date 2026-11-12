/* Comprobación local sin dependencias: node docs/mockups/verificar-mockup.cjs */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');

async function main() {
  const browser = process.env.MOCKUP_BROWSER || [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
  ].find(file => fs.existsSync(file));
  if (!browser) throw new Error('Define MOCKUP_BROWSER con la ruta de Chrome o Edge.');
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'proyecta-mockup-'));
  const proc = spawn(browser, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'], { windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
  let socket;
  try {
    const endpoint = await new Promise((resolve, reject) => {
      let stderr = '';
      const timer = setTimeout(() => reject(new Error('El navegador no inició DevTools.')), 20000);
      proc.on('error', error => { clearTimeout(timer); reject(error); });
      proc.stderr.on('data', data => {
        stderr += data;
        const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
        if (match) { clearTimeout(timer); resolve(match[1]); }
      });
    });
    const base = endpoint.replace('ws:', 'http:').split('/devtools/')[0];
    const pages = await (await fetch(`${base}/json`)).json();
    socket = new WebSocket(pages.find(page => page.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
    let id = 0;
    const pending = new Map();
    const errors = [];
    socket.onmessage = event => {
      const data = JSON.parse(event.data);
      if (data.id) {
        const task = pending.get(data.id);
        if (task) { clearTimeout(task.timer); pending.delete(data.id); data.error ? task.reject(data.error) : task.resolve(data.result); }
      }
      if (data.method === 'Runtime.exceptionThrown') errors.push(data.params.exceptionDetails.text + ': ' + (data.params.exceptionDetails.exception?.description || ''));
    };
    const call = (method, params = {}) => new Promise((resolve, reject) => {
      const requestId = ++id;
      const timer = setTimeout(() => { pending.delete(requestId); reject(new Error(`Timeout: ${method}`)); }, 15000);
      pending.set(requestId, { resolve, reject, timer });
      socket.send(JSON.stringify({ id: requestId, method, params }));
    });
    const evaluate = async expression => {
      const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
      return result.result.value;
    };
    const settle = () => evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
    await call('Runtime.enable');
    await call('Page.enable');
    await call('Page.navigate', { url: pathToFileURL(path.join(__dirname, 'proyecta-mvp-mockup.html')).href });
    for (let tries = 0; tries < 60; tries++) {
      if (await evaluate('typeof enhanceWorkspace === "function" && !!document.querySelector("h1")')) break;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    assert.equal(await evaluate('document.querySelectorAll("h1").length'), 1);
    const out = path.join(__dirname, '.verificacion');
    fs.mkdirSync(out, { recursive: true });
    const report = [];
    for (const width of [1440, 768, 320, 390]) {
      await call('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: false });
      for (const module of ['dash', 'pipe', 'audit', 'params']) {
        await evaluate(`S.module=${JSON.stringify(module)};refreshWorkspace()`);
        await settle();
        const sizes = await evaluate('({viewport:innerWidth, document:document.documentElement.scrollWidth})');
        assert.ok(sizes.document <= sizes.viewport + 1, `${module} desborda a ${width}px: ${JSON.stringify(sizes)}`);
        report.push(`${width}px · ${module}: sin desbordamiento de página`);
      }
      await evaluate("S.module='dash';refreshWorkspace()");
      await evaluate("document.querySelector('.chart-data').open=true");
      assert.ok(await evaluate("document.querySelector('.chart-data tbody').rows.length === S.forecastHorizon"));
      await evaluate("document.querySelector('.chart-data').open=false");
      const shot = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
      fs.writeFileSync(path.join(out, `dashboard-${width}.png`), Buffer.from(shot.data, 'base64'));
    }
    await evaluate("document.querySelectorAll('.op-card')[3].click()");
    assert.equal(await evaluate("S.module === 'pipe' && S.filters.stateFilter === 'ACTIVE'"), true);
    await evaluate("onSearchInput('sin-resultados-xyz')");
    assert.equal(await evaluate('getPipelineRecords().length'), 0);
    assert.ok(await evaluate("document.getElementById('workspace').textContent.includes('Sin registros')"));
    await evaluate('resetFilters()');
    await evaluate("document.getElementById('btn-new-record').focus();openRecordModal()");
    await settle();
    assert.ok(await evaluate("document.getElementById('modal-box').scrollWidth <= document.getElementById('modal-box').clientWidth + 1"), 'Formulario sin desbordamiento horizontal');
    assert.equal(await evaluate("document.getElementById('modal-box').getAttribute('aria-modal')"), 'true');
    assert.ok(await evaluate("document.getElementById('modal-box').contains(document.activeElement)"));
    assert.equal(await evaluate("document.getElementById('btn-save-rec').disabled"), true);
    assert.ok(await evaluate("document.querySelectorAll('[aria-invalid=true]').length >= 2"));
    await call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
    assert.ok(await evaluate("document.getElementById('modal-box').contains(document.activeElement)"));
    await call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9, modifiers: 8 });
    assert.ok(await evaluate("document.getElementById('modal-box').contains(document.activeElement)"));
    const modalShot = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(out, 'formulario-390.png'), Buffer.from(modalShot.data, 'base64'));
    await call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await settle();
    assert.equal(await evaluate("document.activeElement.id"), 'btn-new-record');
    await evaluate('openRecordModal()');
    await settle();
    const before = await evaluate('S.records.length');
    await evaluate("DRAFT.name='Proyecto de prueba UX';DRAFT.client='Cliente Sintético UX';validateDraftForm()");
    assert.equal(await evaluate("document.getElementById('btn-save-rec').disabled"), false);
    await evaluate('saveDraftRecord()');
    assert.equal(await evaluate('S.records.length'), before + 1);
    // Verificar que la exportación conserva las filas visibles sin descargar archivos.
    await evaluate("window.exportedFilename='';window.exportedBlob=null;URL.createObjectURL=blob=>{window.exportedBlob=blob;return 'blob:demo'};URL.revokeObjectURL=()=>{};HTMLAnchorElement.prototype.click=function(){window.exportedFilename=this.download};exportPipelineCSV()");
    assert.ok((await evaluate('window.exportedFilename')).endsWith('.csv'));
    assert.ok((await evaluate('window.exportedBlob.text()')).includes('Cliente Sintético UX'));
    await evaluate("S.module='pipe';refreshWorkspace();document.querySelector('tr[onclick]').focus()");
    await call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
    assert.ok(await evaluate('!!S.selectedId'));
    await evaluate("switchRole('Ejecutivo')");
    assert.equal(await evaluate("getComputedStyle(document.getElementById('btn-new-record')).display"), 'none');
    await evaluate("switchRole('Líder')");
    assert.equal(await evaluate("document.getElementById('filter-manager').disabled"), true);
    await evaluate("switchRole('Operaciones');S.module='dash';refreshWorkspace();toggleTheme()");
    assert.equal(await evaluate('document.documentElement.dataset.theme'), 'dark');
    const darkShot = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(out, 'dashboard-390-oscuro.png'), Buffer.from(darkShot.data, 'base64'));
    await evaluate("document.getElementById('login-modal').classList.add('active')");
    await settle();
    assert.ok(await evaluate("document.getElementById('login-modal').contains(document.activeElement)"));
    await call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    assert.deepEqual(errors, [], 'Errores JavaScript del navegador');
    report.push('MAB, búsqueda vacía, creación, errores de formulario, teclado en diálogo y tabla, roles y tema: OK');
    fs.writeFileSync(path.join(out, 'resultado.txt'), report.join('\n') + '\n', 'utf8');
    console.log(report.join('\n'));
    console.log(`Capturas: ${out}`);
    await call('Browser.close');
  } finally {
    socket?.close();
    if (proc.exitCode === null) proc.kill();
    // El perfil temporal se conserva para evitar borrar archivos mientras Chrome termina.
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
