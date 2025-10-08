#!/usr/bin/env python
"""
Export data from SQLite database to JSON
Run this inside Docker container
"""
import os
import sys
import django

# Set up Django with SQLite
os.environ['DJANGO_SETTINGS_MODULE'] = 'obc_management.settings'
os.environ['DATABASE_URL'] = 'sqlite:////app/src/db.sqlite3'

django.setup()

from django.core import management

print("Exporting data from SQLite...", file=sys.stderr)

management.call_command(
    'dumpdata',
    '--natural-foreign',
    '--natural-primary',
    '--exclude=contenttypes',
    '--exclude=auth.Permission',
    '--exclude=sessions.Session',
    '--exclude=admin.LogEntry',
    '--exclude=auditlog.LogEntry',
    '--indent=2',
    stdout=sys.stdout
)

print("\nExport complete!", file=sys.stderr)
