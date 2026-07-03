import datetime
from datetime import datetime, timedelta, timezone
from typing import Tuple
from loguru import logger
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import src.core.system as system


def generate_self_signed_cert(
    days: int = 365, common_name: str = "localhost"
) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]), critical=False
        )
        .sign(private_key, hashes.SHA256())
    )
    return private_key, cert


def init_ssl(cert_file: str = "ssl.pem", key_file: str = "key.pem"):
    certs_dir="./date/certificates"
    cert_path = certs_dir / cert_file
    key_path = certs_dir / key_file
    if cert_path.exists() and key_path.exists():
        logger.info("SSL сертификат найден")
        return
    try:
        certs_dir.mkdir(parents=True, exist_ok=True)
        private_key, cert = generate_self_signed_cert(days=365)
        key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    except Exception as err:
        logger.critical(f"Ошибка генерации SSL: {err}")
        system.stop_server(1)
