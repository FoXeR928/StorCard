import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

from src.core.certificate import init_ssl, generate_self_signed_cert

CERT_DIR_PATH = "src.core.certificate.CERTIFICATE_DIR"


def test_generate_self_signed_cert():
    """Проверяем, что сертификат создается с правильными полями."""
    common_name = "test.local"
    key, cert = generate_self_signed_cert(days=10, common_name=common_name)

    assert isinstance(key, rsa.RSAPrivateKey)
    assert isinstance(cert, x509.Certificate)
    assert (
        cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        == common_name
    )


@patch("src.core.certificate.CERTIFICATE_DIR")
@patch("src.core.system.stop_server")
def test_init_ssl_creates_files(mock_stop, mock_cert_dir, tmp_path):
    """Проверяем, что init_ssl создает файлы, если их нет."""
    cert_path = tmp_path / "ssl.pem"
    key_path = tmp_path / "key.pem"

    with patch("src.core.certificate.CERTIFICATE_DIR", tmp_path):
        init_ssl("ssl.pem", "key.pem")

        assert cert_path.exists()
        assert key_path.exists()
        assert b"BEGIN CERTIFICATE" in cert_path.read_bytes()
        assert b"BEGIN RSA PRIVATE KEY" in key_path.read_bytes()
        mock_stop.assert_not_called()


@patch("src.core.certificate.CERTIFICATE_DIR")
def test_init_ssl_skips_if_exists(mock_cert_dir, tmp_path):
    """Проверяем, что функция ничего не перезаписывает, если файлы уже есть."""
    cert_file = tmp_path / "ssl.pem"
    key_file = tmp_path / "key.pem"

    cert_file.write_text("existing cert")
    key_file.write_text("existing key")

    with patch("src.core.certificate.CERTIFICATE_DIR", tmp_path):
        init_ssl("ssl.pem", "key.pem")
        assert cert_file.read_text() == "existing cert"
        assert key_file.read_text() == "existing key"
