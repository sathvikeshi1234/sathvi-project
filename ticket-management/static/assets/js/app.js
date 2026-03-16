const state = {
  stats: null,
  rows: []
};

function el(html){
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function renderStats(){
  const wrap = document.querySelector('#stats');
  if(!wrap) return;
  wrap.innerHTML = '';
  const s = state.stats || { total_tickets: 0, open_tickets: 0, resolved_today: 0, distribution: { open:0, in_progress:0, resolved:0 } };
  const cards = [
    { label: 'Open Tickets', value: s.open_tickets || (s.distribution?.open||0), badge: 'teal' },
    { label: 'In Progress', value: s.distribution?.in_progress || 0, badge: 'amber' },
    { label: 'Resolved', value: s.distribution?.resolved || 0, badge: 'green' },
    { label: 'Total', value: s.total_tickets || 0, badge: 'sky' }
  ];
  cards.forEach(c => {
    const node = el(`<div class="panel stat"><div class="label">${c.label}</div><div class="value"><div class="badge ${c.badge}">${c.label.slice(0,1)}</div><div class="num">${c.value}</div></div></div>`);
    wrap.appendChild(node);
  });
}

function statusClass(s){
  const k = String(s||'').toLowerCase().replace(/\s+/g,'-');
  return ['status', k].join(' ');
}

function renderTable(){
  const body = document.querySelector('#tbody');
  if(!body) return;
  body.innerHTML = '';
  state.rows.forEach(r => {
    const tr = el(`<tr>
      <td>${r.id}</td>
      <td>${r.subject}</td>
      <td><span class="${statusClass(r.status)}">${r.status}</span></td>
      <td><div class="bar" style="--value:${r.sla||0}%;"><span></span></div></td>
    </tr>`);
    body.appendChild(tr);
  });
}

function initSidebarToggle(){
  const btn = document.querySelector('#menu');
  const aside = document.querySelector('aside.sidebar');
  if(btn && aside){ btn.addEventListener('click', ()=> aside.classList.toggle('open')); }
}

function switchView(target){
  const views = ['overview','tickets','messages','profile','settings'];
  views.forEach(v => {
    const el = document.querySelector(`#view-${v}`);
    if(!el) return;
    el.classList.toggle('hidden', v !== target);
  });
}

function setupNav(){
  const map = { Overview:'overview', Tickets:'tickets', Messages:'messages', Profile:'profile', Settings:'settings' };
  document.querySelectorAll('nav.nav a[href="#"]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      document.querySelectorAll('nav.nav a').forEach(n => n.classList.remove('active'));
      a.classList.add('active');
      const name = a.textContent.trim();
      switchView(map[name] || 'overview');
    });
  });
}

function setupTicketForm(){
  const form = document.querySelector('#ticket-form');
  const tbody = document.querySelector('#tickets-body');
  const filter = document.querySelector('#filterStatus');
  function redraw(){
    if(!tbody) return;
    tbody.innerHTML = '';
    const items = state.rows.filter(r => filter && (filter.value === 'all' || r.status === filter.value) || !filter);
    items.forEach(r => {
      const tr = el(`<tr>
        <td>${r.id}</td>
        <td>${r.subject}</td>
        <td><span class="${statusClass(r.status)}">${r.status}</span></td>
        <td><div class="bar" style="--value:${r.sla||0}%;"><span></span></div></td>
      </tr>`);
        tbody.appendChild(tr);
    });
  }
  if(filter){ filter.addEventListener('change', redraw); }
  if(form){
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const subject = document.querySelector('#tSubject')?.value?.trim();
      const category = document.querySelector('#tCategory')?.value;
      const desc = document.querySelector('#tDesc')?.value?.trim();
      if(!subject) return;
      try{
        const payload = { title: subject, category, description: desc, priority: 'Medium', status: 'Open', customer_username: (window.CURRENT_USER||'').trim() };
        const res = await fetch('/tickets/api/tickets/',{ method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(payload) });
        if(!res.ok) throw new Error('Create failed');
        await loadMyTickets();
        if(document.querySelector('#tSubject')) document.querySelector('#tSubject').value = '';
        if(document.querySelector('#tDesc')) document.querySelector('#tDesc').value = '';
        redraw();
        renderTable();
        renderStats();
      }catch(err){ console.error(err); alert('Could not submit ticket.'); }
    });
  }
  redraw();
}

function setupMessages(){
  // remains demo unless backend provided
}

async function loadStats(){
  try{
    const res = await fetch('/tickets/dashboard/stats/');
    if(!res.ok) throw new Error('stats failed');
    state.stats = await res.json();
  }catch(e){ console.warn('stats load error', e); state.stats = null; }
}

async function loadMyTickets(){
  try{
    const res = await fetch('/tickets/api/tickets/');
    if(!res.ok) throw new Error('tickets failed');
    const data = await res.json();
    const me = (window.CURRENT_USER||'').toLowerCase();
    const mine = me ? data.filter(t => String(t.created_by_username||'').toLowerCase() === me) : data;
    state.rows = mine.map(t => ({ id: t.ticket_id || `#${t.id}`, subject: t.title, status: t.status, sla: 0 }));
  }catch(e){ console.warn('ticket load error', e); state.rows = []; }
}

async function init(){
  await Promise.all([loadStats(), loadMyTickets()]);
  renderStats();
  renderTable();
  initSidebarToggle();
  setupNav();
  setupTicketForm();
  if (document.querySelector('#view-messages')) { setupMessages(); }
  switchView('overview');

  // Avatar dropdown
  const avatarBtn = document.querySelector('#avatarBtn');
  const dropdown = document.querySelector('#userDropdown');
  const ddName = document.querySelector('#ddName');
  const ddRole = document.querySelector('#ddRole');
  if(ddName) ddName.textContent = (window.CURRENT_USER || 'User');
  if(ddRole) ddRole.textContent = 'Member';
  if(avatarBtn){
    avatarBtn.addEventListener('click', (e)=>{ e.stopPropagation(); dropdown && dropdown.classList.toggle('hidden'); });
    document.addEventListener('click', (e)=>{ if(dropdown && !dropdown.contains(e.target) && e.target !== avatarBtn){ dropdown.classList.add('hidden'); } });
  }
}

document.addEventListener('DOMContentLoaded', init);
