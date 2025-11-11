"""Legacy invoice routes (archived)

This file contains an older, non-blueprint implementation of invoice
endpoints that used to be registered directly on the Flask `app` object.

The functionality has been migrated into `backend/routes/invoices.py` which
provides a blueprint (`invoices_bp`) and improved, tested implementations
for: listing invoices, invoice detail, upload (PDF parsing + ML analysis),
download, and related helpers.

Keep this file for history and reference during the migration. Do NOT import
or register it in the current application wiring; `invoices.py` is the
canonical implementation.
"""

from textwrap import dedent

ARCHIVAL_NOTE = dedent("""
This module was intentionally archived and should not be used by the
application. See `backend/routes/invoices.py` for the active blueprint-based
implementation of invoice endpoints.

If you need to recover any specific logic from the legacy routes, copy the
relevant functions from the original file in the git history rather than
re-adding this module to the app at runtime.
""")

def archived_note():
    return ARCHIVAL_NOTE
