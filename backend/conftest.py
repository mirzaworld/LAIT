"""
Top-level pytest configuration for backend test discovery.

This file prevents pytest from collecting helper/test-server scripts that exist
in the repository but are not intended as unit tests. Placing this at the
`backend/` root ensures pytest discovery ignores these modules before loading
`tests/conftest.py`.
"""
from pathlib import Path


def pytest_ignore_collect(path):
    p = Path(str(path))
    name = p.name
    # Ignore helper servers and legacy scripts that start with test_ but are not real tests
    ignore_names = {
        'test_server.py',
        'test_server_backup.py',
        'test_rate_limit.py',
        'component_test.cjs',
    }
    if name in ignore_names:
        return True
    return False
