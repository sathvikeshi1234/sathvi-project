// Custom Action Menu System with beautiful styling
setTimeout(() => {
    console.log('Initializing Action Menu System...');
   
    // Find all action buttons
    const actionButtons = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    console.log('Found action buttons:', actionButtons.length);
   
    actionButtons.forEach(function(button, index) {
        console.log('Setting up action menu', index);
       
        // Convert button to action trigger
        button.classList.add('action-trigger-btn');
       
        // Wrap in action menu container
        const container = button.parentElement;
        container.classList.add('action-menu-container');
       
        // Find the menu panel
        const menuPanel = container.querySelector('ul.dropdown-menu');
        if (menuPanel) {
            menuPanel.classList.remove('dropdown-menu');
            menuPanel.classList.add('action-menu-panel');
           
            // Convert menu items
            const menuItems = menuPanel.querySelectorAll('li > a');
            menuItems.forEach(item => {
                item.classList.remove('dropdown-item');
                item.classList.add('action-menu-item');
               
                // Add danger class for delete items
                if (item.textContent.includes('Delete')) {
                    item.classList.add('danger');
                }
            });
           
            // Convert separators
            const separators = menuPanel.querySelectorAll('hr.dropdown-divider');
            separators.forEach(separator => {
                separator.classList.remove('dropdown-divider');
                separator.classList.add('action-menu-separator');
            });
        }
       
        // Remove existing click handlers
        button.onclick = null;
       
        // Add custom click handler
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
           
            console.log('Action button clicked');
           
            // Close all other action menus
            document.querySelectorAll('.action-menu-panel.active').forEach(panel => {
                if (panel !== menuPanel) {
                    panel.classList.remove('active');
                }
            });
           
            // Toggle this action menu
            if (menuPanel) {
                menuPanel.classList.toggle('active');
                console.log('Action menu toggled:', menuPanel.classList.contains('active'));
            }
        });
    });
   
    // Close action menus when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.action-menu-container')) {
            document.querySelectorAll('.action-menu-panel.active').forEach(panel => {
                panel.classList.remove('active');
            });
        }
    });
   
    // Keyboard support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.action-menu-panel.active').forEach(panel => {
                panel.classList.remove('active');
            });
        }
    });
   
    console.log('Action Menu System initialized successfully!');
    
    // Add Reset Password functionality
    console.log('Adding Reset Password functionality...');
    
    // Wait a bit for the table to load
    setTimeout(() => {
        // Check if any elements with the class exist
        const allResetLinks = document.querySelectorAll('.user-action-reset-password');
        console.log('Found reset password links:', allResetLinks.length);
        
        // Also check all dropdown items to see what's there
        const allDropdownItems = document.querySelectorAll('.action-menu-item');
        console.log('Total dropdown items found:', allDropdownItems.length);
        allDropdownItems.forEach((item, index) => {
            if (item.textContent.includes('Reset Password')) {
                console.log(`Found Reset Password item ${index}:`, item.textContent, item.className);
            }
        });
        
        allResetLinks.forEach(function(link, index) {
            console.log(`Setting up reset password link ${index}:`, link);
            link.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Reset password link clicked!');
                
                const row = e.target.closest('tr');
                if (!row) {
                    console.error('Could not find parent row');
                    return;
                }
                
                const idEl = row.querySelector('.user-id');
                const nameEl = row.querySelector('.user-name');
                
                const userId = idEl ? idEl.dataset.userId : null;
                const fullName = nameEl ? nameEl.textContent.trim() : '';
                
                console.log('User data:', { userId, fullName });
                
                if (!userId) {
                    console.error('No user ID found');
                    return;
                }
                
                // Populate modal
                const userInfo = document.getElementById('set_password_user_info');
                const hiddenUserId = document.getElementById('set_password_user_id');
                
                if (userInfo) {
                    userInfo.textContent = fullName;
                    console.log('Set user info:', fullName);
                }
                
                if (hiddenUserId) {
                    hiddenUserId.value = userId;
                    console.log('Set user ID:', userId);
                }
                
                // Clear form fields
                const passwordField = document.getElementById('set_password_password');
                const confirmPasswordField = document.getElementById('set_password_confirm_password');
                
                if (passwordField) passwordField.value = '';
                if (confirmPasswordField) confirmPasswordField.value = '';
                
                // Show modal
                const modal = document.getElementById('setPasswordModal');
                if (modal) {
                    console.log('Showing modal');
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                } else {
                    console.error('Modal not found');
                }
            });
        });
        
        // Add form submission handler
        const setPasswordForm = document.getElementById('setPasswordForm');
        if (setPasswordForm) {
            console.log('Adding form submission handler');
            setPasswordForm.addEventListener('submit', function(e) {
                e.preventDefault();
                console.log('Form submitted');
                
                const userId = document.getElementById('set_password_user_id')?.value;
                const newPassword = document.getElementById('set_password_password')?.value;
                const confirmPassword = document.getElementById('set_password_confirm_password')?.value;
                
                console.log('Form data:', { userId, newPassword, confirmPassword });
                
                if (!newPassword || !confirmPassword) {
                    alert('Please fill in both password fields.');
                    return;
                }
                
                if (newPassword.length < 6) {
                    alert('Password must be at least 6 characters long.');
                    return;
                }
                
                if (newPassword !== confirmPassword) {
                    alert('Passwords do not match.');
                    return;
                }
                
                const formData = new FormData();
                formData.append('password', newPassword);
                formData.append('confirm_password', confirmPassword);
                
                fetch(`/api/users/${userId}/set-password/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken') || '',
                    },
                    credentials: 'same-origin',
                    body: formData,
                }).then(resp => {
                    if (!resp.ok) {
                        return resp.json().then(data => { throw new Error(data.error || 'Failed to reset password'); });
                    }
                    return resp.json();
                }).then(data => {
                    alert(data.message || 'Password reset successfully!');
                    
                    const modal = document.getElementById('setPasswordModal');
                    if (modal) {
                        const bsModal = bootstrap.Modal.getInstance(modal);
                        if (bsModal) bsModal.hide();
                    }
                }).catch(err => {
                    console.error('Error:', err);
                    alert(err.message || 'Failed to reset password.');
                });
            });
        }
        
        // Simple CSRF token helper
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }, 1000); // Wait 1 second for table to load
}, 200);
