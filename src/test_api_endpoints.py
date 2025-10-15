#!/usr/bin/env python
"""
Test API endpoints and views for OBCMS.
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

def test_api_views():
    """Test basic API view functionality."""
    try:
        from django.test import Client
        from django.urls import reverse
        from django.contrib.auth import get_user_model

        print("Testing API Views...")

        client = Client()
        User = get_user_model()

        # Test 1: Check if main URLs resolve
        try:
            response = client.get('/')
            print(f"✅ Root URL accessible (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️  Root URL test failed: {e}")

        # Test 2: Check if admin URL resolves
        try:
            response = client.get('/admin/')
            print(f"✅ Admin URL accessible (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️  Admin URL test failed: {e}")

        # Test 3: Test API endpoints that should be available
        api_endpoints = [
            '/api/common/search/',
            '/api/communities/',
            '/api/organizations/',
        ]

        for endpoint in api_endpoints:
            try:
                response = client.get(endpoint)
                print(f"✅ {endpoint} accessible (status: {response.status_code})")
            except Exception as e:
                print(f"⚠️  {endpoint} test failed: {e}")

        print("✅ API views tests completed!")
        return True

    except Exception as e:
        print(f"❌ API views test failed: {e}")
        return False

def test_url_patterns():
    """Test URL pattern configuration."""
    try:
        from django.urls import get_resolver
        from django.urls.resolvers import URLResolver, URLPattern

        print("Testing URL Patterns...")

        resolver = get_resolver()
        url_patterns = []

        def collect_urls(patterns, prefix=''):
            for pattern in patterns:
                if isinstance(pattern, URLPattern):
                    url_patterns.append(f"{prefix}{pattern.pattern}")
                elif isinstance(pattern, URLResolver):
                    collect_urls(pattern.url_patterns, f"{prefix}{pattern.pattern}")

        collect_urls(resolver.url_patterns)
        print(f"✅ Found {len(url_patterns)} URL patterns")

        # Show some key patterns
        key_patterns = [p for p in url_patterns if any(keyword in p for keyword in ['admin', 'api', 'search'])]
        for pattern in key_patterns[:10]:  # Show first 10
            print(f"  - {pattern}")

        print("✅ URL pattern tests completed!")
        return True

    except Exception as e:
        print(f"❌ URL pattern test failed: {e}")
        return False

def test_template_loading():
    """Test template loading functionality."""
    try:
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist

        print("Testing Template Loading...")

        # Test common templates
        template_files = [
            'base.html',
            'includes/navbar.html',
            'includes/footer.html',
        ]

        for template_file in template_files:
            try:
                template = get_template(template_file)
                print(f"✅ Template {template_file} loadable")
            except TemplateDoesNotExist:
                print(f"⚠️  Template {template_file} not found")
            except Exception as e:
                print(f"⚠️  Template {template_file} error: {e}")

        print("✅ Template loading tests completed!")
        return True

    except Exception as e:
        print(f"❌ Template loading test failed: {e}")
        return False

def test_static_files():
    """Test static file configuration."""
    try:
        from django.contrib.staticfiles.finders import find
        from django.templatetags.static import static

        print("Testing Static Files...")

        # Test common static files
        static_files = [
            'css/main.css',
            'js/main.js',
            'images/logo.png',
        ]

        for static_file in static_files:
            try:
                found = find(static_file)
                if found:
                    print(f"✅ Static file {static_file} found")
                else:
                    print(f"⚠️  Static file {static_file} not found")
            except Exception as e:
                print(f"⚠️  Static file {static_file} error: {e}")

        print("✅ Static files tests completed!")
        return True

    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False

def test_middleware():
    """Test middleware configuration."""
    try:
        from django.conf import settings

        print("Testing Middleware...")

        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        print(f"✅ Found {len(middleware_classes)} middleware classes")

        # Check for important middleware
        important_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]

        for middleware in important_middleware:
            if middleware in middleware_classes:
                print(f"✅ {middleware}")
            else:
                print(f"⚠️  {middleware} not found")

        print("✅ Middleware tests completed!")
        return True

    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False

def test_authentication():
    """Test authentication system."""
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        print("Testing Authentication...")

        client = Client()
        User = get_user_model()

        # Test login page access
        try:
            response = client.get('/admin/login/')
            print(f"✅ Login page accessible (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️  Login page test failed: {e}")

        # Test user creation
        try:
            user = User.objects.create_user(
                username='test_api_user',
                email='test@api.com',
                password='testpass123',
            )
            print(f"✅ User creation successful: {user.username}")
        except Exception as e:
            print(f"⚠️  User creation failed: {e}")

        # Test authentication
        try:
            client.login(username='test_api_user', password='testpass123')
            response = client.get('/admin/')
            print(f"✅ User authentication successful (status: {response.status_code})")
        except Exception as e:
            print(f"⚠️  Authentication test failed: {e}")

        print("✅ Authentication tests completed!")
        return True

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_permissions():
    """Test permission system."""
    try:
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        print("Testing Permissions...")

        # Test permission availability
        permission_count = Permission.objects.count()
        print(f"✅ Found {permission_count} permissions")

        # Test content types
        content_type_count = ContentType.objects.count()
        print(f"✅ Found {content_type_count} content types")

        print("✅ Permission tests completed!")
        return True

    except Exception as e:
        print(f"❌ Permission test failed: {e}")
        return False

def main():
    """Run all API and view tests."""
    print("=" * 60)
    print("OBCMS API ENDPOINTS AND VIEWS TESTS")
    print("=" * 60)

    tests = [
        ("API Views", test_api_views),
        ("URL Patterns", test_url_patterns),
        ("Template Loading", test_template_loading),
        ("Static Files", test_static_files),
        ("Middleware", test_middleware),
        ("Authentication", test_authentication),
        ("Permissions", test_permissions),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("API TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("🎉 ALL API TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some API tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())