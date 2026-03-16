const state = {
  stats: null,   // will load from /tickets/dashboard/stats/
  rows: []       // will load current user's tickets from /tickets/api/tickets/
};

function el(html) {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function renderStats() {
  const wrap = document.querySelector('#stats');
  if (!wrap) return;
  wrap.innerHTML = '';
  const s = state.stats || { total_tickets: 0, open_tickets: 0, resolved_today: 0, distribution: { open: 0, in_progress: 0, resolved: 0 } };
  const cards = [
    { label: 'Open Tickets', value: s.open_tickets || (s.distribution?.open || 0), badge: 'teal' },
    { label: 'In Progress', value: s.distribution?.in_progress || 0, badge: 'amber' },
    { label: 'Resolved', value: s.distribution?.resolved || 0, badge: 'green' },
    { label: 'Total', value: s.total_tickets || 0, badge: 'sky' }
  ];
  cards.forEach(c => {
    const node = el(`<div class="panel stat"><div class="label">${c.label}</div><div class="value"><div class="badge ${c.badge}">${c.label.slice(0, 1)}</div><div class="num">${c.value}</div></div></div>`);
    wrap.appendChild(node);
  });
}

function statusClass(s) {
  const k = s.toLowerCase().replace(/\s+/g, '-');
  return ['status', k].join(' ');
}

function renderTable() {
  const body = document.querySelector('#tbody');
  if (!body) return;
  body.innerHTML = '';
  state.rows.forEach(r => {
    const tr = el(`<tr>
      <td>${r.id}</td>
      <td>${r.subject}</td>
      <td><span class="${statusClass(r.status)}">${r.status}</span></td>
      <td><div class="bar" style="--value:${r.sla || 0}%;"><span></span></div></td>
    </tr>`);
    body.appendChild(tr);
  });
}

function initSidebarToggle() {
  const btn = document.querySelector('#menu');
  const aside = document.querySelector('aside.sidebar');
  
  // Only add event listeners if both elements exist
  if (btn && aside) {
    btn.addEventListener('click', () => aside.classList.toggle('open'));
  }
}

function switchView(target) {
  const views = ['overview', 'tickets', 'messages', 'profile', 'settings'];
  views.forEach(v => {
    const el = document.querySelector(`#view-${v}`);
    if (!el) return;
    el.classList.toggle('hidden', v !== target);
  });
}

function setupNav() {
  const map = {
    Overview: 'overview',
    Tickets: 'tickets',
    Messages: 'messages',
    Profile: 'profile',
    Settings: 'settings'
  };
  // Only intercept in-page anchors (href="#"). Real links like tickets.html should navigate normally.
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

function setupTicketForm() {
  const form = document.querySelector('#ticket-form');
  const tbody = document.querySelector('#tickets-body');
  const filter = document.querySelector('#filterStatus');
  function redraw() {
    tbody.innerHTML = '';
    const items = state.rows.filter(r => filter.value === 'all' || r.status === filter.value);
    items.forEach(r => {
      const tr = el(`<tr>
        <td>${r.id}</td>
        <td>${r.subject}</td>
        <td><span class="${statusClass(r.status)}">${r.status}</span></td>
        <td><div class="bar" style="--value:${r.sla || 0}%;"><span></span></div></td>
      </tr>`);
      tbody.appendChild(tr);
    });
  }
  filter.addEventListener('change', redraw);
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const subject = document.querySelector('#tSubject').value.trim();
    const category = document.querySelector('#tCategory').value;
    const desc = document.querySelector('#tDesc').value.trim();
    if (!subject) return;
    try {
      const payload = { title: subject, category, description: desc, priority: 'Medium', status: 'Open', customer_username: (window.CURRENT_USER || '').trim() };
      const res = await fetch('/tickets/api/tickets/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error('Create failed');
      // reload list
      await loadMyTickets();
      document.querySelector('#tSubject').value = '';
      document.querySelector('#tDesc').value = '';
      redraw();
      renderTable();
      renderStats();
    } catch (err) { console.error(err); alert('Could not submit ticket.'); }
  });
  redraw();
}

function setupMessages() {
  const threads = [
    {
      id: 'th1', title: 'Ticket #TCK-1043', msgs: [
        { who: 'them', text: 'Hello! We are looking into your password reset issue.' },
        { who: 'me', text: 'Thanks, awaiting update.' }
      ]
    },
    {
      id: 'th2', title: 'General Inquiry', msgs: [
        { who: 'them', text: 'How can we help you today?' }
      ]
    }
  ];
  const list = document.querySelector('#thread-list');
  const chat = document.querySelector('#chat');
  const title = document.querySelector('#thread-title');
  const form = document.querySelector('#chat-form');
  const input = document.querySelector('#chat-input');
  let current = null;
  function drawList() {
    list.innerHTML = '';
    threads.forEach(t => {
      const li = el(`<li data-id="${t.id}">${t.title}</li>`);
      if (current && current.id === t.id) li.classList.add('active');
      li.addEventListener('click', () => { current = t; drawThread(); drawList(); });
      list.appendChild(li);
    });
  }
  function drawThread() {
    chat.innerHTML = '';
    if (!current) { title.textContent = 'Select a thread'; return; }
    title.textContent = current.title;
    current.msgs.forEach(m => chat.appendChild(el(`<div class="bubble ${m.who}">${m.text}</div>`)));
    chat.scrollTop = chat.scrollHeight;
  }
  form.addEventListener('submit', e => {
    e.preventDefault();
    if (!current) return;
    const text = input.value.trim();
    if (!text) return;
    current.msgs.push({ who: 'me', text });
    input.value = '';
    drawThread();
  });
  current = threads[0];
  drawList();
  drawThread();
}

async function loadStats() {
  try {
    const res = await fetch('/tickets/dashboard/stats/');
    if (!res.ok) throw new Error('stats failed');
    state.stats = await res.json();
  } catch (e) { console.warn('stats load error', e); state.stats = null; }
}

async function loadMyTickets() {
  try {
    const res = await fetch('/tickets/api/tickets/');
    if (!res.ok) throw new Error('tickets failed');
    const data = await res.json();
    const me = (window.CURRENT_USER || '').toLowerCase();
    const mine = me ? data.filter(t => String(t.created_by_username || '').toLowerCase() === me) : data;
    // Normalize for UI
    state.rows = mine.map(t => ({
      id: t.ticket_id || `#${t.id}`,
      subject: t.title,
      status: t.status,
      sla: 0
    }));
  } catch (e) { console.warn('ticket load error', e); state.rows = []; }
}

async function init() {
  await Promise.all([loadStats(), loadMyTickets()]);
  renderStats();
  renderTable();
  initSidebarToggle();
  setupNav();
  setupTicketForm();
  if (document.querySelector('#view-messages')) { setupMessages(); }
  switchView('overview');

  // User avatar dropdown
  const avatarBtn = document.querySelector('#avatarBtn');
  const dropdown = document.querySelector('#userDropdown');
  const ddName = document.querySelector('#ddName');
  const ddRole = document.querySelector('#ddRole');
  const logoutBtn = document.querySelector('#logoutBtn');
  // Fill dropdown from current session (server-rendered name is already in header text)
  if (ddName) ddName.textContent = (window.CURRENT_USER || 'User');
  if (ddRole) ddRole.textContent = 'Member';
  function toggleDropdown(show) { if (!dropdown) return; dropdown.classList.toggle('hidden', show === false ? true : (show === true ? false : dropdown.classList.contains('hidden') ? false : true)); }
  if (avatarBtn) {
    avatarBtn.addEventListener('click', (e) => { e.stopPropagation(); dropdown && dropdown.classList.toggle('hidden'); });
    document.addEventListener('click', (e) => {
      if (!dropdown || dropdown.classList.contains('hidden')) return;
      if (!dropdown.contains(e.target) && e.target !== avatarBtn) { dropdown.classList.add('hidden'); }
    });
  }
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('auth');
      dropdown && dropdown.classList.add('hidden');
    });
  }
}

document.addEventListener('DOMContentLoaded', init);
