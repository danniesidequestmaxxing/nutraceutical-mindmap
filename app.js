const app = document.getElementById('app');
const qInput = document.getElementById('q');
const goBtn = document.getElementById('go');
const libSel = document.getElementById('lib');
const prog = document.getElementById('prog');
const progBar = document.getElementById('progbar');
const progMsg = document.getElementById('progmsg');
const titleEl = document.getElementById('title');
const legendEl = document.getElementById('legend');
const metaEl = document.getElementById('meta');

function render(queryData) {
  const stages = queryData.stages || [];
  const companies = queryData.companies || [];
  const byStage = {};
  stages.forEach(s => { byStage[s.id] = s; });

  titleEl.textContent = queryData.query || 'Supply Chain Mindmap';
  document.title = (queryData.query || 'Supply Chain Mindmap') + ' — Mindmap';

  // Legend
  const stageCounts = {};
  companies.forEach(g => {
    stageCounts[g.s] = (stageCounts[g.s] || 0) + (g.cs || []).length;
  });
  legendEl.innerHTML = stages.map(s => {
    const dotColor = getComputedStyle(document.documentElement).getPropertyValue('--' + s.c + '-dot') || '';
    return `<div class="li ${s.c}"><div class="ld"></div>${s.n} (${stageCounts[s.id] || 0})</div>`;
  }).join('');

  // Meta line
  if (queryData.meta) {
    const m = queryData.meta;
    const parts = [];
    if (m.n_candidates) parts.push(m.n_candidates + ' candidates');
    if (m.cost_usd != null) parts.push('$' + m.cost_usd.toFixed(2));
    if (m.elapsed_s != null) parts.push(m.elapsed_s + 's');
    metaEl.textContent = parts.join(' · ');
  } else {
    metaEl.textContent = '';
  }

  // Group by stage
  const groupsByStage = {};
  companies.forEach(g => {
    (groupsByStage[g.s] = groupsByStage[g.s] || []).push(g);
  });

  let html = '';
  stages.forEach((s, idx) => {
    const groups = groupsByStage[s.id] || [];
    const cnt = (stageCounts[s.id] || 0);
    html += `<div class="stg ${s.c}" id="stg${s.id}">
<div class="sh" onclick="tg('stg${s.id}')">
<div class="sn">${idx + 1}</div><div class="sl">${esc(s.n)}</div><div class="st">${esc(s.t || '')}</div>
<div class="badge">${cnt}</div>
<svg class="chv" viewBox="0 0 16 16"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
</div><div class="sb" id="sb-stg${s.id}">`;
    groups.forEach((grp, gi) => {
      if (grp.g) html += `<div class="grp"><div class="gl">${esc(grp.g)}</div>`;
      else html += `<div class="grp">`;
      (grp.cs || []).forEach((co, ci) => {
        const id = `c${s.id}_${gi}_${ci}`;
        const certs = co.c && co.c.length ? co.c.map(c => `<span class="tag">${esc(c)}</span>`).join('') : '';
        const loc = co.l ? ` (${esc(co.l)})` : '';
        const web = co.w ? `<a class="lnk" href="${co.w.startsWith('http') ? co.w : 'https://' + co.w}" target="_blank" rel="noopener">${esc(co.w.replace(/^https?:\/\//, ''))}</a>` : '';
        const secLabel = co.x && byStage[co.x] ? byStage[co.x].n : (co.x || '');
        const sec = co.x ? `<div class="sec">Also operates in: ${esc(secLabel)}</div>` : '';
        html += `<div class="co"><div class="ch" onclick="tc('${id}')">
<div class="cd"></div><div class="cn">${esc(co.n)}${loc}</div>
<svg class="cx" viewBox="0 0 16 16"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
</div><div class="det" id="${id}">
<div class="dd">${esc(co.d || 'No description available.')}</div>
${certs ? '<div class="tags">' + certs + '</div>' : ''}
${web}${sec}
</div></div>`;
      });
      html += '</div>';
    });
    html += `</div></div>`;
    if (idx < stages.length - 1) html += '<div class="conn"></div>';
  });
  app.innerHTML = html;
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function tg(id) {
  document.getElementById('sb-' + id).classList.toggle('o');
  document.querySelector('#' + id + ' .chv').classList.toggle('o');
}
function tc(id) {
  document.getElementById(id).classList.toggle('o');
  const svg = document.querySelector(`[onclick="tc('${id}')"] .cx`);
  if (svg) svg.classList.toggle('o');
}
window.tg = tg;
window.tc = tc;

async function loadLibrary() {
  try {
    const r = await fetch('/api/queries');
    if (!r.ok) return;
    const items = await r.json();
    libSel.innerHTML = '<option value="">— past queries —</option>' +
      items.map(i => `<option value="${esc(i.slug)}">${esc(i.query)} (${i.n_companies})</option>`).join('');
  } catch (e) { /* offline or no backend */ }
}

async function loadSlug(slug) {
  const r = await fetch('/api/queries/' + encodeURIComponent(slug));
  if (!r.ok) throw new Error('Not found');
  const doc = await r.json();
  render(doc);
  history.replaceState(null, '', '?q=' + encodeURIComponent(slug));
}

function setProgress(pct, msg) {
  prog.classList.add('show');
  progBar.style.width = pct + '%';
  progMsg.textContent = msg;
}
function hideProgress() {
  setTimeout(() => prog.classList.remove('show'), 500);
}

async function startResearch() {
  const query = qInput.value.trim();
  if (query.length < 3) return;
  goBtn.disabled = true;
  setProgress(2, 'Starting…');
  try {
    const r = await fetch('/api/research', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: r.statusText }));
      throw new Error(err.detail || 'Request failed');
    }
    const { slug } = await r.json();
    const es = new EventSource('/api/research/' + encodeURIComponent(slug) + '/stream');
    es.onmessage = async (ev) => {
      try {
        const evt = JSON.parse(ev.data);
        setProgress(evt.pct || 0, evt.msg || evt.phase);
        if (evt.phase === 'complete' || evt.phase === 'done') {
          es.close();
          await loadSlug(slug);
          await loadLibrary();
          hideProgress();
        } else if (evt.phase === 'error') {
          es.close();
          setProgress(100, 'Error: ' + evt.msg);
          setTimeout(() => prog.classList.remove('show'), 4000);
        }
      } catch (e) { /* ignore */ }
    };
    es.onerror = () => { es.close(); };
  } catch (e) {
    setProgress(100, 'Error: ' + e.message);
    setTimeout(() => prog.classList.remove('show'), 4000);
  } finally {
    goBtn.disabled = false;
  }
}

if (goBtn) {
  goBtn.addEventListener('click', startResearch);
  qInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') startResearch(); });
  libSel.addEventListener('change', (e) => { if (e.target.value) loadSlug(e.target.value); });
}

async function bootstrap() {
  const params = new URLSearchParams(location.search);
  const slug = params.get('q');
  await loadLibrary();
  try {
    if (slug) await loadSlug(slug);
    else await loadSlug('malaysia-nutraceutical');
  } catch (e) {
    // Fallback to bundled data.js globals if the backend isn't reachable
    if (typeof D !== 'undefined' && typeof stageLabels !== 'undefined') {
      const stages = Object.keys(stageLabels).map(k => ({
        id: k, n: stageLabels[k].n, t: stageLabels[k].t, c: stageLabels[k].c,
      }));
      render({
        query: 'Malaysia Nutraceutical Supply Chain',
        stages, companies: D, meta: null,
      });
    } else {
      app.innerHTML = '<p style="color:var(--tx2);font-size:13px;padding:20px;text-align:center">No data loaded. Try a search above.</p>';
    }
  }
}

bootstrap();
