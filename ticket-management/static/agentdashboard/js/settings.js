// ============================================
// SETTINGS PAGE FUNCTIONALITY
// ============================================
// Agent Dashboard Settings JavaScript
console.log('Settings.js v202502131008 loaded');

document.addEventListener('DOMContentLoaded', function() {
    // Initialize settings page
    initializeSettingsPage();
    
    // Handle save settings button
    const saveSettingsBtn = document.getElementById('saveSettings');
    const resetDefaultsBtn = document.getElementById('resetDefaults');
    const agentSettingsForm = document.getElementById('agent-settings-form');
    
    if (saveSettingsBtn && agentSettingsForm) {
        saveSettingsBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const originalText = saveSettingsBtn.innerHTML;
            saveSettingsBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Saving...';
            saveSettingsBtn.disabled = true;
            
            try {
                const formData = new FormData(agentSettingsForm);
                
                // Convert FormData to plain object for debugging
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                console.log('Saving settings:', data);
                
                const response = await fetch('/dashboard/agent-dashboard/settings.html', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    if (result.success) {
                        // Update any UI elements if needed
                        if (result.data) {
                            updateSettingsUI(result.data);
                        }
                        
                        // Show success message in settings page
                        const settingsSavedMsg = document.getElementById('settingsSavedMessage');
                        if (settingsSavedMsg) {
                            settingsSavedMsg.textContent = 'Settings saved successfully!';
                            settingsSavedMsg.style.display = 'block';
                            settingsSavedMsg.className = 'alert alert-success alert-dismissible fade show';
                            
                            setTimeout(() => {
                                settingsSavedMsg.style.display = 'none';
                            }, 3000);
                        }
                    } else {
                        showToast(result.message || 'Failed to save settings', 'error');
                    }
                } else {
                    showToast('Failed to save settings. Please try again.', 'error');
                }
                
            } catch (error) {
                console.error('Error saving settings:', error);
                showToast('An error occurred while saving settings', 'error');
            } finally {
                // Restore button state
                saveSettingsBtn.innerHTML = originalText;
                saveSettingsBtn.disabled = false;
            }
        });
    }
    
    // Handle reset defaults button
    if (resetDefaultsBtn) {
        resetDefaultsBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to reset all settings to their default values? This action cannot be undone.')) {
                try {
                    const response = await fetch('/dashboard/agent-dashboard/settings.html', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: 'reset_defaults=true'
                    });
                    
                    if (response.ok) {
                        showToast('Settings reset to defaults successfully!', 'info');
                        // Reload the page to show default values
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        showToast('Failed to reset settings', 'error');
                    }
                } catch (error) {
                    console.error('Error resetting settings:', error);
                    showToast('An error occurred while resetting settings', 'error');
                }
            }
        });
    }
    
    // Handle theme color selection
    const themeColors = document.querySelectorAll('.theme-color');
    const primaryColorInput = document.getElementById('primaryColor');
    
    if (themeColors.length > 0) {
        themeColors.forEach(color => {
            color.addEventListener('click', function() {
                // Remove active class from all colors
                themeColors.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked color
                this.classList.add('active');
                
                // Update primary color input if it exists
                if (primaryColorInput) {
                    primaryColorInput.value = this.dataset.color;
                }
                
                // Apply color to CSS variables
                document.documentElement.style.setProperty('--primary-color', this.dataset.color);
                
                // Save preference
                localStorage.setItem('primaryColor', this.dataset.color);
                
                showToast('Theme color updated!', 'success');
            });
        });
    }
    
    // Initialize primary color from localStorage
    const savedPrimaryColor = localStorage.getItem('primaryColor');
    if (savedPrimaryColor) {
        document.documentElement.style.setProperty('--primary-color', savedPrimaryColor);
        
        // Set active color
        themeColors.forEach(color => {
            if (color.dataset.color === savedPrimaryColor) {
                color.classList.add('active');
                if (primaryColorInput) {
                    primaryColorInput.value = savedPrimaryColor;
                }
            }
        });
    }
    
    // Handle file uploads (logo, favicon, login background)
    const logoUpload = document.getElementById('logoUpload');
    const faviconUpload = document.getElementById('faviconUpload');
    const loginBgUpload = document.getElementById('loginBgUpload');
    const logoPreview = document.getElementById('logoPreview');
    const faviconPreview = document.getElementById('faviconPreview');
    
    if (logoUpload && logoPreview) {
        logoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    logoPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    if (faviconUpload && faviconPreview) {
        faviconUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && (file.type === 'image/x-icon' || file.type === 'image/png')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    faviconPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    if (loginBgUpload) {
        loginBgUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                // Handle login background upload
                console.log('Login background selected:', file.name);
            }
        });
    }
    
    // Handle tab switching
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-bs-target');
            
            // Remove active class from all tabs and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active', 'show'));
            
            // Add active class to clicked tab and corresponding pane
            this.classList.add('active');
            const targetPane = document.querySelector(target);
            if (targetPane) {
                targetPane.classList.add('active', 'show');
            }
        });
    });
});

function initializeSettingsPage() {
    // Set initial active tab
    const firstTab = document.querySelector('[data-bs-toggle="tab"]');
    if (firstTab) {
        firstTab.click();
    }
}

function updateSettingsUI(data) {
    // Update UI elements with new settings data
    console.log('Updating UI with settings:', data);
    
    // You can add specific UI updates here based on the settings data
    // For example, update form values, toggle switches, etc.
}

function showToast(message, type = 'info') {
    // Create and show a toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,.15);
    `;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert">×</button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
