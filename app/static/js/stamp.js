/* Basma Service — генератор оттиска печати (SVG) и конструктор заказа */
(() => {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let uid = 0;

  const T = window.BASMA_I18N || (() => { try { return JSON.parse(document.getElementById('i18n').textContent); } catch (_) { return {}; } })();
  const PREFIX = {
    ooo: T.prefixOoo || 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ',
    ip: T.prefixIp || 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ',
    doctor: T.prefixDoctor || 'ВРАЧ',
    stamp: '',
  };

  /** Подгоняет текст по пути: растягивает короткий, сжимает длинный. */
  const fitText = (svg) => {
    svg.querySelectorAll('[data-fit]').forEach((tp) => {
      const max = parseFloat(tp.dataset.fit);
      tp.removeAttribute('textLength');
      let natural = 0;
      try { natural = tp.getComputedTextLength(); } catch (_) { natural = 0; }
      if (!natural) { tp.setAttribute('textLength', max); return; }
      tp.setAttribute('textLength', Math.min(max, Math.max(natural, max * (tp.dataset.stretch ? 1 : 0))));
      tp.setAttribute('lengthAdjust', natural > max ? 'spacingAndGlyphs' : 'spacing');
    });
    svg.querySelectorAll('[data-fit-x]').forEach((t) => {
      const max = parseFloat(t.dataset.fitX);
      let w = 0;
      try { w = t.getComputedTextLength(); } catch (_) { w = 0; }
      if (w > max) { t.setAttribute('textLength', max); t.setAttribute('lengthAdjust', 'spacingAndGlyphs'); }
    });
  };

  const roundStamp = (o, id) => {
    const C = 2 * Math.PI * 80;
    const ring = [PREFIX[o.kind], o.org ? `«${o.org.toUpperCase()}»` : '', o.city ? `${o.city.toUpperCase()}` : '']
      .filter(Boolean).join(' ✦ ') + ' ✦';
    const centerTop = o.kind === 'doctor' ? T.personalSeal : T.country;
    const centerMain = (o.center || (o.kind === 'doctor' ? o.org : T.forDocs)).toUpperCase();
    return `
      <defs>
        <path id="r${id}" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/>
        <filter id="ink${id}" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="3"/>
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.2 1.4"/>
          <feComposite in="SourceGraphic" operator="in"/>
        </filter>
      </defs>
      <g filter="url(#ink${id})" fill="none" stroke="${o.ink}">
        <circle cx="100" cy="100" r="97" stroke-width="3.2"/>
        <circle cx="100" cy="100" r="92" stroke-width="1"/>
        <circle cx="100" cy="100" r="66" stroke-width="1.4"/>
        <circle cx="100" cy="100" r="62" stroke-width=".8" stroke-dasharray="1.5 2.5"/>
      </g>
      <g filter="url(#ink${id})" fill="${o.ink}" font-family="Manrope, Arial, sans-serif" font-weight="800">
        <text font-size="11.5" letter-spacing=".6"><textPath href="#r${id}" data-fit="${(C * 0.985).toFixed(1)}" data-stretch="1">${esc(ring)}</textPath></text>
        <text x="100" y="74" font-size="7" text-anchor="middle" letter-spacing=".5" data-fit-x="96">${esc(centerTop)}</text>
        <text x="100" y="104" font-size="${centerMain.length > 14 ? 10 : 13}" text-anchor="middle" data-fit-x="108">${esc(centerMain)}</text>
        ${o.inn ? `<text x="100" y="130" font-size="8.5" text-anchor="middle" letter-spacing=".4" data-fit-x="100">${esc(T.inn)} ${esc(o.inn)}</text>` : ''}
        <text x="100" y="146" font-size="9" text-anchor="middle">✦</text>
      </g>`;
  };

  const boxStamp = (o, id, rect) => {
    const w = rect ? 200 : 170;
    const h = rect ? 92 : 170;
    const x0 = (200 - w) / 2;
    const y0 = (200 - h) / 2;
    const lines = [];
    if (PREFIX[o.kind] && o.kind !== 'stamp') lines.push([PREFIX[o.kind], 7.5]);
    if (o.org) lines.push([o.kind === 'stamp' ? o.org.toUpperCase() : `«${o.org.toUpperCase()}»`, rect ? 14 : 15]);
    if (o.center) lines.push([o.center.toUpperCase(), rect ? 10 : 11]);
    if (o.inn) lines.push([`${T.inn} ${o.inn}`, 9]);
    if (o.city) lines.push([o.city.toUpperCase(), 8.5]);
    const gap = 6;
    const total = lines.reduce((s, [, fs]) => s + fs + gap, -gap);
    let y = 100 - total / 2;
    const texts = lines.map(([t, fs]) => {
      y += fs;
      const el = `<text x="100" y="${(y - fs * 0.15).toFixed(1)}" font-size="${fs}" text-anchor="middle" data-fit-x="${w - 22}">${esc(t)}</text>`;
      y += gap;
      return el;
    }).join('');
    return `
      <defs>
        <filter id="ink${id}" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="5"/>
          <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.25"/>
          <feComposite in="SourceGraphic" operator="in"/>
        </filter>
      </defs>
      <g filter="url(#ink${id})" fill="none" stroke="${o.ink}">
        <rect x="${x0}" y="${y0}" width="${w}" height="${h}" rx="6" stroke-width="3.2"/>
        <rect x="${x0 + 5}" y="${y0 + 5}" width="${w - 10}" height="${h - 10}" rx="3" stroke-width="1"/>
      </g>
      <g filter="url(#ink${id})" fill="${o.ink}" font-family="Manrope, Arial, sans-serif" font-weight="800">${texts}</g>`;
  };

  /** Рисует оттиск в контейнер. opts: kind, shape, org, inn, city, center, ink */
  const render = (container, opts) => {
    const o = Object.assign({ kind: 'ooo', shape: 'round', org: '', inn: '', city: '', center: '', ink: '#1f3fbf' }, opts);
    const id = ++uid;
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 200 200');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', T.previewLabel);
    svg.innerHTML = o.shape === 'round' ? roundStamp(o, id) : boxStamp(o, id, o.shape === 'rect');
    container.replaceChildren(svg);
    fitText(svg);
    return svg;
  };

  window.BasmaStamp = { render };

  const ready = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();

  /* ---------- Демо на главной ---------- */
  const demo = document.querySelector('[data-stamp-demo]');
  const demoInput = document.querySelector('[data-stamp-demo-input]');
  if (demo && demoInput) {
    const draw = () => render(demo, { org: demoInput.value || T.yourCompany, inn: '01234567890123', city: T.demoCity, ink: '#1f3fbf' });
    ready.then(draw);
    demoInput.addEventListener('input', draw);
  }

  /* ---------- Конструктор ---------- */
  const form = document.querySelector('[data-builder]');
  if (!form) return;

  const dataEl = document.getElementById('holders-data');
  const holders = dataEl ? JSON.parse(dataEl.textContent) : [];
  const stage = form.querySelector('[data-b-stage]');
  const holdersBox = form.querySelector('[data-b-holders]');
  const totalEl = form.querySelector('[data-b-total]');
  const totalInput = form.querySelector('[data-b-total-input]');
  const termEl = form.querySelector('[data-b-term]');
  const qtyInput = form.querySelector('[data-b-qty]');
  const urgent = form.querySelector('[data-b-urgent]');
  const subject = form.querySelector('[data-b-subject]');
  const preselect = new URLSearchParams(location.search).get('holder');
  const money = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(n)) + ' ' + T.som;

  const state = () => {
    const kindEl = form.querySelector('[name=d_kind]:checked');
    const shapeEl = form.querySelector('[name=d_shape]:checked');
    const inkEl = form.querySelector('[name=d_ink]:checked');
    const v = (k) => (form.querySelector(`[data-b="${k}"]`).value || '').trim();
    return {
      kind: kindEl.dataset.kind,
      shape: shapeEl.dataset.shape,
      ink: inkEl.dataset.ink,
      org: v('org'), inn: v('inn'), city: v('city'), center: v('center'),
    };
  };

  const renderHolders = (shape) => {
    const list = holders.filter((h) => !h.shape || h.shape === shape);
    const checked = form.querySelector('[name=product]:checked');
    const keep = checked ? checked.value : preselect;
    holdersBox.innerHTML = list.map((h) => `
      <label class="option holder">
        <input type="radio" name="product" value="${h.id}" data-price="${h.price ?? ''}" data-name="${esc(h.name)}">
        <span class="option__box">
          ${h.image ? `<img src="${esc(h.image)}" alt="" loading="lazy">` : ''}
          <b>${esc(h.name)}</b>
          <small>${esc([h.category, h.size].filter(Boolean).join(' · '))}</small>
          <span class="holder__price">${h.price != null ? money(h.price) : T.onRequest}</span>
        </span>
      </label>`).join('') + `
      <label class="option holder">
        <input type="radio" name="product" value="" data-price="" data-name="Подобрать с менеджером">
        <span class="option__box"><b>${esc(T.pickForMe)}</b><small>${esc(T.pickForMeHint)}</small></span>
      </label>`;
    const target = holdersBox.querySelector(`[name=product][value="${keep}"]`) || holdersBox.querySelector('[name=product]');
    if (target) target.checked = true;
  };

  const update = (animate) => {
    const s = state();
    render(stage, s);
    if (animate) { stage.classList.remove('is-stamp'); void stage.offsetWidth; stage.classList.add('is-stamp'); }

    const h = form.querySelector('[name=product]:checked');
    const qty = Math.max(1, Math.min(99, parseInt(qtyInput.value, 10) || 1));
    const price = h && h.dataset.price ? parseFloat(h.dataset.price) : null;
    if (price != null) {
      const total = price * qty * (urgent.checked ? 1.3 : 1);
      totalEl.textContent = money(total);
      totalInput.value = money(total);
    } else {
      totalEl.textContent = T.onRequest;
      totalInput.value = '';
    }
    termEl.textContent = urgent.checked ? T.oneHour : T.fromHour;
    const kindLabel = form.querySelector('[name=d_kind]:checked').value;
    subject.value = `Конструктор: ${kindLabel}${s.org ? ' «' + s.org + '»' : ''}${h && h.dataset.name ? ' — ' + h.dataset.name : ''}`;

    form.querySelector('[data-b-org-label]').textContent = s.kind === 'doctor' ? T.lblDoctor : s.kind === 'ip' ? T.lblIp : s.kind === 'stamp' ? T.lblStamp : T.lblOrg;
    form.querySelector('[data-b-inn-label]').textContent = s.kind === 'doctor' ? T.lblDoctorInn : T.lblInn;
  };

  form.addEventListener('input', (e) => { if (e.target.matches('[data-b], [data-b-qty]')) update(false); });
  form.addEventListener('change', (e) => {
    if (e.target.name === 'd_kind') {
      const kind = e.target.dataset.kind;
      const shape = kind === 'stamp' ? 'rect' : 'round';
      form.querySelector(`[name=d_shape][data-shape="${shape}"]`).checked = true;
      renderHolders(shape);
    }
    if (e.target.name === 'd_shape') renderHolders(e.target.dataset.shape);
    if (['d_kind', 'd_shape', 'd_ink', 'product', 'd_urgent'].includes(e.target.name)) update(true);
  });
  form.querySelectorAll('[data-qty]').forEach((b) => b.addEventListener('click', () => {
    qtyInput.value = Math.max(1, Math.min(99, (parseInt(qtyInput.value, 10) || 1) + parseInt(b.dataset.qty, 10)));
    update(false);
  }));

  form.addEventListener('lead:sent', () => {
    form.style.display = 'none';
    const ok = document.querySelector('[data-builder-success]');
    ok.style.display = 'block';
    ok.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  // Если пришли со страницы товара — выбираем его форму
  const pre = holders.find((h) => String(h.id) === preselect);
  if (pre && pre.shape) form.querySelector(`[name=d_shape][data-shape="${pre.shape}"]`).checked = true;
  renderHolders(form.querySelector('[name=d_shape]:checked').dataset.shape);
  ready.then(() => update(false));
})();
