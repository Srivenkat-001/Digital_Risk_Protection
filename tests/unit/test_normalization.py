"""
Unit tests for text, handle, URL, and package ID normalization.
"""

from detection.normalization import (
    extract_domain,
    normalize_handle,
    normalize_package_id,
    normalize_text,
    normalize_url,
)


def test_normalize_text():
    assert normalize_text("  NovaPay   Global  ") == "novapay global"
    assert normalize_text("") == ""
    assert normalize_text(None) == ""

def test_normalize_handle():
    assert normalize_handle("@NovaPayOfficial") == "novapayofficial"
    assert normalize_handle("  @Nova_Pay.123! ") == "nova_pay.123"
    assert normalize_handle("") == ""

def test_normalize_url():
    assert normalize_url("https://www.novapay.io/about/") == "novapay.io/about"
    assert normalize_url("http://novapay.io/") == "novapay.io"
    assert normalize_url("NOVAPAY.IO") == "novapay.io"
    assert normalize_url("https://[::1") == ""
    assert normalize_url("javascript:alert(1)") == ""
    assert normalize_url("https://user:pass@example.com") == ""
    assert normalize_url(123) == ""

def test_normalize_package_id():
    assert normalize_package_id("  com.NovaPay.Wallet  ") == "com.novapay.wallet"
    assert normalize_package_id("") == ""

def test_extract_domain():
    assert extract_domain("https://checkout.novapay.io/pay") == "checkout.novapay.io"
    assert extract_domain("www.novapay.io") == "novapay.io"
    assert extract_domain("https://[::1") == ""
