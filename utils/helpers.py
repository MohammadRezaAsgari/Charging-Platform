import random
import string
import secrets

def create_random_str(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_random_digits(length: int = 10) -> str:
    return "".join(secrets.choice(string.digits) for i in range(length))
