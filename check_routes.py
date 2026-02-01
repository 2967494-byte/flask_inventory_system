"""Script to check all registered routes in the Flask application"""

from app import create_app

app = create_app()

print("=" * 80)
print("REGISTERED ROUTES")
print("=" * 80)

# Get all routes
routes = []
for rule in app.url_map.iter_rules():
    routes.append(
        {
            "endpoint": rule.endpoint,
            "methods": ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"})),
            "path": str(rule),
        }
    )

# Filter routes containing 'dashboard', 'favorites', 'profile', 'messages'
keywords = ["dashboard", "favorites", "profile", "messages"]

print("\nFiltered routes (dashboard-related):")
print("-" * 80)
for route in sorted(routes, key=lambda x: x["path"]):
    if any(
        keyword in route["path"].lower() or keyword in route["endpoint"].lower()
        for keyword in keywords
    ):
        print(f"{route['path']:<40} -> {route['endpoint']:<30} [{route['methods']}]")

print("\n" + "=" * 80)
print(f"Total routes found: {len(routes)}")
print("=" * 80)

# Check specific endpoints
print("\nChecking specific endpoints:")
print("-" * 80)
endpoints_to_check = [
    "main.dashboard",
    "main.favorites",
    "main.profile",
    "main.messages",
    "main.old_favorites_redirect",
    "main.old_profile_redirect",
    "main.old_messages_redirect",
]

for endpoint in endpoints_to_check:
    try:
        # Try to build URL for this endpoint
        with app.test_request_context():
            from flask import url_for

            url = url_for(endpoint)
            print(f"✓ {endpoint:<35} -> {url}")
    except Exception as e:
        print(f"✗ {endpoint:<35} -> ERROR: {str(e)}")

print("=" * 80)
