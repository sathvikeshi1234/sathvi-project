#!/usr/bin/env python3
"""
Create a simple, reliable ticket submission form
"""

def create_simple_form():
    html_content = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TicketHub - Create Ticket</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="{% static 'userdashboard/css/styles.css' %}">
</head>
<body class="app-body" data-page="dashboard">
<div class="app-root">
    <!-- Include Sidebar -->
    {% include 'userdashboard/partials/sidebar.html' %}
    
    <!-- Main Content -->
    <main class="main">
        <!-- Include Header -->
        {% include 'userdashboard/partials/header.html' %}
        
        <section class="page">
            <section class="tickets">
                <div class="page-header">
                    <div class="page-header-content">
                        <div>
                            <h1 class="section-title">Create New Ticket</h1>
                            <p class="page-subtitle">Fill in details below to create a new support ticket</p>
                        </div>
                    </div>
                </div>

                <form method="post" action="" id="ticketForm" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="ticket-form">
                        <div class="form-group">
                            <label for="ticket-title">Ticket Title *</label>
                            <input type="text" id="ticket-title" name="title" class="form-control" placeholder="Enter ticket title" required>
                            <div class="text-danger" id="error-title" style="display:none; margin-top:6px; color:#dc3545;"></div>
                        </div>
                    
                        <div class="form-group">
                            <label for="ticket-description">Description *</label>
                            <textarea id="ticket-description" name="description" class="form-control" rows="6" placeholder="Describe the issue" required></textarea>
                            <div class="text-danger" id="error-description" style="display:none; margin-top:6px; color:#dc3545;"></div>
                        </div>
                    
                        <div class="form-row">
                            <div class="form-group">
                                <label for="priority">Priority *</label>
                                <select id="priority" name="priority" class="form-control" required>
                                    <option value="">Select Priority</option>
                                    <option value="Low">Low</option>
                                    <option value="Medium">Medium</option>
                                    <option value="High">High</option>
                                    <option value="Critical">Critical</option>
                                </select>
                                <div class="text-danger" id="error-priority" style="display:none; margin-top:6px; color:#dc3545;"></div>
                            </div>
                            
                            <div class="form-group">
                                <label for="category">Category *</label>
                                <select id="category" name="category" class="form-control" required>
                                    <option value="">Select Category</option>
                                    <option value="Technical">Technical</option>
                                    <option value="IT Support">IT Support</option>
                                    <option value="Others">Others</option>
                                </select>
                                
                                <input type="text" id="category-other" name="category_other" class="form-control" placeholder="Please type your category" style="display:none; margin-top: 10px;">
                                <div class="text-danger" id="error-category" style="display:none; margin-top:6px; color:#dc3545;"></div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="file-upload">Attachments</label>
                            <div class="file-upload">
                                <input type="file" id="file-upload" name="attachments" multiple hidden>
                                <label for="file-upload" class="file-upload-label">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                    <span>Click to upload or drag and drop</span>
                                </label>
                            </div>
                            <div class="text-danger" id="error-attachments" style="display:none; margin-top:6px; color:#dc3545;"></div>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-draft">
                                <i class="fas fa-save"></i> Save as Draft
                            </button>
                            <button type="submit" class="btn btn-submit">
                                <i class="fas fa-paper-plane"></i> Submit Ticket
                            </button>
                        </div>
                    </div>
                </form>
            </section>
        </main>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('ticketForm');
        const categoryEl = document.getElementById('category');
        const otherEl = document.getElementById('category-other');
        
        // Show/hide "Other" category field
        categoryEl.addEventListener('change', function() {
            if (this.value === 'Others') {
                otherEl.style.display = 'block';
                otherEl.required = true;
            } else {
                otherEl.style.display = 'none';
                otherEl.required = false;
            }
        });
        
        // Handle form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const title = document.getElementById('ticket-title').value.trim();
            const description = document.getElementById('ticket-description').value.trim();
            const priority = document.getElementById('priority').value;
            const category = document.getElementById('category').value;
            
            let isValid = true;
            
            // Clear previous errors
            document.querySelectorAll('.text-danger').forEach(el => el.style.display = 'none');
            
            // Validate title
            if (!title || title.length < 5) {
                document.getElementById('error-title').textContent = title ? 'Title must be at least 5 characters' : 'Title is required';
                document.getElementById('error-title').style.display = 'block';
                isValid = false;
            }
            
            // Validate description
            if (!description || description.length < 10) {
                document.getElementById('error-description').textContent = description ? 'Description must be at least 10 characters' : 'Description is required';
                document.getElementById('error-description').style.display = 'block';
                isValid = false;
            }
            
            // Validate priority
            if (!priority) {
                document.getElementById('error-priority').textContent = 'Please select a priority';
                document.getElementById('error-priority').style.display = 'block';
                isValid = false;
            }
            
            // Validate category
            if (!category) {
                document.getElementById('error-category').textContent = 'Please select a category';
                document.getElementById('error-category').style.display = 'block';
                isValid = false;
            } else if (category === 'Others' && !otherEl.value.trim()) {
                document.getElementById('error-category').textContent = 'Please type your category';
                document.getElementById('error-category').style.display = 'block';
                isValid = false;
            }
            
            if (!isValid) {
                return;
            }
            
            // Submit via AJAX
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitBtn.disabled = true;
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Ticket created successfully!');
                    form.reset();
                    window.location.href = '/dashboard/user-dashboard/tickets/';
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating ticket. Please try again.');
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    });
    </script>
</body>
</html>
"""
    
    return html_content

if __name__ == '__main__':
    print("Creating simplified ticket form...")
    print("This form will be more reliable and easier to debug.")
    print("Save this content to replace the current ticket.html template.")
    print("=" * 60)
    print(create_simple_form())
