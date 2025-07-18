import os
import json
import base64
from Credential.credential import Credential
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from utils.file_utils import *
from utils.crypto_utils import *


class Student:
    def __init__(self, base_dir: str):
        persistency_dir = os.path.join(base_dir, "persistency")
        json_path = os.path.join(persistency_dir, "student_data.json")
        keys_dir = os.path.join(persistency_dir, "keys")
        pub_key_path = os.path.join(keys_dir, "public.pem")
        priv_key_path = os.path.join(keys_dir, "private.pem")
        self.credentials_dir = os.path.join(persistency_dir, "credentials")

        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"File JSON non trovato: {json_path}")
        if not os.path.isfile(pub_key_path) or not os.path.isfile(priv_key_path):
            raise FileNotFoundError(f"File delle chiavi non trovato in: {keys_dir}")

        data = load_json(json_path)
        required = [
            "name", "surname", "birthDate", "gender", "nationality",
            "documentNumber", "documentIssuer", "email"
        ]

        if any(field not in data for field in required):
            raise ValueError(f"Campi mancanti nel JSON: {required}")
        
        self._json_path = json_path
        self.name = data["name"]
        self.surname = data["surname"]
        self.birthDate = data["birthDate"]
        self.gender = data["gender"]
        self.nationality = data["nationality"]
        self.documentNumber = data["documentNumber"]
        self.documentIssuer = data["documentIssuer"]
        self.email = data["email"]
        self.SID = data.get("SID", None)

        self.pub_key = load_pem_key(pub_key_path)
        self.priv_key = load_pem_key(priv_key_path,True)
        
        os.makedirs(self.credentials_dir, exist_ok=True)

        self.credentials = []
        for filename in os.listdir(self.credentials_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.credentials_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = Credential.fromJSON(f.read())
                        self.credentials.append(data)
                    except json.JSONDecodeError:
                        print(f"Warning: File JSON non valido ignorato: {filename}")

        print(f"Studente '{self.name} {self.surname}' caricato da {base_dir}")

    def set_sid(self, sid):
        self.SID = sid
        self.update_student_data()

    def challenge(self, nonce):
        sign = self.priv_key.sign(
            nonce,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(sign).decode('utf-8')

    def save_credential(self, credential):
        if not hasattr(self, "credentials_dir"):
            raise RuntimeError("Cartella delle credenziali non inizializzata")

        self.credentials.append(credential)

        existing_files = [f for f in os.listdir(self.credentials_dir) if f.startswith("credential_") and f.endswith(".json")]
        indices = []
        for f in existing_files:
            try:
                num = int(f.split("_")[1].split(".")[0])
                indices.append(num)
            except (IndexError, ValueError):
                continue
        next_index = max(indices, default=-1) + 1

        filename = f"credential_{next_index}.json"
        filepath = os.path.join(self.credentials_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(credential.toJSON())

        print(f"Credenziale salvata in: {filepath}")

    def update_student_data(self):
        data = {
            "name": self.name,
            "surname": self.surname,
            "birthDate": self.birthDate,
            "gender": self.gender,
            "nationality": self.nationality,
            "documentNumber": self.documentNumber,
            "documentIssuer": self.documentIssuer,
            "email": self.email,
            "SID": self.SID
        }
        save_json(data, self._json_path)

    @staticmethod
    def create_student(base_path: str):
        name = input("Nome: ").strip()
        surname = input("Cognome: ").strip()
        birthDate = input("Data di nascita (YYYY-MM-DD): ").strip()
        gender = input("Genere: ").strip()
        nationality = input("Nazionalità: ").strip()
        documentNumber = input("Numero documento: ").strip()
        documentIssuer = input("Ente rilascio documento: ").strip()
        email = input("Email: ").strip()

        
        private_key,public_key = gen_key_pair()

        folder_name = f"Student_{name}{surname}".replace(" ", "_")
        root_dir = os.path.join(base_path, folder_name)
        persistency_dir = os.path.join(root_dir, "persistency")
        keys_dir = os.path.join(persistency_dir, "keys")
        os.makedirs(keys_dir, exist_ok=False)
        save_pem_key_pair(keys_dir,private_key,public_key)

        json_path = os.path.join(persistency_dir, "student_data.json")
        data = {
            "name": name,
            "surname": surname,
            "birthDate": birthDate,
            "gender": gender,
            "nationality": nationality,
            "documentNumber": documentNumber,
            "documentIssuer": documentIssuer,
            "email": email,
            "SID": None
        }
        os.makedirs(os.path.join(persistency_dir, "credentials"), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"\nStudente creato e salvato in: {json_path}")
