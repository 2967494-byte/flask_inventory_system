"""Test script to check dashboard page with authentication"""

from flask import url_for

from app import create_app
from app.models import User

app = create_app()
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False

with app.app_context():
    # Get first user for testing
    user = User.query.first()

    if not user:
        print("ERROR: No users found in database")
        exit(1)

    print(f"Testing with user: {user.email} (ID: {user.id})")
    print("=" * 80)

    # Create test client
    client = app.test_client()

    # Login
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)

    print("\nTesting /dashboard route...")
    print("-" * 80)

    try:
        response = client.get("/dashboard")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ Dashboard loaded successfully")

            # Check if response contains expected content
            data = response.data.decode("utf-8")

            checks = [
                ("Мои объявления" in data or "объявлен" in data, "Title present"),
                ("db-container" in data, "Dashboard container present"),
                ("db-sidebar" in data, "Sidebar present"),
                ("db-main" in data, "Main content present"),
            ]

            print("\nContent checks:")
            for check, description in checks:
                status = "✓" if check else "✗"
                print(f"  {status} {description}")

        elif response.status_code == 302:
            print(f"✗ Redirected to: {response.location}")
        elif response.status_code == 500:
            print("✗ Internal Server Error")
            print("\nResponse data:")
            print(response.data.decode("utf-8")[:1000])
        else:
            print(f"✗ Unexpected status code: {response.status_code}")

    except Exception as e:
        print(f"✗ Exception occurred: {type(e).__name__}")
        print(f"   Error: {str(e)}")

        # Print full traceback
        import traceback

        print("\nFull traceback:")
        print("-" * 80)
        traceback.print_exc()

print("\n" + "=" * 80)
