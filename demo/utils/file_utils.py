import json
import os
from datetime import date
from cryptography.hazmat.primitives import serialization

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_pem_key(path, private=False):
    with open(path, 'rb') as key_file:
        return serialization.load_pem_private_key(key_file.read(), None) if private else serialization.load_pem_public_key(key_file.read())

def save_pem_key_pair(keys_dir, priv_key, pub_key):
    with open(os.path.join(keys_dir, "private.pem"), "wb") as f:
        f.write(priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    with open(os.path.join(keys_dir, "public.pem"), "wb") as f:
        f.write(pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def data_odierna():
    return date.today().strftime("%Y-%m-%d")