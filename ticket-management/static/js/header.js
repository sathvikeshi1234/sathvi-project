// js/header.js

// Store event listeners to prevent duplicates
let headerInitialized = false;

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

async function refreshAdminNotifications() {
    const badge = document.getElementById('adminNotificationBadge');
    const list = document.getElementById('adminNotificationsList');
    const empty = document.getElementById('adminNotificationsEmpty');

    if (!badge || !list || !empty) return;

    try {
        const res = await fetch('/dashboard/admin-dashboard/api/notifications/', {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json' }
        });
        if (!res.ok) return;
        const data = await res.json();

        const unreadCount = Number(data.unread_count || 0);
        badge.textContent = String(unreadCount);
        badge.style.display = unreadCount > 0 ? 'inline-block' : 'none';

        const results = Array.isArray(data.results) ? data.results : [];
        list.querySelectorAll('.notification-item[data-dynamic="1"]').forEach((n) => n.remove());

        if (!results.length) {
            empty.style.display = 'block';
            return;
        }

        empty.style.display = 'none';
        results.forEach((n) => {
            const item = document.createElement('div');
            item.className = `notification-item${n.is_unread ? ' unread' : ''}`;
            item.setAttribute('data-dynamic', '1');

            const iconClass = escapeHtml(n.icon || 'bi bi-bell');
            const text = escapeHtml(n.text || '');
            const time = escapeHtml(n.time_ago || '');
            const url = escapeHtml(n.url || '#');

            item.innerHTML = `
                <a href="${url}" style="text-decoration:none; color:inherit; display:flex; gap:10px;">
                    <div class="notification-avatar"><i class="${iconClass}"></i></div>
                    <div class="notification-content">
                        <p>${text}</p>
                        <small>${time}</small>
                    </div>
                </a>
            `;
            list.appendChild(item);
        });
    } catch (e) {
        return;
    }
}

window.__refreshAdminNotifications = refreshAdminNotifications;

// Make the function available globally so it can be called after dynamic loading
window.initializeHeader = function() {
    if (headerInitialized) return;
    headerInitialized = true;

    // Remove any existing event listeners to prevent duplicates
    const newThemeToggle = document.getElementById('theme-toggle')?.cloneNode(true);
    const newMobileMenuToggle = document.getElementById('mobile-menu-toggle')?.cloneNode(true);
    const newNotificationsBtn = document.getElementById('notifications-btn')?.cloneNode(true);
    const newProfileBtn = document.getElementById('profile-btn')?.cloneNode(true);
    const newSidebarToggle = document.getElementById('sidebar-toggle')?.cloneNode(true);
    const newMobileSidebarToggle = document.getElementById('mobile-sidebar-toggle')?.cloneNode(true);

    if (newThemeToggle) document.getElementById('theme-toggle').replaceWith(newThemeToggle);
    if (newMobileMenuToggle) document.getElementById('mobile-menu-toggle').replaceWith(newMobileMenuToggle);
    if (newNotificationsBtn) document.getElementById('notifications-btn').replaceWith(newNotificationsBtn);
    if (newProfileBtn) document.getElementById('profile-btn').replaceWith(newProfileBtn);
    if (newSidebarToggle) document.getElementById('sidebar-toggle').replaceWith(newSidebarToggle);
    if (newMobileSidebarToggle) document.getElementById('mobile-sidebar-toggle').replaceWith(newMobileSidebarToggle);

    // Dark Mode Toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            themeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
        } else {
            themeToggle.innerHTML = '<i class="bi bi-moon-stars"></i>';
        }

        themeToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            themeToggle.innerHTML = isDark ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-stars"></i>';
        });
    }

    // Notifications Dropdown
    const notificationsBtn = document.getElementById('notifications-btn');
    const notificationsDropdown = document.getElementById('notifications-dropdown');

    if (notificationsBtn && notificationsDropdown) {
        notificationsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationsDropdown.classList.toggle('show');
            const profileDropdown = document.getElementById('profile-dropdown');
            if (profileDropdown) profileDropdown.classList.remove('show');

            if (notificationsDropdown.classList.contains('show')) {
                window.__refreshAdminNotifications && window.__refreshAdminNotifications();
            }
        });
    }

    // Profile Dropdown
    const profileBtn = document.getElementById('profile-btn');
    const profileDropdown = document.getElementById('profile-dropdown');

    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isHidden = profileDropdown.style.display === 'none' || !profileDropdown.style.display;
            profileDropdown.style.display = isHidden ? 'block' : 'none';
            if (notificationsDropdown) notificationsDropdown.classList.remove('show');
        });

        document.addEventListener('click', function(e) {
            if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.style.display = 'none';
            }
        });

        const dropdownItems = profileDropdown.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
                this.style.transform = 'translateX(4px)';
            });
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
                this.style.transform = '';
            });
        });
    }

    document.addEventListener('click', function() {
        if (notificationsDropdown) notificationsDropdown.classList.remove('show');
        if (profileDropdown) profileDropdown.classList.remove('show');
    });

    if (window.__refreshAdminNotifications) {
        window.__refreshAdminNotifications();
        setInterval(window.__refreshAdminNotifications, 20000);
    }

    // Sidebar toggles (keep behavior consistent with existing dashboards)
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }

        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }

    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const sidebar1 = document.querySelector('.sidebar');

    if (mobileSidebarToggle && sidebar1) {
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar1.classList.add('collapsed');
        }

        mobileSidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar1.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar1.classList.contains('collapsed'));
        });
    }

    const darkModeSwitch = document.getElementById('darkModeSwitch');
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        if (darkModeSwitch) darkModeSwitch.checked = true;
    } else if (localStorage.getItem('darkMode') === 'false') {
        document.body.classList.remove('dark-mode');
        if (darkModeSwitch) darkModeSwitch.checked = false;
    }

    if (darkModeSwitch) {
        darkModeSwitch.addEventListener('change', function() {
            const enabled = this.checked;
            document.body.classList.toggle('dark-mode', enabled);
            localStorage.setItem('darkMode', enabled ? 'true' : 'false');
        });
    }

    document.addEventListener('click', function(event) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        const clickedToggle = event.target.closest('[data-bs-toggle="dropdown"]');
        if (!clickedToggle && !event.target.closest('.dropdown-menu')) {
            dropdowns.forEach(dropdown => {
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            });
        }
    });

    const dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl, {
            offset: [0, 5],
            boundary: 'viewport',
            reference: 'toggle'
        });
    });
};
