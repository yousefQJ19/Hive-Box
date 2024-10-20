"""
testing
"""
from app import version

def test_version():
    """
        tests the version
    """
    assert version() == 'v0.0.1'
