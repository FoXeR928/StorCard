import os
import datetime
import sys
from loguru import logger
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from data.config_modules.config_init import config_folder_path
from data.config_modules.config_check import check_folder_path

CERTIFICATE_DIR = f"{config_folder_path}/cert"


def init_ssl(cert_file: str = "ssl.pem", key_file: str = "key.pem"):
    if os.path.exists(f"{cert_folder_path}/{cert_file}") == True and os.path.exists(
        f"{cert_folder_path}/{key_file}"
    ):
        logger.info("Certificate found")
    else:
        try:
            keyFileGenerate = rsa.generate_private_key(
                public_exponent=65537, key_size=2048
            )
            subject = x509.Name(
                [
                    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
                ]
            )
            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(subject)
                .public_key(keyFileGenerate.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.datetime.now())
                .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
                .add_extension(
                    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                    critical=False,
                )
                .sign(keyFileGenerate, hashes.SHA256())
            )
            if check_folder_path(config_folder_path):
                if check_folder_path(cert_folder_path):
                    with open(f"{cert_folder_path}/{key_file}", "wb") as f:
                        f.write(
                            keyFileGenerate.private_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PrivateFormat.TraditionalOpenSSL,
                                encryption_algorithm=serialization.NoEncryption(),
                            )
                        )
                    logger.success("File certificate key create")
                    with open(f"{cert_folder_path}/{cert_file}", "wb") as f:
                        f.write(cert.public_bytes(serialization.Encoding.PEM))
                    logger.success("File certificate create")
        except Exception as err:
            logger.critical(f"Certificate not create. Error: {err}")
            sys.exit(1)
