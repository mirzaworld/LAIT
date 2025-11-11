"""Legacy invoice routes (deprecated)

This module was an older, non-blueprint implementation of invoice endpoints.
The application now exposes invoice functionality via the `invoices_bp` blueprint
in `backend/routes/invoices.py` (the canonical, actively maintained module).

This file remains for historical reference only and should not be imported or
registered in the running application. Duplicate route definitions can cause
priority/behavioral conflicts.
"""

def legacy_placeholder():
    """Return a short message indicating this file is deprecated."""
    return {
        'status': 'deprecated',
        'message': 'Use backend/routes/invoices.py (invoices_bp) instead.'
    }
