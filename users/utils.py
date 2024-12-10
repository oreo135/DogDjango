import random
import string

def generate_random_password():
    """
    Генерация случайного пароля.
    """
    length = 12
    letters = string.ascii_letters
    digits = string.digits
    special = "!@#$%^&*"
    password = random.choices(letters, k=6) + random.choices(digits, k=3) + random.choices(special, k=3)
    random.shuffle(password)
    return ''.join(password)
