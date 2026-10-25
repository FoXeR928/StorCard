import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

AES_BLOCK_SIZE = 16


def decrypt_storcard_file(password: str, file_bytes: bytes) -> str:
    """
    Расшифровывает файл .storcard.
    Формат: [16 байт IV] + [AES-CBC(PKCS7)].
    Ключ = SHA-256(password).
    """
    if len(file_bytes) < AES_BLOCK_SIZE * 2:
        raise ValueError("Файл повреждён или слишком мал.")

    payload = file_bytes[AES_BLOCK_SIZE:]
    if len(payload) % AES_BLOCK_SIZE != 0:
        raise ValueError("Размер шифротекста не кратен 16 — файл повреждён.")

    key = hashlib.sha256(password.encode("utf-8")).digest()
    iv = file_bytes[:AES_BLOCK_SIZE]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(payload) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded) + unpadder.finalize()

    return data.decode("utf-8")