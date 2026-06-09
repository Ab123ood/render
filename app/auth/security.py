import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import current_app


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password against an Argon2id hash."""
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def check_password_strength(password: str) -> tuple[bool, str]:
    """Check if password meets minimum strength requirements."""
    if len(password) < 12:
        return False, "كلمة المرور يجب أن تكون 12 حرفًا على الأقل"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    score = sum([has_upper, has_lower, has_digit, has_special])
    
    if score < 3:
        return False, "كلمة المرور يجب أن تحتوي على أحرف كبيرة وصغيرة وأرقام ورموز خاصة"
    
    return True, "كلمة مرور قوية"