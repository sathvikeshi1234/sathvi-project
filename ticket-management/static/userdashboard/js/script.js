// Sidebar toggle for mobile (works with injected layout)

document.addEventListener("click", (e) => {

  const openBtn = e.target.closest("#sidebarOpenBtn");

  const closeBtn = e.target.closest("#sidebarCloseBtn");

  const sidebar = document.getElementById("sidebar");



  if (!sidebar) return;



  if (openBtn) {

    e.stopPropagation();

    sidebar.classList.remove("hidden-mobile");

    return;

  }



  if (closeBtn) {

    e.stopPropagation();

    sidebar.classList.add("hidden-mobile");

    return;

  }



  // Click anywhere outside sidebar on mobile: close it

  const clickedInsideSidebar = sidebar.contains(e.target);

  const isMobileWidth = window.innerWidth < 991.98;

  if (isMobileWidth && !clickedInsideSidebar) {

    sidebar.classList.add("hidden-mobile");

  }

});



// Update the theme in localStorage and apply it

const updateTheme = (isLight) => {

  if (isLight) {

    document.body.classList.add("light-theme");

    document.body.classList.remove("dark-theme");

  } else {

    document.body.classList.add("dark-theme");

    document.body.classList.remove("light-theme");

  }

  localStorage.setItem('theme', isLight ? 'light' : 'dark');

  updateThemeIcon();

};



// Update the theme icon based on current theme

const updateThemeIcon = () => {

  const btn = document.getElementById("themeToggleBtn");

  if (!btn) return;

  const isLight = document.body.classList.contains("light-theme");



  const sunSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M12 20v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M4.93 4.93l1.41 1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M17.66 17.66l1.41 1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M2 12h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M20 12h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M4.93 19.07l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M17.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  const moonSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M20.354 15.354A9 9 0 0 1 8.646 3.646 7 7 0 1 0 20.354 15.354Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';



  btn.innerHTML = isLight ? sunSvg : moonSvg;

};



// Apply saved theme on page load

const applySavedTheme = () => {

  const savedTheme = localStorage.getItem('theme');

  if (savedTheme === 'light') {

    updateTheme(true);

  } else if (savedTheme === 'dark') {

    updateTheme(false);

  }

};



// Toggle theme on button click

document.addEventListener("click", (e) => {

  const btn = e.target.closest("#themeToggleBtn");

  if (!btn) return;

  const isLight = document.body.classList.contains("light-theme");

  updateTheme(!isLight);

});



// Apply saved theme when DOM is ready

document.addEventListener("DOMContentLoaded", () => {

  // slight delay to allow layout.js to inject header

  setTimeout(() => {

    applySavedTheme();

    updateThemeIcon();

  }, 50);

});



// Try to set initial icon once DOM is ready (button may appear a bit later)

document.addEventListener("DOMContentLoaded", () => {

  // slight delay to allow layout.js to inject header

  setTimeout(updateThemeIcon, 50);

});



// Ticket filter logic

const filterButtons = document.querySelectorAll("#ticketFilters .chip");

const tickets = document.querySelectorAll("#ticketsList .ticket");



filterButtons.forEach((btn) => {

  btn.addEventListener("click", () => {

    const filter = btn.getAttribute("data-filter");



    filterButtons.forEach((b) => b.classList.remove("active"));

    btn.classList.add("active");



    tickets.forEach((ticket) => {

      const status = ticket.getAttribute("data-status");

      if (filter === "all" || filter === status) {

        ticket.classList.remove("hidden");

      } else {

        ticket.classList.add("hidden");

      }

    });

  });

});



// Three-dots actions dropdown (user tickets table)

