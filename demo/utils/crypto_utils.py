import base64
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import utils
import os

def sign_hashed_data(private_key, hashed_data_as_hex: str) -> str:
    
    signature = private_key.sign(
        bytes.fromhex(hashed_data_as_hex),
        padding.PSS(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        utils.Prehashed(hashes.SHA256())
    )
    return base64.b64encode(signature).decode('utf-8')

def gen_key_pair():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return priv, priv.public_key()

def recover_public_key_from_modulus_exponent(modulus:bytes,exponent:bytes):
    modulus_int = int.from_bytes(modulus, byteorder='big')
    exponent_int = int.from_bytes(exponent, byteorder='big')
    public_numbers = rsa.RSAPublicNumbers(exponent_int, modulus_int)
    return public_numbers.public_key()


def generate_random_nonce(length_bytes: int = 32) -> bytes:
    if length_bytes <= 0:
        raise ValueError("Lunghezza nonce non valida.")
    return os.urandom(length_bytes)