import random
import string


def generate_part_number():
    part_number = ''.join(random.choices(string.ascii_uppercase, k=2))
    part_number += str(random.randint(100_000_000, 999_999_999))
    return part_number