document.addEventListener('click', (e) => {

  const toggle = e.target.closest('.ts-actions__toggle');



  const closeAll = () => {

    document.querySelectorAll('.ts-actions.is-open').forEach(el => {

      el.classList.remove('is-open');

      const t = el.querySelector('.ts-actions__toggle');

      t && t.setAttribute('aria-expanded', 'false');

    });

  };



  // Toggle dropdown

  if (toggle) {

    e.preventDefault();

    e.stopPropagation();



    const wrap = toggle.closest('.ts-actions');

    if (!wrap) return;



    // Close others

    document.querySelectorAll('.ts-actions.is-open').forEach(el => {

      if (el !== wrap) {

        el.classList.remove('is-open');

        const t = el.querySelector('.ts-actions__toggle');

        t && t.setAttribute('aria-expanded', 'false');

      }

    });



    const willOpen = !wrap.classList.contains('is-open');

    wrap.classList.toggle('is-open', willOpen);

    toggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');

    return;

  }



  // Click on any action inside the menu: close menu (then let the action proceed)

  const menu = e.target.closest('.ts-actions__menu');

  if (menu) {

    const wrap = menu.closest('.ts-actions');

    if (!wrap) return;



    const clickedActionItem = !!e.target.closest('.ts-actions__item');

    const clickedStar = !!e.target.closest('.ticket-actions__star');

    if (clickedActionItem || clickedStar) {

      wrap.classList.remove('is-open');

      const t = wrap.querySelector('.ts-actions__toggle');

      t && t.setAttribute('aria-expanded', 'false');

    }

    return;

  }



  // Click outside: close all

  closeAll();

});



document.addEventListener('keydown', (e) => {

  if (e.key !== 'Escape') return;

  document.querySelectorAll('.ts-actions.is-open').forEach(el => {

    el.classList.remove('is-open');

    const t = el.querySelector('.ts-actions__toggle');

    t && t.setAttribute('aria-expanded', 'false');

  });

});



// Custom delete confirmation modal (tickets page)

(() => {

  let pendingDeleteForm = null;



  function getEls() {

    return {

      overlay: document.getElementById('deleteConfirmOverlay'),

      cancel: document.getElementById('deleteConfirmCancel'),

      ok: document.getElementById('deleteConfirmOk')

    };

  }



  function openConfirm() {

    const { overlay, ok } = getEls();

    if (!overlay) return;

    overlay.classList.remove('hidden');

    overlay.setAttribute('aria-hidden', 'false');

    try { ok && ok.focus(); } catch (e) {}

  }



  function closeConfirm() {

    const { overlay } = getEls();

    if (!overlay) return;

    overlay.classList.add('hidden');

    overlay.setAttribute('aria-hidden', 'true');

    pendingDeleteForm = null;

  }



  // Intercept delete form submits

  document.addEventListener('submit', (e) => {

    const form = e.target;

    if (!form || !(form instanceof HTMLFormElement)) return;

    if (!form.classList.contains('ticket-actions__delete-form')) return;



    const { overlay } = getEls();

    if (!overlay) return; // fallback: allow normal submit



    e.preventDefault();

    pendingDeleteForm = form;

    openConfirm();

  }, true);



  // Buttons

  document.addEventListener('click', (e) => {

    const { overlay, cancel, ok } = getEls();

    if (!overlay) return;



    if (cancel && (e.target === cancel || e.target.closest('#deleteConfirmCancel'))) {

      e.preventDefault();

      closeConfirm();

      return;

    }



    if (ok && (e.target === ok || e.target.closest('#deleteConfirmOk'))) {

      e.preventDefault();

      const f = pendingDeleteForm;

      closeConfirm();

      if (f) f.submit();

      return;

    }



    // click outside dialog closes

    if (e.target === overlay) {

      closeConfirm();

    }

  });



  // Escape closes

  document.addEventListener('keydown', (e) => {

    if (e.key === 'Escape') {

      const { overlay } = getEls();

      if (overlay && !overlay.classList.contains('hidden')) {

        closeConfirm();

      }

    }

  });

})();



// Tickets page filters (status + sort) for userdashboard/tickets.html

