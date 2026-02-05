import uvicorn
from sys import stdout
import os
from loguru import logger
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from api.api_app import app

def init_log(log_level_file="INFO", log_level_std="WARNING"):
    try:
        logger.remove()
        logger.add(
            "logs/app.log",
            format="{time} | {level} | {message} | {name}",
            rotation="256 MB",
            retention=f"10 days",
            level=log_level_file,
        )
        if bool(int(get_config(name="debug"))) == True:
            log_level_std = "TRACE"
        logger.add(stdout, level=log_level_std)
        logger.success(
            "Log init"
        )
    except Exception as err:
        logger.error(
            f"Log not init. Error: {err}"
        )
        exit()

def init_ssl(cert_file:str="ssl.pem",key_file:str="key.pem"):
    if os.path.exists(f"./instance/cert/{cert_file}")==True and os.path.exists(f"./instance/cert/{key_file}"):
        logger.info("Certificate found")
    else:
        try:
            keyFileGenerate=rsa.generate_private_key(public_exponent=65537, key_size=2048)
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
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
            if os.path.exists("./instance")==False:
                os.mkdir("./instance")
            if os.path.exists("./instance/cert")==False:
                os.mkdir("./instance/cert")
            with open(f"./instance/cert/{key_file}", "wb") as f:
                f.write(keyFileGenerate.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            logger.success("File certificate key create")
            with open(f"./instance/cert/{cert_file}", "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            logger.success("File certificate create")
        except Exception as err:
            logger.critical(f"Certificate not create. Error: {err}")
            exit()

if os.path.exists("./instance/config.json") == True:
    from db_modules.db_query_config import get_config

    port = int(get_config(name="app_port"))
    cert_file=get_config(name="cert")
    key_file=get_config(name="cert_key")
    init_ssl(cert_file=cert_file,key_file=key_file)
    init_log()
else:
    port = 7000
    init_ssl()
    cert_file="ssl.pem"
    key_file="key.pem"

if __name__ == "__main__":
    try:
        logger.success(
            f"Сервер запущен на порту {port}"
        )
        uvicorn.run(app=app, host="0.0.0.0", port=port,ssl_certfile=f"./instance/cert/{cert_file}", ssl_keyfile=f"./instance/cert/{key_file}")
    except Exception as err:
        logger.error(f"Ошибка запуски сервера: {err}")
    finally:
        logger.info("Сервер остановлен")
