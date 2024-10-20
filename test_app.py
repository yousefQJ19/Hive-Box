from app import version

def test_version():
    assert version() == 'v0.0.1'
