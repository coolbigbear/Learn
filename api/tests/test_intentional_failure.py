
def test_intentional_failure():
    """This test intentionally fails to verify CI failure detection."""
    assert False, "This is an intentional failure to test CI failure handling"
