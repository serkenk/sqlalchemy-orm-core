# security.py
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

# BcryptHasher ile parola hash'leme mekanizmasını başlatıyoruz
password_hash = PasswordHash((BcryptHasher(),))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Düz metin parolanın veritabanındaki hash ile eşleşip eşleşmediğini doğrular."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Düz metin parolayı bcrypt kullanarak güvenli bir şekilde hash'ler."""
    return password_hash.hash(password)