document.addEventListener('DOMContentLoaded', () => {

  const statusSelect = document.getElementById('ticketStatusFilter');

  const sortSelect = document.getElementById('ticketSort');

  const tbody = document.getElementById('myTickets');



  if (!statusSelect || !sortSelect || !tbody) return;



  const getRows = () => Array.from(tbody.querySelectorAll('tr'));



  const priorityOrder = {

    'Critical': 4,

    'High': 3,

    'Medium': 2,

    'Low': 1

  };



  const applyFiltersAndSort = () => {

    const statusFilter = statusSelect.value || 'all';

    const sortMode = sortSelect.value || 'recent';



    let rows = getRows();



    // Filter by status

    rows.forEach(row => {

      const rowStatus = (row.getAttribute('data-status') || '').trim();

      const show = (statusFilter === 'all' || rowStatus === statusFilter);

      row.style.display = show ? '' : 'none';

    });



    // Sort only visible rows in DOM order

    const visibleRows = rows.filter(r => r.style.display !== 'none');



    visibleRows.sort((a, b) => {

      if (sortMode === 'recent' || sortMode === 'oldest') {

        const aCreated = Number(a.getAttribute('data-created') || 0);

        const bCreated = Number(b.getAttribute('data-created') || 0);

        if (sortMode === 'recent') {

          return bCreated - aCreated; // newest first

        }

        return aCreated - bCreated;   // oldest first

      }



      if (sortMode === 'priority') {

        const aP = (a.getAttribute('data-priority') || '').trim();

        const bP = (b.getAttribute('data-priority') || '').trim();

        const aScore = priorityOrder[aP] || 0;

        const bScore = priorityOrder[bP] || 0;

        return bScore - aScore; // highest priority first

      }



      return 0;

    });



    // Re-append in sorted order

    visibleRows.forEach(row => tbody.appendChild(row));

  };



  statusSelect.addEventListener('change', applyFiltersAndSort);

  sortSelect.addEventListener('change', applyFiltersAndSort);



  // Initial apply to ensure consistent order

  applyFiltersAndSort();

});



// User profile dropdown + notifications (work with injected header using event delegation)

document.addEventListener("click", (e) => {

  const userToggle = e.target.closest("#userMenuToggle");

  const userMenu = document.getElementById("userMenu");

  const userDropdown = document.getElementById("userDropdown");



  const notifBtn = e.target.closest("#notificationBtn");

  const notifMenu = document.getElementById("notificationMenu");

  const notifDropdown = document.getElementById("notificationDropdown");

  const viewAllBtn = e.target.closest("#notificationViewAllBtn");



  // Click on avatar: toggle profile dropdown

  if (userToggle && userMenu && userDropdown) {

    e.stopPropagation();

    userDropdown.classList.toggle("hidden");

    // Close notification dropdown if open

    if (notifDropdown) notifDropdown.classList.add("hidden");

    return;

  }



  // Click on notification bell: toggle notification dropdown

  if (notifBtn && notifMenu && notifDropdown) {

    e.stopPropagation();

    notifDropdown.classList.toggle("hidden");

    if (!notifDropdown.classList.contains('hidden')) {

      window.__refreshNavbarNotifications && window.__refreshNavbarNotifications();

    }

    // Close profile dropdown if open

    if (userDropdown) userDropdown.classList.add("hidden");

    return;

  }



  // Click on "View all notifications"

  if (viewAllBtn) {

    e.stopPropagation();

    if (notifDropdown) notifDropdown.classList.add("hidden");



    // Go to the user dashboard notifications page (absolute URL)

    window.location.href = "/dashboard/user-dashboard/notifications/";

    return;

  }



  // Click outside: close both dropdowns if open

  if (userMenu && userDropdown && !userMenu.contains(e.target)) {

    userDropdown.classList.add("hidden");

  }



  if (notifMenu && notifDropdown && !notifMenu.contains(e.target)) {

    notifDropdown.classList.add("hidden");

  }

});



