import string
import secrets


def gen_code():
    """
    Generates unique code of length 8
    :return:
    """
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))

    return password