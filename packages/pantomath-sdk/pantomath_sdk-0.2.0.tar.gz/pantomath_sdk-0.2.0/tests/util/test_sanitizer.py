import pantomath_sdk as util


def test_normalizeHost():
    assert util.normalize_host("test/") == "test"


def test_sanitize_string():
    assert util.sanitize_string(" ") == "%20"
    assert util.sanitize_string(" \t") == "%20%09"
