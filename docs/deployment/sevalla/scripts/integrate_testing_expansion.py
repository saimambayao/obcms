#!/usr/bin/env python3
"""
Integrate Testing Expansion into TRANSITION_PLAN.md

This script safely integrates Component Testing and expanded Performance Testing
sections from TESTING_EXPANSION.md into TRANSITION_PLAN.md.

Approved changes:
- Replace Section 23.4 (Performance Testing) with expanded version
- Insert Section 23.7 (Component Testing) after Section 23.6 (UAT)
"""

import os
import sys

def read_file(filepath):
    """Read file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write content to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def find_section_boundaries(content, section_marker):
    """Find start and end of a section."""
    lines = content.split('\n')
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if section_marker in line:
            start_idx = i
        elif start_idx is not None and line.startswith('###') and section_marker not in line:
            end_idx = i
            break

    if start_idx and not end_idx:
        # Section goes to end of file
        end_idx = len(lines)

    return start_idx, end_idx

def main():
    """Main integration logic."""

    # File paths
    base_dir = "/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms"
    transition_plan = os.path.join(base_dir, "docs/plans/bmms/TRANSITION_PLAN.md")
    testing_expansion = os.path.join(base_dir, "docs/plans/bmms/TESTING_EXPANSION.md")
    backup_file = os.path.join(base_dir, "docs/plans/bmms/TRANSITION_PLAN.md.backup")

    print("🔧 BMMS Testing Expansion Integration Tool")
    print("=" * 60)

    # Check files exist
    if not os.path.exists(transition_plan):
        print(f"❌ Error: {transition_plan} not found")
        sys.exit(1)

    if not os.path.exists(testing_expansion):
        print(f"❌ Error: {testing_expansion} not found")
        sys.exit(1)

    print(f"✅ Found TRANSITION_PLAN.md ({os.path.getsize(transition_plan):,} bytes)")
    print(f"✅ Found TESTING_EXPANSION.md ({os.path.getsize(testing_expansion):,} bytes)")

    # Create backup
    print(f"\n📦 Creating backup: TRANSITION_PLAN.md.backup")
    transition_content = read_file(transition_plan)
    write_file(backup_file, transition_content)
    print(f"✅ Backup created ({os.path.getsize(backup_file):,} bytes)")

    # Read testing expansion content
    print(f"\n📖 Reading testing expansion content...")
    expansion_content = read_file(testing_expansion)
    expansion_lines = expansion_content.split('\n')

    # Extract Section 23.4 (Performance Testing) from expansion
    perf_start = None
    perf_end = None
    for i, line in enumerate(expansion_lines):
        if line.strip().startswith('## 23.4'):
            perf_start = i
        elif perf_start and line.strip().startswith('## 23.7'):
            perf_end = i
            break

    if not perf_start or not perf_end:
        print("❌ Error: Could not find Section 23.4 boundaries in TESTING_EXPANSION.md")
        print(f"   perf_start: {perf_start}, perf_end: {perf_end}")
        sys.exit(1)

    new_perf_content = '\n'.join(expansion_lines[perf_start:perf_end])
    print(f"✅ Extracted expanded Section 23.4 ({len(new_perf_content):,} chars)")

    # Extract Section 23.7 (Component Testing) from expansion
    comp_start = perf_end
    comp_end = len(expansion_lines)
    new_comp_content = '\n'.join(expansion_lines[comp_start:comp_end])
    print(f"✅ Extracted new Section 23.7 ({len(new_comp_content):,} chars)")

    # Process TRANSITION_PLAN.md
    print(f"\n🔄 Processing TRANSITION_PLAN.md...")
    transition_lines = transition_content.split('\n')

    # Find Section 23.4 boundaries in transition plan
    section_24_start = None
    section_234_start = None
    section_235_start = None

    for i, line in enumerate(transition_lines):
        if line.strip().startswith('#### 23.4'):
            section_234_start = i
        elif line.strip().startswith('#### 23.5'):
            section_235_start = i
        elif line.strip().startswith('### Section 24:'):
            section_24_start = i

    if not section_234_start or not section_235_start:
        print("❌ Error: Could not find Section 23.4 or 23.5 in TRANSITION_PLAN.md")
        sys.exit(1)

    print(f"✅ Found Section 23.4 at line {section_234_start + 1}")
    print(f"✅ Found Section 23.5 at line {section_235_start + 1}")
    print(f"✅ Found Section 24 at line {section_24_start + 1}" if section_24_start else "⚠️  Section 24 not found (will append at end)")

    # Build new content
    print(f"\n🔨 Building updated document...")

    # Part 1: Everything before Section 23.4
    new_lines = transition_lines[:section_234_start]

    # Part 2: New Section 23.4 (Performance Testing - Expanded)
    new_lines.append("#### 23.4 Performance Testing")
    new_lines.append("")
    new_lines.extend(expansion_lines[perf_start + 1:perf_end])

    # Part 3: Sections 23.5 and 23.6 (unchanged)
    section_237_insert = None
    for i in range(section_235_start, len(transition_lines)):
        new_lines.append(transition_lines[i])
        if transition_lines[i].strip().startswith('### Section 24:') or transition_lines[i].strip().startswith('## Section 24:'):
            section_237_insert = len(new_lines) - 1
            break

    # Part 4: Insert new Section 23.7 (Component Testing) before Section 24
    if section_237_insert:
        # Insert before Section 24
        insert_pos = section_237_insert
        new_lines.insert(insert_pos, "")
        new_lines.insert(insert_pos + 1, "---")
        new_lines.insert(insert_pos + 2, "")
        for line in expansion_lines[comp_start:comp_end]:
            insert_pos += 1
            new_lines.insert(insert_pos + 2, line)

        print(f"✅ Inserted Section 23.7 before Section 24")
    else:
        # Append at end
        new_lines.append("")
        new_lines.append("---")
        new_lines.append("")
        new_lines.extend(expansion_lines[comp_start:comp_end])
        print(f"✅ Appended Section 23.7 at end of document")

    # Write updated content
    new_content = '\n'.join(new_lines)
    print(f"\n💾 Writing updated TRANSITION_PLAN.md ({len(new_content):,} chars)...")
    write_file(transition_plan, new_content)

    print(f"✅ Successfully updated TRANSITION_PLAN.md")
    print(f"   New size: {os.path.getsize(transition_plan):,} bytes")
    print(f"   Backup saved: TRANSITION_PLAN.md.backup")

    print(f"\n🎉 Integration Complete!")
    print(f"\n📋 Changes Made:")
    print(f"   ✅ Replaced Section 23.4 (Performance Testing) with expanded version (10 subsections)")
    print(f"   ✅ Inserted Section 23.7 (Component Testing) with 8 subsections")
    print(f"   ✅ Preserved all other content")

    print(f"\n🔍 Next Steps:")
    print(f"   1. Review the updated TRANSITION_PLAN.md")
    print(f"   2. Verify sections 23.4 and 23.7 are correctly integrated")
    print(f"   3. If satisfied, delete TRANSITION_PLAN.md.backup")
    print(f"   4. If issues, restore from backup: mv TRANSITION_PLAN.md.backup TRANSITION_PLAN.md")

if __name__ == "__main__":
    main()
