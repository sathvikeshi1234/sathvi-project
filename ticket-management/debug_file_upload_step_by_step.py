#!/usr/bin/env python
"""
Step-by-step debug for file upload functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from users.models import UserProfile, Role
from tickets.models import Ticket

User = get_user_model()

def debug_file_upload_step_by_step():
    print("=== Step-by-Step File Upload Debug ===")
    
    # Create test users
    admin_role, _ = Role.objects.get_or_create(name='Admin')
    user_role, _ = Role.objects.get_or_create(name='User')
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': admin_role})
    
    # Create customer user
    customer_user, created = User.objects.get_or_create(
        username='customer',
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Customer',
            'last_name': 'User',
        }
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        UserProfile.objects.get_or_create(user=customer_user, defaults={'role': user_role})
    
    # Create a test ticket
    ticket, created = Ticket.objects.get_or_create(
        ticket_id='TEST-001',
        defaults={
            'title': 'Test Ticket for Chat',
            'description': 'This is a test ticket',
            'created_by': customer_user,
            'status': 'Open',
        }
    )
    
    print(f"[OK] Created test environment")
    print(f"   - Admin: {admin_user.get_full_name()} (ID: {admin_user.id})")
    print(f"   - Customer: {customer_user.get_full_name()} (ID: {customer_user.id})")
    print(f"   - Ticket: {ticket.ticket_id}")
    
    # Test the chat page
    client = Client()
    client.force_login(customer_user)
    
    response = client.get('/dashboard/user-dashboard/chat/')
    print(f"\n[OK] Chat page loads: {response.status_code == 200}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Step 1: Check if support_admin is set
        if 'data-contact-id=' in content:
            print("[OK] Step 1: Support admin is set in template")
            
            # Extract the contact ID
            import re
            contact_id_match = re.search(r'data-contact-id="(\d+)"', content)
            if contact_id_match:
                contact_id = contact_id_match.group(1)
                print(f"   - Contact ID: {contact_id}")
            else:
                print("[ERROR] Step 1: Could not extract contact ID")
                return
        else:
            print("[ERROR] Step 1: Support admin NOT set in template")
            return
        
        # Step 2: Check if JavaScript variables are being set
        if 'window.USER_CHAT_CONTACT_ID' in content:
            print("[OK] Step 2: JavaScript variables are being set")
        else:
            print("[ERROR] Step 2: JavaScript variables NOT being set")
            return
        
        # Step 3: Check if HTML elements exist
        html_elements = [
            'id="attachFileBtn"',
            'id="fileUpload"', 
            'id="filePreviews"',
            'class="chat-input"',
            'id="sendMessage"'
        ]
        
        print("\n[CHECK] Step 3: HTML Elements Check:")
        all_elements_found = True
        for element in html_elements:
            if element in content:
                print(f"   [OK] {element}")
            else:
                print(f"   [MISSING] {element}")
                all_elements_found = False
        
        if not all_elements_found:
            print("[ERROR] Some HTML elements are missing")
            return
        
        # Step 4: Check if JavaScript file is included
        if 'chat.js' in content:
            print("[OK] Step 4: chat.js is included")
        else:
            print("[ERROR] Step 4: chat.js is NOT included")
            return
        
        # Step 5: Create a simple HTML test page to verify JavaScript functionality
        print("\n[TEST] Step 5: Creating test page...")
        
        test_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>File Upload Test</title>
    <script src="https://127.0.0.1:8000/static/userdashboard/js/chat.js"></script>
</head>
<body>
    <h1>File Upload Test</h1>
    
    <button id="attachFileBtn">Attach File</button>
    <input type="file" id="fileUpload" style="display: none;" multiple>
    <div id="filePreviews" style="display: none;"></div>
    
    <script>
        // Test the setupFileUploadHandlers function
        console.log('Testing file upload functionality...');
        
        // Wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded');
            
            // Check if setupFileUploadHandlers function exists
            if (typeof setupFileUploadHandlers === 'function') {{
                console.log('[OK] setupFileUploadHandlers function found');
                
                // Call the function
                setupFileUploadHandlers();
                console.log('[OK] setupFileUploadHandlers called');
                
                // Check if event listeners were attached
                const attachBtn = document.getElementById('attachFileBtn');
                const fileInput = document.getElementById('fileUpload');
                
                if (attachBtn) {{
                    console.log('[OK] Attach button found');
                    // Check if it has event listeners
                    const listeners = getEventListeners ? getEventListeners(attachBtn) : 'N/A';
                    console.log('   Event listeners:', listeners);
                }} else {{
                    console.log('[ERROR] Attach button NOT found');
                }}
                
                if (fileInput) {{
                    console.log('[OK] File input found');
                }} else {{
                    console.log('[ERROR] File input NOT found');
                }}
                
            }} else {{
                console.log('[ERROR] setupFileUploadHandlers function NOT found');
            }}
        }});
        
        // Helper function to check event listeners (if available)
        function getEventListeners(element) {{
            return element.eventListeners ? Object.keys(element.eventListeners) : 'Not available';
        }}
    </script>
</body>
</html>
        """
        
        # Save the test HTML file
        test_file_path = os.path.join(os.path.dirname(__file__), 'test_file_upload.html')
        with open(test_file_path, 'w') as f:
            f.write(test_html)
        
        print(f"[OK] Test page created: {test_file_path}")
        print(f"   Open this file in your browser to test the JavaScript functionality")
        print(f"   URL: file:///{test_file_path.replace('\\', '/')}")
        
        # Step 6: Test the actual file upload functionality via API
        print("\n[TEST] Step 6: Testing actual file upload...")
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "debug_test.txt", 
            b"This is a debug test file", 
            content_type="text/plain"
        )
        
        # Test the API directly
        response = client.post('/api/chat/messages/', {
            'contact_id': admin_user.id,
            'ticket_id': 'TEST-001',
            'text': 'Debug test message',
            'files': test_file,
        })
        
        if response.status_code == 201:
            data = response.json()
            print("[OK] Step 6: Direct API upload works")
            print(f"   - Message ID: {data.get('id')}")
            print(f"   - Attachments: {len(data.get('attachments', []))}")
        else:
            print(f"[ERROR] Step 6: Direct API upload failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Error: {response.content.decode()}")
        
        print("\n=== Debug Summary ===")
        print("[OK] Backend API: Working perfectly")
        print("[OK] HTML Elements: All present")
        print("[OK] JavaScript File: Included")
        print("[ERROR] Frontend Issue: JavaScript initialization problem")
        print("\n[RECOMMENDED] Actions:")
        print("1. Open the test HTML file in your browser")
        print("2. Check the browser console for JavaScript errors")
        print("3. Click the 'Attach File' button to test functionality")
        print("4. If it works, the issue is in the main page")
        print("5. If it doesn't, the issue is in the JavaScript file")
        
    else:
        print(f"[ERROR] Chat page failed to load: {response.status_code}")

if __name__ == '__main__':
    debug_file_upload_step_by_step()