function escapeHtml(str) {

  return String(str)

    .replace(/&/g, '&amp;')

    .replace(/</g, '&lt;')

    .replace(/>/g, '&gt;')

    .replace(/"/g, '&quot;')

    .replace(/'/g, '&#039;');

}



async function refreshNavbarNotifications() {

  const dropdown = document.getElementById('notificationDropdown');

  const list = document.getElementById('notificationList');

  const empty = document.getElementById('notificationEmptyState');

  const badge = document.getElementById('notificationBadge');



  if (!dropdown || !list || !empty || !badge) return;



  try {

    const res = await fetch('/dashboard/user-dashboard/api/notifications/', {

      credentials: 'same-origin',

      headers: {

        'Accept': 'application/json'

      }

    });



    if (!res.ok) return;

    const data = await res.json();



    const unreadCount = Number(data.unread_count || 0);

    badge.textContent = String(unreadCount);

    badge.classList.toggle('hidden', unreadCount <= 0);



    const results = Array.isArray(data.results) ? data.results : [];

    list.innerHTML = '';



    if (!results.length) {

      empty.classList.remove('hidden');

      return;

    }



    empty.classList.add('hidden');

    results.forEach((n) => {

      const icon = n.icon ? `<i class="${escapeHtml(n.icon)}"></i> ` : '';

      const title = n.title ? `<strong>${escapeHtml(n.title)}</strong>` : '';

      const text = n.text ? `<span>${escapeHtml(n.text)}</span>` : '';

      const time = n.time_ago ? `<span> · ${escapeHtml(n.time_ago)}</span>` : '';

      const href = n.url ? escapeHtml(n.url) : '#';

      const item = document.createElement('div');

      item.className = 'navbar-notification-item';



      if ((n.category || '') === 'tickets' && href && href !== '#') {

        item.innerHTML = `<a href="#" class="ticket-view-link" data-ticket-url="${href}" style="color: inherit; text-decoration: none; display: block;">${icon}${title}<br />${text}${time}</a>`;

      } else {

        item.innerHTML = `<a href="${href}" style="color: inherit; text-decoration: none; display: block;">${icon}${title}<br />${text}${time}</a>`;

      }

      list.appendChild(item);

    });

  } catch (err) {

    return;

  }

}



window.__refreshNavbarNotifications = refreshNavbarNotifications;



document.addEventListener('DOMContentLoaded', () => {

  refreshNavbarNotifications();

  setInterval(refreshNavbarNotifications, 20000);

});



// Logout button

document.addEventListener('click', (e) => {

  if (e.target.matches('#logoutBtn') || e.target.closest('#logoutBtn')) {

    e.preventDefault();

    const overlay = document.getElementById('logoutConfirmOverlay');

    const ok = document.getElementById('logoutConfirmOk');

    if (!overlay) {

      // Fallback

      window.location.href = '/logout/';

      return;

    }

    overlay.classList.remove('hidden');

    overlay.setAttribute('aria-hidden', 'false');

    try { ok && ok.focus(); } catch (err) {}

  }

});



// Logout confirm modal controls

(() => {

  const getEls = () => ({

    overlay: document.getElementById('logoutConfirmOverlay'),

    cancel: document.getElementById('logoutConfirmCancel'),

    ok: document.getElementById('logoutConfirmOk')

  });



  const close = () => {

    const { overlay } = getEls();

    if (!overlay) return;

    overlay.classList.add('hidden');

    overlay.setAttribute('aria-hidden', 'true');

  };



  document.addEventListener('click', (e) => {

    const { overlay, cancel, ok } = getEls();

    if (!overlay || overlay.classList.contains('hidden')) return;



    if (cancel && (e.target === cancel || e.target.closest('#logoutConfirmCancel'))) {

      e.preventDefault();

      close();

      return;

    }



    if (ok && (e.target === ok || e.target.closest('#logoutConfirmOk'))) {

      e.preventDefault();

      close();

      window.location.href = '/logout/';

      return;

    }



    if (e.target === overlay) {

      close();

    }

  });



  document.addEventListener('keydown', (e) => {

    if (e.key !== 'Escape') return;

    const { overlay } = getEls();

    if (overlay && !overlay.classList.contains('hidden')) {

      close();

    }

  });

})();



// Overall rating star selector logic for Ratings page

document.addEventListener('DOMContentLoaded', () => {

  const starRating = document.getElementById('starRating');

  const hiddenOverallInput = document.getElementById('overall_rating');

  const ratingLabel = document.getElementById('ratingLabel');



  if (!starRating || !hiddenOverallInput) return;



  let selected = Number(hiddenOverallInput.value || 0);



  const labelMap = {

    0: 'Please select a rating',

    1: 'Very Poor',

    2: 'Poor',

    3: 'Average',

    4: 'Good',

    5: 'Excellent'

  };



  const renderStars = (val) => {

    starRating.querySelectorAll('.star').forEach((el) => {

      const r = Number(el.getAttribute('data-rating')) || 0;

      el.classList.toggle('filled', r <= val);

      el.setAttribute('aria-pressed', r <= val ? 'true' : 'false');

    });

    if (ratingLabel) ratingLabel.textContent = labelMap[val] || labelMap[0];

  };



  // Initial state

  renderStars(selected);



  starRating.addEventListener('mouseover', (e) => {

    const star = e.target.closest('.star');

    if (!star) return;

    const val = Number(star.getAttribute('data-rating')) || 0;

    renderStars(val);

  });



  starRating.addEventListener('mouseleave', () => {

    renderStars(selected);

  });



  starRating.addEventListener('click', (e) => {

    const star = e.target.closest('.star');

    if (!star) return;

    selected = Number(star.getAttribute('data-rating')) || 0;

    hiddenOverallInput.value = String(selected);

    renderStars(selected);

  });



  // Keyboard accessibility

  starRating.querySelectorAll('.star').forEach((el) => {

    el.setAttribute('tabindex', '0');

    el.addEventListener('keydown', (e) => {

      if (e.key === 'Enter' || e.key === ' ') {

        e.preventDefault();

        el.click();

      }

    });

  });

});



// Optional: mini category stars (purely visual)

document.addEventListener('DOMContentLoaded', () => {

  const containers = document.querySelectorAll('.mini-stars');

  containers.forEach((container) => {

    let selected = 0;

    const render = (val) => {

      container.querySelectorAll('.mini-star').forEach((el) => {

        const v = Number(el.getAttribute('data-value')) || 0;

        el.classList.toggle('filled', v <= val);

      });

    };

    render(selected);



    container.addEventListener('mouseover', (e) => {

      const s = e.target.closest('.mini-star');

      if (!s) return;

      const val = Number(s.getAttribute('data-value')) || 0;

      render(val);

    });

    container.addEventListener('mouseleave', () => render(selected));

    container.addEventListener('click', (e) => {

      const s = e.target.closest('.mini-star');

      if (!s) return;

      selected = Number(s.getAttribute('data-value')) || 0;

      render(selected);

    });

  });

});



// Ticket detail modal for user dashboard tickets page

document.addEventListener('click', async (e) => {

  const link = e.target.closest('.ticket-view-link');

  if (!link) return;

  e.preventDefault();



  const url = link.getAttribute('data-ticket-url') || link.getAttribute('href');

  if (!url) return;



  const overlay = document.getElementById('ticketDetailOverlay');

  const content = document.getElementById('ticketDetailContent');

  if (!overlay || !content) return;



  try {

    const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });

    if (!res.ok) return;

    const html = await res.text();

    content.innerHTML = html;

    overlay.classList.remove('hidden');



    const notifDropdown = document.getElementById('notificationDropdown');

    if (notifDropdown) notifDropdown.classList.add('hidden');

  } catch (err) {

    console.error('Failed to load ticket detail', err);

  }

});



document.addEventListener('click', (e) => {

  const overlay = document.getElementById('ticketDetailOverlay');

  if (!overlay) return;



  const closeBtn = e.target.closest('#ticketDetailClose');

  if (closeBtn || e.target === overlay) {

    overlay.classList.add('hidden');

  }

});