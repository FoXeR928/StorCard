import pytest
from unittest.mock import patch, MagicMock
from cryptography import x509
import src.core.certificate as certificate


@pytest.fixture
def mock_cert_dir(tmp_path):
    with patch("src.core.certificate.CERTIFICATE_DIR", tmp_path):
        yield tmp_path


def test_generate_self_signed_cert():
    days = 10
    cn = "test.local"
    key, cert = certificate.generate_self_signed_cert(days=days, common_name=cn)
    assert key.key_size == 2048
    assert isinstance(cert, x509.Certificate)
    subject = cert.subject.get_attributes_for_oid(certificate.NameOID.COMMON_NAME)[0]
    assert subject.value == cn
    duration = cert.not_valid_after_utc - cert.not_valid_before_utc
    assert duration.days == days


def test_init_ssl_creates_files(mock_cert_dir):
    cert_file = "test_cert.pem"
    key_file = "test_key.pem"
    certificate.init_ssl(cert_file=cert_file, key_file=key_file)
    assert (mock_cert_dir / cert_file).exists()
    assert (mock_cert_dir / key_file).exists()
    cert_data = (mock_cert_dir / cert_file).read_bytes()
    cert = x509.load_pem_x509_certificate(cert_data)
    assert (
        cert.issuer.get_attributes_for_oid(certificate.NameOID.COMMON_NAME)[0].value
        == "localhost"
    )


def test_init_ssl_skips_if_exists(mock_cert_dir, caplog_loguru):
    cert_path = mock_cert_dir / "ssl.pem"
    key_path = mock_cert_dir / "key.pem"
    cert_path.write_text("existing_cert")
    key_path.write_text("existing_key")
    certificate.init_ssl()
    assert "SSL сертификат найден" in caplog_loguru.text
    assert cert_path.read_text() == "existing_cert"


@patch("src.core.system.stop_server")
def test_init_ssl_error_handling(mock_stop, mock_cert_dir):
    data_dir = mock_cert_dir / "data"
    logs_dir = mock_cert_dir / "logs"
    try:
        mock_cert_dir.chmod(0o444)
        certificate.init_ssl("fail.pem", "fail.key")
        mock_stop.assert_called_once_with(1)
    finally:
        mock_cert_dir.chmod(0o755)
        if data_dir.exists():
            data_dir.chmod(0o755)
        if logs_dir.exists():
            logs_dir.chmod(0o755)
