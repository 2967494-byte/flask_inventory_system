from app import create_app, db
from app.models import User
from flask_login import login_user
from flask import request
from werkzeug.datastructures import ImmutableMultiDict

app = create_app()
app.app_context().push()

# Get admin user
admin = User.query.filter_by(email='admin@example.com').first()
if admin:
    print(f"Testing with user: {admin.email} (ID: {admin.id})")
    
    # Test 1: Direct access to /messages/sent?iframe=1
    print("\n=== Test 1: Direct iframe access ===")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['_fresh'] = True
        
        response = client.get('/messages/sent?iframe=1')
        print(f"Status: {response.status_code}")
        
        # Check if the response contains sidebar
        content = response.data.decode('utf-8', errors='ignore')
        if 'col-md-3' in content:
            print("❌ ISSUE: Sidebar still present in iframe mode")
            # Find the sidebar section
            import re
            sidebar_match = re.search(r'<div class="col-md-3">.*?</div>', content, re.DOTALL)
            if sidebar_match:
                print(f"Sidebar content found: {sidebar_match.group()[:200]}...")
        else:
            print("✅ GOOD: No sidebar found in iframe mode")
            
        # Check if it's using iframe base template
        if 'base_iframe.html' in content or 'iframe-container' in content:
            print("✅ GOOD: Using iframe template")
        else:
            print("❌ ISSUE: Not using iframe template")
            
        # Check content width
        if 'col-12' in content:
            print("✅ GOOD: Using full width content")
        elif 'col-md-9' in content:
            print("❌ ISSUE: Still using col-md-9 (not full width)")
            
    # Test 2: Check what happens with dashboard context
    print("\n=== Test 2: Dashboard simulation ===")
    with app.test_request_context('/dashboard/messages?subsection=sent'):
        login_user(admin)
        
        # Simulate what the dashboard does
        from flask import url_for
        subsection = 'sent'
        iframe_src = url_for('messages.' + subsection, iframe=1)
        print(f"Dashboard would load iframe with src: {iframe_src}")

else:
    print('Admin user not found')
