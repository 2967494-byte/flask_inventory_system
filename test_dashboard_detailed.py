"""Detailed test script to check dashboard page and capture full error"""

import sys
import traceback

from flask import url_for

from app import create_app
from app.models import User

app = create_app()
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False

print("=" * 80)
print("DETAILED DASHBOARD TEST")
print("=" * 80)

with app.app_context():
    # Get first user for testing
    user = User.query.first()

    if not user:
        print("ERROR: No users found in database")
        sys.exit(1)

    print(f"\nTesting with user: {user.email} (ID: {user.id})")
    print("-" * 80)

    # Create test client
    client = app.test_client()

    # Login by setting session
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    print("\n[1] Testing GET /dashboard")
    print("-" * 80)

    try:
        # Make request
        response = client.get("/dashboard", follow_redirects=True)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        print(f"Content-Length: {len(response.data)} bytes")

        if response.status_code == 200:
            print("\n[SUCCESS] Dashboard loaded successfully!")

            # Decode response
            data = response.data.decode("utf-8", errors="ignore")

            # Check for expected content
            print("\n[2] Content validation:")
            print("-" * 80)

            checks = [
                (
                    "<!DOCTYPE html>" in data or "<!doctype html>" in data,
                    "HTML doctype",
                ),
                ("db-container" in data, "Dashboard container class"),
                ("db-sidebar" in data, "Sidebar component"),
                ("db-main" in data, "Main content area"),
                ("Мои объявления" in data or "объявлен" in data, "Page title"),
                ("dashboard_sidebar" in data or "nav-link" in data, "Navigation links"),
            ]

            for check, description in checks:
                status = "[OK]" if check else "[FAIL]"
                print(f"{status} {description}")

            # Show first 500 chars of response
            print("\n[3] Response preview (first 500 chars):")
            print("-" * 80)
            print(data[:500])
            print("...")

        elif response.status_code == 500:
            print("\n[ERROR] Internal Server Error (500)")
            print("-" * 80)

            # Try to decode response
            try:
                data = response.data.decode("utf-8", errors="ignore")
                print("\nResponse content:")
                print(data[:2000])  # First 2000 chars

                # Look for error message in HTML
                if "Traceback" in data:
                    print("\n[FOUND TRACEBACK IN RESPONSE]")
                if "Error" in data:
                    print("\n[ERROR MESSAGE FOUND]")

            except Exception as e:
                print(f"Could not decode response: {e}")

        elif response.status_code == 302:
            print(f"\n[REDIRECT] Redirected to: {response.location}")

        else:
            print(f"\n[UNEXPECTED] Status code: {response.status_code}")

    except Exception as e:
        print(f"\n[EXCEPTION] {type(e).__name__}: {str(e)}")
        print("\n[FULL TRACEBACK]")
        print("=" * 80)
        traceback.print_exc()
        print("=" * 80)

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
