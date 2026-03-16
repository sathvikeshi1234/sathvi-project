// js/header.js

// Store event listeners to prevent duplicates
let headerInitialized = false;

// Make the function available globally so it can be called after dynamic loading
window.initializeHeader = function() {
    console.log('initializeHeader called, headerInitialized:', headerInitialized);
    
    headerInitialized = false;
    
    // Skip if already initialized to prevent duplicate event listeners
    if (headerInitialized) return;
    
    // Wait a bit for the DOM to be fully ready
    setTimeout(() => {
        console.log('Starting header element setup...');
        
        // Get all elements
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        const themeToggle = document.getElementById('theme-toggle');
        const notificationsBtn = document.getElementById('notifications-btn');
        const notificationsDropdown = document.getElementById('notifications-dropdown');
        const profileBtn = document.getElementById('profile-btn');
        const profileDropdown = document.getElementById('profile-dropdown');
        
        console.log('Elements found:');
        console.log('- sidebarToggle:', !!sidebarToggle);
        console.log('- sidebar:', !!sidebar);
        console.log('- themeToggle:', !!themeToggle);
        console.log('- notificationsBtn:', !!notificationsBtn);
        console.log('- notificationsDropdown:', !!notificationsDropdown);
        console.log('- profileBtn:', !!profileBtn);
        console.log('- profileDropdown:', !!profileDropdown);
        
        // Mark as initialized
        headerInitialized = true;
        
        // Dark Mode Toggle
        if (themeToggle) {
            console.log('Setting up dark mode toggle');
            // Set initial theme
            if (localStorage.getItem('darkMode') === 'true') {
                document.body.classList.add('dark-mode');
                themeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
            } else {
                themeToggle.innerHTML = '<i class="bi bi-moon-stars"></i>';
            }
            
            // Toggle theme
            themeToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Dark mode toggle clicked!');
                document.body.classList.toggle('dark-mode');
                const isDark = document.body.classList.contains('dark-mode');
                localStorage.setItem('darkMode', isDark);
                themeToggle.innerHTML = isDark ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-stars"></i>';
                console.log('Dark mode toggled to:', isDark);
            });
        } else {
            console.log('Theme toggle not found');
        }

        // Notifications Dropdown
        if (notificationsBtn && notificationsDropdown) {
            console.log('Setting up notifications dropdown');
            notificationsBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Notifications button clicked!');
                notificationsDropdown.classList.toggle('show');
                if (profileDropdown) profileDropdown.classList.remove('show');
            });
        } else {
            console.log('Notifications elements not found - btn:', !!notificationsBtn, 'dropdown:', !!notificationsDropdown);
        }

        // Profile Dropdown
        if (profileBtn && profileDropdown) {
            console.log('Setting up profile dropdown');
            // Toggle dropdown on profile button click
            profileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Profile button clicked!');
                const isHidden = profileDropdown.style.display === 'none' || !profileDropdown.style.display;
                profileDropdown.style.display = isHidden ? 'block' : 'none';
                if (notificationsDropdown) notificationsDropdown.classList.remove('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
                    profileDropdown.style.display = 'none';
                }
            });

            // Add hover effect to dropdown items
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
        } else {
            console.log('Profile elements not found - btn:', !!profileBtn, 'dropdown:', !!profileDropdown);
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', function() {
            if (notificationsDropdown) notificationsDropdown.classList.remove('show');
            if (profileDropdown) profileDropdown.classList.remove('show');
        });

        // Sidebar Toggle
        if (sidebarToggle && sidebar) {
            console.log('Setting up sidebar toggle');
            // Set initial state
            if (localStorage.getItem('sidebarCollapsed') === 'true') {
                sidebar.classList.add('collapsed');
                console.log('Applied initial collapsed state');
            }
            
            // Toggle sidebar
            sidebarToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Sidebar toggle button clicked!');
                
                const wasCollapsed = sidebar.classList.contains('collapsed');
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
                
                console.log('Sidebar toggled. Was collapsed:', wasCollapsed, 'Now collapsed:', sidebar.classList.contains('collapsed'));
                
                // Force a reflow to ensure CSS changes take effect
                void sidebar.offsetWidth;
            });
        } else {
            console.error('Sidebar toggle or sidebar element not found!');
            console.log('sidebarToggle:', sidebarToggle);
            console.log('sidebar:', sidebar);
        }

        console.log('Header initialization completed successfully!');
    }, 200); // Wait 200ms for DOM to be ready
};
