#!/usr/bin/env python3
"""
Automated Legacy Model Refactoring Script
Refactors StaffTask, Event, ProjectWorkflow → WorkItem

Usage:
    python3 refactor_legacy_models.py --dry-run  # Preview changes
    python3 refactor_legacy_models.py             # Apply changes
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple

# Base directory
BASE_DIR = Path(__file__).parent / "src"

# Files to EXCLUDE (migration commands need legacy imports)
EXCLUDE_FILES = [
    "src/common/management/commands/migrate_staff_tasks.py",
    "src/common/management/commands/migrate_events.py",
    "src/common/management/commands/migrate_project_workflows.py",
    "src/common/management/commands/migrate_to_workitem.py",
    "src/common/management/commands/verify_workitem_migration.py",
    "src/common/management/commands/populate_task_templates.py",
]

# Refactoring patterns
IMPORT_PATTERNS = [
    # StaffTask imports
    (
        r"from common\.models import (.*)StaffTask(.*)",
        lambda m: f"from common.models import {m.group(1)}WorkItem{m.group(2)}"
    ),
    # Event imports from coordination
    (
        r"from coordination\.models import (.*)Event([,\s].*|$)",
        lambda m: f"from coordination.models import {m.group(1)}{m.group(2)}"  # Keep other imports
    ),
    # ProjectWorkflow imports
    (
        r"from project_central\.models import (.*)ProjectWorkflow(.*)",
        lambda m: f"# REMOVED: from project_central.models import {m.group(1)}ProjectWorkflow{m.group(2)}"
    ),
]

# Model usage patterns
USAGE_PATTERNS = [
    # StaffTask.objects → WorkItem.objects.filter(work_type__in=[...])
    (
        r"StaffTask\.objects\.filter\(",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK], "
    ),
    (
        r"StaffTask\.objects\.all\(\)",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK])"
    ),
    (
        r"StaffTask\.objects\.get\(",
        "WorkItem.objects.get(work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK], "
    ),
    (
        r"StaffTask\.objects\.create\(",
        "WorkItem.objects.create(work_type=WorkItem.WORK_TYPE_TASK, "
    ),

    # Status constants
    (r"StaffTask\.STATUS_NOT_STARTED", "WorkItem.STATUS_NOT_STARTED"),
    (r"StaffTask\.STATUS_IN_PROGRESS", "WorkItem.STATUS_IN_PROGRESS"),
    (r"StaffTask\.STATUS_AT_RISK", "WorkItem.STATUS_AT_RISK"),
    (r"StaffTask\.STATUS_COMPLETED", "WorkItem.STATUS_COMPLETED"),
    (r"StaffTask\.STATUS_BLOCKED", "WorkItem.STATUS_BLOCKED"),
    (r"StaffTask\.STATUS_CANCELLED", "WorkItem.STATUS_CANCELLED"),

    # Priority constants
    (r"StaffTask\.PRIORITY_LOW", "WorkItem.PRIORITY_LOW"),
    (r"StaffTask\.PRIORITY_MEDIUM", "WorkItem.PRIORITY_MEDIUM"),
    (r"StaffTask\.PRIORITY_HIGH", "WorkItem.PRIORITY_HIGH"),
    (r"StaffTask\.PRIORITY_URGENT", "WorkItem.PRIORITY_URGENT"),
    (r"StaffTask\.PRIORITY_CRITICAL", "WorkItem.PRIORITY_CRITICAL"),

    # Choices
    (r"StaffTask\.STATUS_CHOICES", "WorkItem.STATUS_CHOICES"),
    (r"StaffTask\.PRIORITY_CHOICES", "WorkItem.PRIORITY_CHOICES"),

    # Event → WorkItem (activity)
    (
        r"Event\.objects\.filter\(",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY], "
    ),
    (
        r"Event\.objects\.all\(\)",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY])"
    ),
    (
        r"Event\.objects\.get\(",
        "WorkItem.objects.get(work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY], "
    ),
    (
        r"Event\.objects\.create\(",
        "WorkItem.objects.create(work_type=WorkItem.WORK_TYPE_ACTIVITY, "
    ),

    # ProjectWorkflow → WorkItem (project)
    (
        r"ProjectWorkflow\.objects\.filter\(",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT], "
    ),
    (
        r"ProjectWorkflow\.objects\.all\(\)",
        "WorkItem.objects.filter(work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT])"
    ),
    (
        r"ProjectWorkflow\.objects\.get\(",
        "WorkItem.objects.get(work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT], "
    ),
    (
        r"ProjectWorkflow\.objects\.create\(",
        "WorkItem.objects.create(work_type=WorkItem.WORK_TYPE_PROJECT, "
    ),
]


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped."""
    file_str = str(file_path)
    return any(excluded in file_str for excluded in EXCLUDE_FILES)


