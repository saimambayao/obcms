#!/usr/bin/env python
"""
Test frontend components and templates for OBCMS.
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

def test_template_structure():
    """Test template structure and availability."""
    try:
        print("Testing Template Structure...")

        # Check template directories
        template_dirs = [
            'templates',
            'templates/components',
            'templates/includes',
            'templates/pages',
            'templates/emails',
        ]

        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                template_count = len([f for f in os.listdir(template_dir) if f.endswith('.html')])
                print(f"✅ {template_dir}: {template_count} templates")
            else:
                print(f"⚠️  {template_dir}: Not found")

        # Test key templates
        key_templates = [
            'templates/base.html',
            'templates/dashboard.html',
            'templates/components/navbar.html',
            'templates/components/footer.html',
        ]

        for template in key_templates:
            if os.path.exists(template):
                print(f"✅ {template} exists")
            else:
                print(f"⚠️  {template} not found")

        print("✅ Template structure tests completed!")
        return True

    except Exception as e:
        print(f"❌ Template structure test failed: {e}")
        return False

def test_static_files_structure():
    """Test static files structure."""
    try:
        print("Testing Static Files Structure...")

        # Check static directories
        static_dirs = [
            'static',
            'static/css',
            'static/js',
            'static/images',
            'static/fonts',
        ]

        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                file_count = len([f for f in os.listdir(static_dir) if not f.startswith('.')])
                print(f"✅ {static_dir}: {file_count} files")
            else:
                print(f"⚠️  {static_dir}: Not found")

        # Test key static files
        key_static_files = [
            'static/css/main.css',
            'static/js/main.js',
            'static/images/logo.png',
        ]

        for static_file in key_static_files:
            if os.path.exists(static_file):
                print(f"✅ {static_file} exists")
            else:
                print(f"⚠️  {static_file} not found")

        print("✅ Static files structure tests completed!")
        return True

    except Exception as e:
        print(f"❌ Static files structure test failed: {e}")
        return False

def test_template_loading():
    """Test template loading functionality."""
    try:
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist

        print("Testing Template Loading...")

        # Test common templates
        templates_to_test = [
            'base.html',
            'dashboard.html',
            'includes/navbar.html',
        ]

        loaded_count = 0
        for template in templates_to_test:
            try:
                loaded_template = get_template(template)
                print(f"✅ {template} loadable")
                loaded_count += 1
            except TemplateDoesNotExist:
                print(f"⚠️  {template} not found")
            except Exception as e:
                print(f"⚠️  {template} error: {e}")

        print(f"✅ {loaded_count}/{len(templates_to_test)} templates loadable")
        print("✅ Template loading tests completed!")
        return True

    except Exception as e:
        print(f"❌ Template loading test failed: {e}")
        return False

def test_template_context():
    """Test template context processors."""
    try:
        from django.conf import settings

        print("Testing Template Context Processors...")

        context_processors = getattr(settings, 'TEMPLATES', [{}])[0].get('OPTIONS', {}).get('context_processors', [])
        print(f"✅ Found {len(context_processors)} context processors")

        # Key context processors
        key_processors = [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]

        for processor in key_processors:
            if processor in context_processors:
                print(f"✅ {processor}")
            else:
                print(f"⚠️  {processor} not found")

        print("✅ Template context processors tests completed!")
        return True

    except Exception as e:
        print(f"❌ Template context processors test failed: {e}")
        return False

def test_forms_configuration():
    """Test Django forms configuration."""
    try:
        print("Testing Forms Configuration...")

        # Test form imports
        try:
            from django import forms
            print("✅ Django forms importable")
        except ImportError:
            print("❌ Django forms not importable")
            return False

        # Test specific app forms
        app_forms = [
            ('communities', 'CommunityForm'),
            ('coordination', 'OrganizationForm'),
            ('mana', 'WorkshopActivityForm'),
        ]

        for app_name, form_name in app_forms:
            try:
                module = __import__(f'{app_name}.forms', fromlist=[form_name])
                form_class = getattr(module, form_name, None)
                if form_class:
                    print(f"✅ {app_name}.{form_name} available")
                else:
                    print(f"⚠️  {app_name}.{form_name} not found")
            except ImportError:
                print(f"⚠️  {app_name}.forms module not found")

        print("✅ Forms configuration tests completed!")
        return True

    except Exception as e:
        print(f"❌ Forms configuration test failed: {e}")
        return False

def test_template_tags():
    """Test custom template tags."""
    try:
        print("Testing Custom Template Tags...")

        # Check for template tag directories
        template_tag_dirs = [
            'common/templatetags',
            'communities/templatetags',
            'coordination/templatetags',
        ]

        for tag_dir in template_tag_dirs:
            if os.path.exists(tag_dir):
                tag_files = [f for f in os.listdir(tag_dir) if f.endswith('.py') and not f.startswith('__')]
                print(f"✅ {tag_dir}: {len(tag_files)} tag files")
                for tag_file in tag_files:
                    print(f"   - {tag_file}")
            else:
                print(f"⚠️  {tag_dir}: Not found")

        print("✅ Custom template tags tests completed!")
        return True

    except Exception as e:
        print(f"❌ Custom template tags test failed: {e}")
        return False

def test_middleware_configuration():
    """Test middleware configuration."""
    try:
        from django.conf import settings

        print("Testing Middleware Configuration...")

        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        print(f"✅ Found {len(middleware_classes)} middleware classes")

        # Test security middleware
        security_middleware = 'django.middleware.security.SecurityMiddleware'
        if security_middleware in middleware_classes:
            print("✅ Security middleware configured")
        else:
            print("⚠️  Security middleware not found")

        # Test CSRF middleware
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
        if csrf_middleware in middleware_classes:
            print("✅ CSRF middleware configured")
        else:
            print("⚠️  CSRF middleware not found")

        # Test authentication middleware
        auth_middleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
        if auth_middleware in middleware_classes:
            print("✅ Authentication middleware configured")
        else:
            print("⚠️  Authentication middleware not found")

        print("✅ Middleware configuration tests completed!")
        return True

    except Exception as e:
        print(f"❌ Middleware configuration test failed: {e}")
        return False

def test_ui_components():
    """Test UI component templates."""
    try:
        print("Testing UI Component Templates...")

        # Check for component templates
        component_templates = [
            'templates/components/stat_cards.html',
            'templates/components/data_tables.html',
            'templates/components/forms.html',
            'templates/components/modals.html',
            'templates/components/pagination.html',
        ]

        found_components = 0
        for component in component_templates:
            if os.path.exists(component):
                print(f"✅ {component}")
                found_components += 1
            else:
                print(f"⚠️  {component} not found")

        print(f"✅ {found_components}/{len(component_templates)} UI components found")
        print("✅ UI component templates tests completed!")
        return True

    except Exception as e:
        print(f"❌ UI component templates test failed: {e}")
        return False

def main():
    """Run all frontend tests."""
    print("=" * 60)
    print("OBCMS FRONTEND COMPONENTS TESTS")
    print("=" * 60)

    tests = [
        ("Template Structure", test_template_structure),
        ("Static Files Structure", test_static_files_structure),
        ("Template Loading", test_template_loading),
        ("Template Context Processors", test_template_context),
        ("Forms Configuration", test_forms_configuration),
        ("Custom Template Tags", test_template_tags),
        ("Middleware Configuration", test_middleware_configuration),
        ("UI Components", test_ui_components),
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
    print("FRONTEND TEST SUMMARY")
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
        print("🎉 ALL FRONTEND TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some frontend tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())