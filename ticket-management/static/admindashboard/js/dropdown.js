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
                // Check if this is a reset password link
                if (item.textContent.includes('Reset Password')) {
                    // Keep the user-action-reset-password class and add action-menu-item
                    item.classList.add('action-menu-item');
                    console.log('Reset Password item found, keeping classes:', item.className);
                    
                    // Add reset password click handler immediately
                    item.addEventListener('click', function(e) {
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
                        
                        // Show modal
                        console.log('Looking for modal elements...');
                        const userInfo = document.getElementById('set_password_user_info');
                        const hiddenUserId = document.getElementById('set_password_user_id');
                        const modal = document.getElementById('setPasswordModal');
                        
                        console.log('Modal elements found:', {
                            userInfo: !!userInfo,
                            hiddenUserId: !!hiddenUserId,
                            modal: !!modal,
                            bootstrap: !!window.bootstrap,
                            bootstrapModal: !!(window.bootstrap && window.bootstrap.Modal)
                        });
                        
                        if (userInfo) {
                            userInfo.textContent = fullName;
                            console.log('Set user info:', fullName);
                        } else {
                            console.error('User info element not found');
                        }
                        
                        if (hiddenUserId) {
                            hiddenUserId.value = userId;
                            console.log('Set user ID:', userId);
                        } else {
                            console.error('Hidden user ID element not found');
                        }
                        
                        if (modal) {
                            console.log('Modal found, attempting to show...');
                            if (window.bootstrap && window.bootstrap.Modal) {
                                // Wait a bit for modal to be fully loaded
                                setTimeout(() => {
                                    const bsModal = new bootstrap.Modal(modal);
                                    bsModal.show();
                                    console.log('Modal show() called');
                                }, 500);
                            } else {
                                console.error('Bootstrap Modal not available');
                            }
                        } else {
                            console.error('Modal not found, retrying...');
                            // Retry after 1 second
                            setTimeout(() => {
                                const retryModal = document.getElementById('setPasswordModal');
                                if (retryModal) {
                                    console.log('Modal found on retry!');
                                    const userInfo = document.getElementById('set_password_user_info');
                                    const hiddenUserId = document.getElementById('set_password_user_id');
                                    
                                    if (userInfo) userInfo.textContent = fullName;
                                    if (hiddenUserId) hiddenUserId.value = userId;
                                    
                                    const bsModal = new bootstrap.Modal(retryModal);
                                    bsModal.show();
                                } else {
                                    console.error('Modal still not found on retry');
                                }
                            }, 1000);
                        }
                    });
                } else {
                    // For other items, replace dropdown-item with action-menu-item
                    item.classList.remove('dropdown-item');
                    item.classList.add('action-menu-item');
                }
               
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
    
    // Add the setPasswordModal directly to the page since users.html script isn't loading
    if (!document.getElementById('setPasswordModal')) {
        console.log('Adding setPasswordModal directly to page...');
        const modalHTML = `
            <div class="modal fade" id="setPasswordModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Set User Password</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="setPasswordForm">
                                <input type="hidden" id="set_password_user_id" name="user_id">
                                <div class="mb-3">
                                    <label class="form-label" for="set_password_user_info">User</label>
                                    <div id="set_password_user_info" class="form-control bg-light text-muted"></div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label" for="set_password_password">New Password</label>
                                    <input type="password" id="set_password_password" name="password" class="form-control" autocomplete="new-password" required>
                                    <div class="form-text">Password must be at least 6 characters long</div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label" for="set_password_confirm_password">Confirm Password</label>
                                    <input type="password" id="set_password_confirm_password" name="confirm_password" class="form-control" autocomplete="new-password" required>
                                </div>
                                <div class="alert alert-info">
                                    <i class="bi bi-info-circle me-2"></i>
                                    <strong>Note:</strong> After setting the password, the user will be able to login using their email/username and this password.
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-warning">Set Password</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to document body
        const modalDiv = document.createElement('div');
        modalDiv.innerHTML = modalHTML;
        document.body.appendChild(modalDiv.firstElementChild);
        console.log('setPasswordModal added to page');
    }
    
    // Debug: Check if modals container exists loaded
    const modalsContainer = document.getElementById('modals-container');
    console.log('Modals container found:', !!modalsContainer);
    if (modalsContainer) {
        console.log('Modals container children:', modalsContainer.children.length);
        console.log('Modals container HTML:', modalsContainer.innerHTML.substring(0, 200) + '...');
    }
    
    // Debug: Check if setPasswordModal exists anywhere
    const allModals = document.querySelectorAll('[id*="Modal"]');
    console.log('All modals found:', allModals.length);
    allModals.forEach((modal, index) => {
        console.log(`Modal ${index}:`, modal.id);
    });
    
    // Add form submission handler for reset password
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
}, 3000);
