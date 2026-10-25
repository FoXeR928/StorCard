"""Юнит-тесты core/crypto_utils.py — не трогают БД и HTTP."""

import json

import pytest

from core.crypto_utils import decrypt_storcard_file
from migration_helpers import encrypt_storcard


def test_crypto_roundtrip():
    payload = {"version": 1, "users": [], "cards": [], "extra": "юникод-тест"}
    blob = encrypt_storcard("secret", payload)
    assert json.loads(decrypt_storcard_file("secret", blob)) == payload


def test_crypto_wrong_password_raises():
    blob = encrypt_storcard("correct", {"version": 1})
    with pytest.raises(Exception):
        decrypt_storcard_file("wrong", blob)


def test_crypto_short_file_raises():
    with pytest.raises(Exception):
        decrypt_storcard_file("pw", b"\x00" * 10)


def test_crypto_unaligned_file_raises():
    with pytest.raises(Exception):
        decrypt_storcard_file("pw", b"\x00" * 36)


def test_crypto_iv_randomization():
    """Один plaintext + один пароль → два разных шифротекста (из-за IV)."""
    payload = {"version": 1}
    a = encrypt_storcard("pw", payload)
    b = encrypt_storcard("pw", payload)
    assert a != b