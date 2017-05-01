import os
import base64


def get_random_id():
    return base64.b32encode(os.urandom(25)).decode().lower()