def find_files_with_legacy_imports() -> List[Path]:
    """Find all Python files with legacy model imports."""
    files = []
    for pattern in ["**/views/**/*.py", "**/services/**/*.py", "**/admin.py",
                    "**/serializers.py", "**/tasks.py", "**/forms.py", "**/models.py"]:
        files.extend(BASE_DIR.glob(pattern))

    # Remove duplicates and sort
    files = sorted(set(files))

    # Filter files that actually contain legacy imports
    files_with_imports = []
    for file_path in files:
        if should_skip_file(file_path):
            continue

        try:
            content = file_path.read_text()
            if any(pattern in content for pattern in ["from common.models import", "from coordination.models import", "from project_central.models import"]):
                if "StaffTask" in content or "Event" in content or "ProjectWorkflow" in content:
                    files_with_imports.append(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return files_with_imports


def refactor_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Refactor a single file."""
    try:
        content = file_path.read_text()
        original_content = content
        changes = []

        # Apply import patterns
        for pattern, replacement in IMPORT_PATTERNS:
            if isinstance(replacement, str):
                new_content = re.sub(pattern, replacement, content)
            else:
                new_content = re.sub(pattern, replacement, content)

            if new_content != content:
                changes.append(f"Import: {pattern}")
                content = new_content

        # Apply usage patterns
        for pattern, replacement in USAGE_PATTERNS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(f"Usage: {pattern} → {replacement[:50]}")
                content = new_content

        # Write back if changed and not dry run
        if content != original_content:
            if not dry_run:
                file_path.write_text(content)
            return True, "\n  ".join(changes)
        else:
            return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Refactor legacy models to WorkItem")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    args = parser.parse_args()

    print("=" * 80)
    print("LEGACY MODEL REFACTORING SCRIPT")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (applying changes)'}")
    print()

    # Find files
    print("Finding files with legacy imports...")
    files = find_files_with_legacy_imports()
    print(f"Found {len(files)} files to refactor\n")

    # Refactor each file
    success_count = 0
    no_change_count = 0
    error_count = 0

    for file_path in files:
        rel_path = file_path.relative_to(BASE_DIR.parent)
        changed, details = refactor_file(file_path, dry_run=args.dry_run)

        if changed:
            print(f"✓ {rel_path}")
            if details:
                print(f"  Changes: {details}")
            success_count += 1
        elif "Error" in details:
            print(f"✗ {rel_path}: {details}")
            error_count += 1
        else:
            no_change_count += 1

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files changed: {success_count}")
    print(f"Files unchanged: {no_change_count}")
    print(f"Errors: {error_count}")
    print()

    if args.dry_run:
        print("DRY RUN complete. Run without --dry-run to apply changes.")
    else:
        print("Refactoring complete!")
        print("\nNext steps:")
        print("1. Run: cd src && python3 -m py_compile common/views/*.py")
        print("2. Run: pytest src/common/tests/ -v")
        print("3. Review git diff to verify changes")


if __name__ == "__main__":
    main()
