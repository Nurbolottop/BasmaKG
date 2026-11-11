/* Basma Service — основной скрипт (без зависимостей) */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const T = (() => { try { return JSON.parse(document.getElementById('i18n').textContent); } catch (_) { return {}; } })();
  window.BASMA_I18N = T;

  /* ---------- Toasts ---------- */
  const toasts = $('#toasts');
  const toast = (text, type = '') => {
    const el = document.createElement('div');
    el.className = `toast${type ? ' toast--' + type : ''}`;
    el.textContent = text;
    toasts.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  };
  $$('.toast', toasts).forEach((el) => setTimeout(() => el.remove(), 6000));

  /* ---------- Header shadow ---------- */
  const header = $('#header');
  const onScroll = () => header && header.classList.toggle('is-scrolled', window.scrollY > 8);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  const menu = $('#mobile-menu');
  const burger = $('[data-menu-open]');
  const setMenu = (open) => {
    if (!menu) return;
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', String(!open));
    burger && burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  };
  burger && burger.addEventListener('click', () => setMenu(true));
  $$('[data-menu-close]').forEach((b) => b.addEventListener('click', () => setMenu(false)));
  menu && $$('a', menu).forEach((a) => a.addEventListener('click', () => setMenu(false)));

  /* ---------- Modal ---------- */
  const modal = $('#lead-modal');
  let lastFocus = null;
  const openModal = (opts = {}) => {
    if (!modal) return;
    const card = $('[data-form-card]', modal);
    const form = $('form', modal);
    card.classList.remove('is-sent');
    form.reset();
    clearErrors(form);
    $('[data-modal-title]', modal).textContent = opts.title || (opts.type === 'order' ? T.orderTitle : T.leadTitle);
    form.querySelector('[name=type]').value = opts.type || 'callback';
    form.querySelector('[name=subject]').value = opts.subject || '';
    let product = form.querySelector('[name=product]');
    if (opts.product) {
      if (!product) {
        product = Object.assign(document.createElement('input'), { type: 'hidden', name: 'product' });
        form.appendChild(product);
      }
      product.value = opts.product;
    } else if (product) {
      product.remove();
    }
    lastFocus = document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    setTimeout(() => form.querySelector('[name=name]').focus(), 120);
  };
  const closeModal = () => {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    lastFocus && lastFocus.focus();
  };
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-modal-open]');
    if (opener) {
      e.preventDefault();
      openModal({
        type: opener.dataset.type,
        subject: opener.dataset.subject,
        product: opener.dataset.product,
        title: opener.dataset.title,
      });
      fab && fab.classList.remove('is-open');
    }
    if (e.target.closest('[data-modal-close]')) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { closeModal(); setMenu(false); }
  });

  /* ---------- FAB ---------- */
  const fab = $('[data-fab]');
  if (fab) {
    const t = $('[data-fab-toggle]', fab);
    t.addEventListener('click', () => {
      const open = fab.classList.toggle('is-open');
      t.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', (e) => { if (!fab.contains(e.target)) fab.classList.remove('is-open'); });
  }

  /* ---------- Phone mask (+996 XXX XXX XXX) ---------- */
  const formatPhone = (value) => {
    let d = value.replace(/\D/g, '');
    if (d.startsWith('0')) d = '996' + d.slice(1);
    if (!d.startsWith('996')) d = '996' + d;
    d = d.slice(0, 12);
    const p = [d.slice(3, 6), d.slice(6, 9), d.slice(9, 12)].filter(Boolean);
    return '+996' + (p.length ? ' ' + p.join(' ') : ' ');
  };
  document.addEventListener('focusin', (e) => {
    if (e.target.matches('[data-phone]') && !e.target.value) e.target.value = '+996 ';
  });
  document.addEventListener('input', (e) => {
    if (e.target.matches('[data-phone]')) e.target.value = formatPhone(e.target.value);
  });
  document.addEventListener('focusout', (e) => {
    if (e.target.matches('[data-phone]') && e.target.value.replace(/\D/g, '').length <= 3) e.target.value = '';
  });

  /* ---------- File drop ---------- */
  $$('[data-file-drop]').forEach((drop) => {
    const input = $('input[type=file]', drop);
    const name = $('[data-file-name]', drop);
    const initial = name.textContent;
    input.addEventListener('change', () => {
      name.textContent = input.files[0] ? input.files[0].name : initial;
    });
    ['dragenter', 'dragover'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('is-drag'); }));
    ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove('is-drag')));
    drop.addEventListener('drop', (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event('change'));
      }
    });
  });

  /* ---------- Lead forms (AJAX) ---------- */
  function clearErrors(form) {
    $$('.field__error', form).forEach((el) => el.remove());
    $$('.has-error', form).forEach((el) => el.classList.remove('has-error'));
  }
  const showErrors = (form, errors) => {
    let general = [];
    Object.entries(errors).forEach(([field, msgs]) => {
      const input = form.querySelector(`[name="${field}"]`);
      const wrap = input && input.closest('.field');
      if (wrap) {
        wrap.classList.add('has-error');
        const err = document.createElement('span');
        err.className = 'field__error';
        err.textContent = msgs[0];
        wrap.appendChild(err);
      } else {
        general = general.concat(msgs);
      }
    });
    general.filter((m) => m !== 'spam').forEach((m) => toast(m, 'error'));
    const first = form.querySelector('.has-error input, .has-error textarea');
    first && first.focus();
  };

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('[data-lead-form]');
    if (!form) return;
    e.preventDefault();
    clearErrors(form);

    const name = form.querySelector('[name=name]');
    const phone = form.querySelector('[name=phone]');
    const local = {};
    if (!name.value.trim()) local.name = [T.errName];
    if (phone.value.replace(/\D/g, '').length < 12) local.phone = [T.errPhone];
    const agree = form.querySelector('[name=agree]');
    if (agree && !agree.checked) local.agree = [T.errAgree];
    if (Object.keys(local).length) return showErrors(form, local);

    const btn = form.querySelector('[type=submit]');
    const btnHtml = btn.innerHTML;
    btn.disabled = true;
    btn.textContent = T.sending;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.ok) {
        form.dispatchEvent(new CustomEvent('lead:sent', { bubbles: true, detail: data }));
        const card = form.closest('[data-form-card]');
        if (card) card.classList.add('is-sent');
        else toast(T.sent);
        form.reset();
        $$('[data-file-name]', form).forEach((n) => (n.textContent = T.fileAttached));
        if (window.ym && window.YM_ID) window.ym(window.YM_ID, 'reachGoal', 'lead');
        if (window.gtag) window.gtag('event', 'generate_lead');
      } else {
        showErrors(form, data.errors || { __all__: [T.sendFailed] });
      }
    } catch (err) {
      toast(T.offline, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = btnHtml;
    }
  });

  /* ---------- Reveal on scroll ---------- */
  const io = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 })
    : null;
  const observe = (root = document) => $$('.reveal:not(.is-in)', root).forEach((el) => (io ? io.observe(el) : el.classList.add('is-in')));
  observe();

  /* ---------- Hero seal: «поставить печать» ---------- */
  const seal = $('[data-seal]');
  if (seal) {
    const stamp = (x, y) => {
      seal.classList.remove('is-stamping');
      void seal.offsetWidth;
      seal.classList.add('is-stamping');
      const img = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      img.setAttribute('viewBox', '0 0 200 200');
      img.classList.add('imprint');
      img.style.left = x + 'px';
      img.style.top = y + 'px';
      img.innerHTML = '<defs><path id="imp" d="M100,100 m-72,0 a72,72 0 1,1 144,0 a72,72 0 1,1 -144,0"/>'
        + '<filter id="ink"><feTurbulence baseFrequency=".9" numOctaves="2"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter></defs>'
        + '<g fill="none" stroke="#2340c9" filter="url(#ink)" opacity=".85"><circle cx="100" cy="100" r="94" stroke-width="4"/><circle cx="100" cy="100" r="86" stroke-width="1.5"/><circle cx="100" cy="100" r="52" stroke-width="2"/></g>'
        + '<g fill="#2340c9" filter="url(#ink)" opacity=".85" font-family="Unbounded, sans-serif" font-weight="700">'
        + '<text font-size="15" letter-spacing="3"><textPath href="#imp" textLength="440">BASMA SERVICE ✦ ' + T.impDone + ' ✦ ' + T.impCity + ' ✦</textPath></text>'
        + '<text x="100" y="98" font-size="18" text-anchor="middle">' + T.impStamp + '</text><text x="100" y="118" font-size="11" text-anchor="middle">' + T.impHour + '</text></g>';
      document.body.appendChild(img);
      setTimeout(() => img.remove(), 1700);
    };
    seal.addEventListener('click', (e) => stamp(e.clientX, e.clientY));
    seal.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const r = seal.getBoundingClientRect();
        stamp(r.left + r.width / 2, r.top + r.height / 2);
      }
    });
  }

  /* ---------- Catalog: фильтр и поиск без перезагрузки ---------- */
  const catForm = $('[data-catalog-form]');
  const grid = $('[data-catalog-grid]');
  if (catForm && grid) {
    let timer;
    const load = async (url, push = true) => {
      grid.classList.add('loading');
      try {
        const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        grid.innerHTML = await res.text();
        observe(grid);
        if (push) history.replaceState(null, '', url);
      } catch (_) {
        window.location.href = url;
      } finally {
        grid.classList.remove('loading');
      }
    };
    const submit = () => {
      const params = new URLSearchParams(new FormData(catForm));
      if (!params.get('q')) params.delete('q');
      if (params.get('sort') === 'popular') params.delete('sort');
      const qs = params.toString();
      load(window.location.pathname + (qs ? '?' + qs : ''));
    };
    catForm.addEventListener('submit', (e) => { e.preventDefault(); submit(); });
    $('[name=q]', catForm).addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(submit, 350); });
    $('[data-autosubmit]', catForm).addEventListener('change', submit);
    grid.addEventListener('click', (e) => {
      const a = e.target.closest('.pagination a');
      if (a) { e.preventDefault(); load(a.href); grid.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  }

  /* ---------- Product gallery ---------- */
  const gallery = $('[data-gallery]');
  if (gallery) {
    const main = $('[data-gallery-main]', gallery);
    $$('.gallery__thumb', gallery).forEach((t) => t.addEventListener('click', () => {
      $$('.gallery__thumb', gallery).forEach((x) => x.classList.remove('is-active'));
      t.classList.add('is-active');
      if (main) main.src = t.dataset.src;
    }));
  }

  /* ---------- SEO-текст: «Читать полностью» ---------- */
  $$('[data-seo-text]').forEach((box) => {
    const btn = $('[data-seo-toggle]', box);
    const body = $('.seo-text__body', box);
    if (body.scrollHeight <= body.clientHeight + 20) { box.classList.add('is-open'); btn.remove(); return; }
    btn.addEventListener('click', () => {
      const open = box.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  /* ---------- FAQ: открыт только один ---------- */
  $$('.faq').forEach((faq) => {
    $$('details', faq).forEach((d) => d.addEventListener('toggle', () => {
      if (d.open) $$('details', faq).forEach((o) => o !== d && (o.open = false));
    }));
  });
})();
