import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

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

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel parsing del file JSON: {e}")

        required_fields = [
            "name", "surname", "birthDate", "gender", "nationality",
            "documentNumber", "documentIssuer", "email"
        ]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Campi mancanti nel JSON: {', '.join(missing)}")

        self.name = data["name"]
        self.surname = data["surname"]
        self.birthDate = data["birthDate"]
        self.gender = data["gender"]
        self.nationality = data["nationality"]
        self.documentNumber = data["documentNumber"]
        self.documentIssuer = data["documentIssuer"]
        self.email = data["email"]
        self.SID = data.get("SID", None)

        with open(pub_key_path, 'rb') as f:
            self.pub_key = serialization.load_pem_public_key(f.read())
        with open(priv_key_path, 'rb') as f:
            self.priv_key = serialization.load_pem_private_key(f.read(), password=None)

        os.makedirs(self.credentials_dir, exist_ok=True)

        self.credentials = []
        for filename in os.listdir(self.credentials_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.credentials_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        self.credentials.append(data)  # Se vuoi, qui puoi convertire in oggetti
                    except json.JSONDecodeError:
                        print(f"Warning: File JSON non valido ignorato: {filename}")

        print(f"Studente '{self.name} {self.surname}' caricato da {base_dir}")

    def set_sid(self, sid):
        self.SID = sid

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

    def generate_keypair(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return public_key, private_key

    def generate_keys(self):
        if self.pub_key is None and self.priv_key is None:
            self.pub_key, self.priv_key = self.generate_keypair()

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

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        folder_name = f"Student_{name}{surname}".replace(" ", "_")
        root_dir = os.path.join(base_path, folder_name)
        persistency_dir = os.path.join(root_dir, "persistency")
        keys_dir = os.path.join(persistency_dir, "keys")
        os.makedirs(keys_dir, exist_ok=False)

        private_path = os.path.join(keys_dir, "private.pem")
        public_path = os.path.join(keys_dir, "public.pem")

        with open(private_path, "wb") as priv_file:
            priv_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(public_path, "wb") as pub_file:
            pub_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

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
