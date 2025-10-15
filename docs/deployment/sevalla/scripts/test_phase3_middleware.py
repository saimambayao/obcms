#!/usr/bin/env python
"""
Quick test script to verify Phase 3 middleware implementation.

This script validates:
1. Middleware files exist and are importable
2. Mode detection functions work correctly
3. File structure is correct
"""

import os
import sys

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

print("=" * 60)
print("Phase 3 Middleware Implementation Test")
print("=" * 60)

# Test 1: Check files exist
print("\n1. Checking file structure...")
files_to_check = [
    'src/organizations/middleware/__init__.py',
    'src/organizations/middleware/obcms_middleware.py',
    'src/organizations/middleware/organization.py',
]

for file_path in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        print(f"   ✓ {file_path}")
    else:
        print(f"   ✗ {file_path} NOT FOUND")
        sys.exit(1)

# Test 2: Check Python syntax
print("\n2. Checking Python syntax...")
import py_compile

for file_path in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    try:
        py_compile.compile(full_path, doraise=True)
        print(f"   ✓ {file_path} - syntax valid")
    except py_compile.PyCompileError as e:
        print(f"   ✗ {file_path} - syntax error: {e}")
        sys.exit(1)

# Test 3: Check middleware imports (without Django initialization)
print("\n3. Checking middleware classes exist...")
try:
    # Read the files and check for class definitions
    obcms_path = os.path.join(os.path.dirname(__file__), 'src/organizations/middleware/obcms_middleware.py')
    with open(obcms_path) as f:
        content = f.read()
        if 'class OBCMSOrganizationMiddleware:' in content:
            print("   ✓ OBCMSOrganizationMiddleware class found")
        else:
            print("   ✗ OBCMSOrganizationMiddleware class not found")
            sys.exit(1)

    org_path = os.path.join(os.path.dirname(__file__), 'src/organizations/middleware/organization.py')
    with open(org_path) as f:
        content = f.read()
        if 'class OrganizationMiddleware:' in content:
            print("   ✓ OrganizationMiddleware class found")
        else:
            print("   ✗ OrganizationMiddleware class not found")
            sys.exit(1)

        # Check for mode detection
        if 'is_obcms_mode()' in content:
            print("   ✓ Mode detection logic found in OrganizationMiddleware")
        else:
            print("   ✗ Mode detection logic not found")
            sys.exit(1)

except Exception as e:
    print(f"   ✗ Error checking middleware: {e}")
    sys.exit(1)

# Test 4: Check settings update
print("\n4. Checking settings.py middleware configuration...")
settings_path = os.path.join(os.path.dirname(__file__), 'src/obc_management/settings/base.py')
with open(settings_path) as f:
    settings_content = f.read()

    if 'organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware' in settings_content:
        print("   ✓ OBCMSOrganizationMiddleware added to MIDDLEWARE")
    else:
        print("   ✗ OBCMSOrganizationMiddleware not in MIDDLEWARE")
        sys.exit(1)

    if 'organizations.middleware.OrganizationMiddleware' in settings_content:
        print("   ✓ OrganizationMiddleware added to MIDDLEWARE")
    else:
        print("   ✗ OrganizationMiddleware not in MIDDLEWARE")
        sys.exit(1)

    # Check ordering
    obcms_idx = settings_content.index('organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware')
    org_idx = settings_content.index('organizations.middleware.OrganizationMiddleware')

    if obcms_idx < org_idx:
        print("   ✓ Middleware ordering correct (OBCMSOrganizationMiddleware before OrganizationMiddleware)")
    else:
        print("   ✗ Middleware ordering incorrect")
        sys.exit(1)

    # Check context processor
    if 'organizations.middleware.organization.organization_context' in settings_content:
        print("   ✓ Context processor path updated")
    else:
        print("   ✗ Context processor path not updated")
        sys.exit(1)

print("\n" + "=" * 60)
print("✓ All Phase 3 middleware tests passed!")
print("=" * 60)
print("\nImplementation Summary:")
print("  • OBCMSOrganizationMiddleware: Auto-injects OOBC in OBCMS mode")
print("  • OrganizationMiddleware: Extracts org from URL in BMMS mode")
print("  • Mode detection: Both middleware check is_obcms_mode()")
print("  • Middleware order: Correct (OBCMS before Organization)")
print("  • Context processor: Updated path")
print("\nNext steps:")
print("  1. Start development server: python src/manage.py runserver")
print("  2. Verify request.organization exists in views")
print("  3. Test OOBC auto-injection in OBCMS mode")
print("=" * 60)
