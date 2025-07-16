import json
import os
import time
import random
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Credential.credential import Credential
from Credential.fields import *
from Student.student import Student

class University:
    def __init__(self, university_root_path: str):
        persistency_path = os.path.join(university_root_path, "persistency")
        if not os.path.isdir(persistency_path):
            raise FileNotFoundError(f"Cartella 'persistency' non trovata in: {university_root_path}")

        json_path = os.path.join(persistency_path, "university_data.json")
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"File JSON non trovato: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel parsing del file JSON: {e}")

        required_fields = [
            "nome", "ethereum_account_address", "chiave_account",
            "SID_counter", "CID_counter"
        ]

        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Campi mancanti nel JSON: {', '.join(missing)}")

        keys_dir = os.path.join(persistency_path, "keys")
        public_path = os.path.join(keys_dir, "public.pem")
        private_path = os.path.join(keys_dir, "private.pem")

        if not os.path.isfile(public_path) or not os.path.isfile(private_path):
            raise FileNotFoundError("File delle chiavi RSA non trovati nella cartella 'keys'.")

        with open(public_path, "rb") as pub_file:
            self.chiave_pubblica = serialization.load_pem_public_key(pub_file.read())

        with open(private_path, "rb") as priv_file:
            self.chiave_privata = serialization.load_pem_private_key(priv_file.read(), password=None)

        self._json_path = json_path

        self.UID = data.get("UID")
        self.nome = data["nome"]
        self.ethereum_account_address = data["ethereum_account_address"]
        self.chiave_account = data["chiave_account"]
        self.SID_counter = data["SID_counter"]
        self.CID_counter = data["CID_counter"]
        self.SID_contract_address = data.get("SID_contract_address")
        self.CID_contract_address = data.get("CID_contract_address")

    @staticmethod
    def __register_SID_contract():
        print("registrato contratto SID")
        return "siumaSID"

    @staticmethod
    def __register_CID_contract():
        print("registrato contratto CID")
        return "siumaCID"

    @staticmethod
    def create_university(base_path: str):
        nome = input("Nome università: ").strip()
        ethereum_account_address = input("Indirizzo Ethereum: ").strip()
        chiave_account = input("Chiave dell'account: ").strip()

        chiave_privata = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        chiave_pubblica = chiave_privata.public_key()

        root_dir = os.path.join(base_path, 'University_'+nome)
        persistency_dir = os.path.join(root_dir, "persistency")
        keys_dir = os.path.join(persistency_dir, "keys")
        os.makedirs(keys_dir, exist_ok=False)

        private_path = os.path.join(keys_dir, "private.pem")
        public_path = os.path.join(keys_dir, "public.pem")

        with open(private_path, "wb") as priv_file:
            priv_file.write(chiave_privata.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(public_path, "wb") as pub_file:
            pub_file.write(chiave_pubblica.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        SID_contract_address = University.__register_SID_contract()
        CID_contract_address = University.__register_CID_contract()

        data = {
            "nome": nome,
            "ethereum_account_address": ethereum_account_address,
            "chiave_account": chiave_account,
            "SID_counter": 0,
            "CID_counter": 0,
            "SID_contract_address": SID_contract_address,
            "CID_contract_address": CID_contract_address
        }

        json_path = os.path.join(persistency_dir, "university_data.json")

        if os.path.exists(json_path):
            raise FileExistsError(f"Il file {json_path} esiste già. Scegli un altro nome o percorso.")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Università creata e salvata in: {json_path}")

    def update_UID(self, UID):
        self.UID = UID
        self.save_json()

    def update_nome(self, nome):
        self.nome = nome
        self.save_json()

    def update_chiave_pubblica(self, chiave_pubblica):
        self.chiave_pubblica = chiave_pubblica
        self.save_json()

    def update_chiave_privata(self, chiave_privata):
        self.chiave_privata = chiave_privata
        self.save_json()

    def update_ethereum_account_address(self, ethereum_account_address):
        self.ethereum_account_address = ethereum_account_address
        self.save_json()

    def update_chiave_account(self, chiave_account):
        self.chiave_account = chiave_account
        self.save_json()

    def update_SID_counter(self, SID_counter):
        self.SID_counter = SID_counter
        self.save_json()

    def update_CID_counter(self, CID_counter):
        self.CID_counter = CID_counter
        self.save_json()

    def update_SID_contract_address(self, SID_contract_address):
        self.SID_contract_address = SID_contract_address
        self.save_json()

    def update_CID_contract_address(self, CID_contract_address):
        self.CID_contract_address = CID_contract_address
        self.save_json()

    def save_json(self):
        data = {
            "UID": self.UID,
            "nome": self.nome,
            "ethereum_account_address": self.ethereum_account_address,
            "chiave_account": self.chiave_account,
            "SID_counter": self.SID_counter,
            "CID_counter": self.CID_counter,
            "SID_contract_address": self.SID_contract_address,
            "CID_contract_address": self.CID_contract_address
        }

        with open(self._json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def register_student(self, student: Student):
        student_infos = SubjectInfo(
            student.name, 
            student.surname, 
            student.birthDate, 
            student.gender, 
            student.nationality, 
            student.documentNumber, 
            student.documentIssuer, 
            student.email
        )
        
        credential = Credential(
            certificateId="exampleCID",
            studentId="exampleSID",
            universityId=self.UID,
            issuanceDate="2023-10-01",
            properties=[student_infos]
        )
        
        sign = self.chiave_privata.sign(
            credential.toJSON().encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        signature_b64 = base64.b64encode(sign).decode('utf-8')
        
        credential.add_sign(signature_b64)
        
        return credential
    
    def register_erasmus_student(self, student_credential: Credential, student: Student):
        print("Verifica CID: NON IMPLEMENTATA")

        print("Ottenimento chiave pubblica università origine: NON IMPLEMENTATA")

        print("Verifica firma della credenziale: NON IMPLEMENTATA")

        print("Ottenimento chiave pubblica studente: NON IMPLEMENTATA")

        challenge_string = f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        print(f"Inviata challenge: {challenge_string}")
        student_response = student.challenge(challenge_string)

        try:
            response_signature = base64.b64decode(student_response)

            student.pub_key.verify(
                response_signature,
                challenge_string.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("Firma challenge verificata correttamente.")
        except Exception as e:
            print(f"Verifica della firma della challenge fallita: {e}")
            return

        persistency_path = os.path.join(os.path.dirname(self._json_path), "erasmus_students")
        os.makedirs(persistency_path, exist_ok=True)

        student_id = student_credential.studentId
        file_path = os.path.join(persistency_path, f"{student_id}.json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(student_credential.toDict(), f, ensure_ascii=False, indent=4)

        print(f"Credenziale Erasmus salvata per lo studente: {student_id}")
    
    def release_career_credential(self, student: Student, identity_credential: Credential):
        student.challenge(f"{int(time.time() * 1000)}{random.randint(1000, 9999)}")
        print("Assumo che la challenge sia superata")
        
        properties = [
            Course(name="Analisi Matematica I", achieved=True, grade=28, cfu=9, achievementData="2023-01-20"),
            Course(name="Fondamenti di Informatica", achieved=True, grade=30, cfu=12, achievementData="2023-02-15"),
            Course(name="Fisica I", achieved=True, grade=25, cfu=6, achievementData="2023-03-01"),
            ExtraActivity(name="Hackathon di Ateneo", cfu=2),
            ExtraActivity(name="Corso Python base", cfu=1)
        ]
        
        credential = Credential(
            certificateId="exampleCID",
            studentId="exampleSID",
            universityId=self.UID,
            issuanceDate="2023-10-01",
            properties=properties
        )
        
        sign = self.chiave_privata.sign(
            credential.toJSON().encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        signature_b64 = base64.b64encode(sign).decode('utf-8')
        
        credential.add_sign(signature_b64)
        
        return credential
    
    def revoke_sid():
        pass
    
    def revoke_credential():
        pass
    