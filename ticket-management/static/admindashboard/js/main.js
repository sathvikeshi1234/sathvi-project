// main.js - Common initialization code for all pages

// Toggle mobile menu
function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
        
        // Close menu when clicking outside
        document.addEventListener('click', function closeMenu(e) {
            if (!e.target.closest('.sidebar') && !e.target.closest('#mobile-menu-toggle')) {
                sidebar.classList.remove('show');
                document.removeEventListener('click', closeMenu);
            }
        });
    }
}

// Initialize header when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMobileMenu();
        });
    }
    // Load components
    if (typeof loadComponent === 'function') {
        // Load header if container exists
        if (document.getElementById('header-container')) {
            loadComponent('partials/header.html', 'header-container')
                .then(() => {
                    // Initialize header after loading
                    if (window.initializeHeader) {
                        window.initializeHeader();
                    }
                });
        }

        // Load sidebar if container exists
        if (document.getElementById('sidebar-container')) {
            loadComponent('partials/sidebar.html', 'sidebar-container');
        }

        // Load modals if container exists
        if (document.getElementById('modals-container')) {
            loadComponent('partials/modals.html', 'modals-container');
        }
    }

    // Listen for navigation events (for single-page navigation)
    document.body.addEventListener('click', function(e) {
        // Check if the click was on a navigation link
        const navLink = e.target.closest('a[data-page]');
        if (navLink) {
            // Re-initialize header after a short delay to allow the page to update
            setTimeout(() => {
                if (window.initializeHeader) {
                    window.initializeHeader();
                }
            }, 100);
        }
    });
});
