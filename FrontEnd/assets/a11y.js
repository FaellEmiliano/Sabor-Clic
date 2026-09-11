(() => {
  const KEY = 'sabor-clic-a11y';
  const state = JSON.parse(localStorage.getItem(KEY) || '{}');

  const icon = (path) =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;

  const icons = {
    trigger: icon('<circle cx="12" cy="4.5" r="1.8" fill="currentColor" stroke="none"/><path d="M4 8.5c2.6.9 5.2 1.35 8 1.35s5.4-.45 8-1.35"/><path d="M12 9.85V21"/><path d="M8.2 21l1.6-6.4M15.8 21l-1.6-6.4"/><path d="M8.5 14.2c1.1.35 2.3.55 3.5.55s2.4-.2 3.5-.55"/>'),
    fontDown: icon('<path d="M4 19l4-13 4 13"/><path d="M5.2 15h5.6"/><path d="M15 19l3-8"/>'),
    fontUp: icon('<path d="M4 19l4-13 4 13"/><path d="M5.2 15h5.6"/><path d="M16.5 11v8"/><path d="M14 13h5"/>'),
    contrast: icon('<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 000 18z" fill="currentColor" stroke="none"/>'),
    grayscale: icon('<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>'),
    motion: icon('<path d="M4 12h4l2-6 4 12 2-6h4"/>'),
    focus: icon('<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>'),
    reset: icon('<path d="M3 12a9 9 0 109-9"/><path d="M3 4v5h5"/>'),
  };

  const apply = () => {
    document.documentElement.classList.toggle('a11y-large', state.font === 'large');
    document.documentElement.classList.toggle('a11y-xlarge', state.font === 'xlarge');
    document.body.classList.toggle('a11y-contrast', !!state.contrast);
    document.body.classList.toggle('a11y-grayscale', !!state.grayscale);
    document.body.classList.toggle('a11y-reduced-motion', !!state.motion);

    panel.querySelectorAll('button[data-action]').forEach(btn => {
      const action = btn.dataset.action;
      if (action === 'font-down' || action === 'font-up') {
        btn.disabled = action === 'font-down'
          ? !state.font || state.font === 'normal'
          : state.font === 'xlarge';
        return;
      }
      let active = false;
      if (action === 'contrast') active = !!state.contrast;
      if (action === 'grayscale') active = !!state.grayscale;
      if (action === 'motion') active = !!state.motion;
      if (action === 'focus') active = document.body.classList.contains('a11y-focus-helper');
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', String(active));
    });
  };
  const save = () => localStorage.setItem(KEY, JSON.stringify(state));

  const panel = document.createElement('div');
  panel.className = 'a11y-panel';
  panel.id = 'a11yPanel';
  panel.hidden = true;
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'false');
  panel.setAttribute('aria-labelledby', 'a11yTitle');
  panel.innerHTML = `
    <div class="a11y-panel-head">
      ${icons.trigger}
      <h2 id="a11yTitle">Modo de acessibilidade</h2>
    </div>
    <p>Ferramentas para melhorar a leitura e a navegação, seguindo as diretrizes do WCAG.</p>
    <div class="a11y-grid">
      <button type="button" data-action="font-down" aria-pressed="false" aria-label="Diminuir tamanho do texto">${icons.fontDown}<span>Diminuir texto</span></button>
      <button type="button" data-action="font-up" aria-pressed="false" aria-label="Aumentar tamanho do texto">${icons.fontUp}<span>Aumentar texto</span></button>
      <button type="button" data-action="contrast" aria-pressed="false">${icons.contrast}<span>Alto contraste</span></button>
      <button type="button" data-action="grayscale" aria-pressed="false">${icons.grayscale}<span>Escala de cinza</span></button>
      <button type="button" data-action="motion" aria-pressed="false">${icons.motion}<span>Reduzir movimento</span></button>
      <button type="button" data-action="focus" aria-pressed="false">${icons.focus}<span>Foco visível</span></button>
    </div>
    <button type="button" class="a11y-reset" data-action="reset">${icons.reset}<span>Restaurar padrão</span></button>
    <div class="a11y-status" id="a11yStatus" aria-live="polite"></div>`;

  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'a11y-trigger';
  trigger.id = 'a11yTrigger';
  trigger.setAttribute('aria-controls', 'a11yPanel');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-label', 'Abrir modo de acessibilidade');
  trigger.innerHTML = `${icons.trigger}<span>Acessibilidade</span>`;

  document.body.append(trigger, panel);
  apply();

  const status = msg => { document.getElementById('a11yStatus').textContent = msg; };
  trigger.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    trigger.setAttribute('aria-expanded', String(!panel.hidden));
    if (!panel.hidden) panel.querySelector('button')?.focus();
  });
  panel.addEventListener('click', e => {
    const action = e.target.closest('button')?.dataset.action;
    if (!action) return;
    if (action === 'font-up') state.font = state.font === 'large' ? 'xlarge' : 'large';
    if (action === 'font-down') state.font = state.font === 'xlarge' ? 'large' : 'normal';
    if (action === 'contrast') state.contrast = !state.contrast;
    if (action === 'grayscale') state.grayscale = !state.grayscale;
    if (action === 'motion') state.motion = !state.motion;
    if (action === 'focus') document.body.classList.toggle('a11y-focus-helper');
    if (action === 'reset') { Object.keys(state).forEach(k => delete state[k]); document.body.classList.remove('a11y-focus-helper'); }
    save(); apply(); status('Configuração atualizada.');
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !panel.hidden) {
      panel.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      trigger.focus();
    }
  });
})();
