// Se aplica antes del primer pintado; los recursos propios respetan la CSP.
(() => {
  const sistema = window.matchMedia('(prefers-color-scheme: dark)');
  let preferencia = 'sistema';
  try { preferencia = localStorage.getItem('proyecta-tema') || 'sistema'; } catch { /* Almacenamiento restringido. */ }
  if (!['sistema', 'light', 'dark'].includes(preferencia)) preferencia = 'sistema';
  const aplicar = () => {
    document.documentElement.dataset.bsTheme = preferencia === 'sistema' ? (sistema.matches ? 'dark' : 'light') : preferencia;
    document.dispatchEvent(new Event('proyecta:tema'));
  };
  aplicar();
  sistema.addEventListener('change', () => { if (preferencia === 'sistema') aplicar(); });
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tema]').forEach((selector) => {
      selector.value = preferencia;
      selector.addEventListener('change', () => {
        preferencia = selector.value;
        try { localStorage.setItem('proyecta-tema', preferencia); } catch { /* La selección funciona durante la visita. */ }
        aplicar();
      });
    });
  });
})();
