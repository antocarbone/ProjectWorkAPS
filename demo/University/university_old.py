import json
import os
import time
import random
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Credential.credential import Credential
from Credential.fields import *
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.middleware import ExtraDataToPOAMiddleware
from Student.student import Student

class University:
    def __init__(self, university_root_path: str, smart_contract_build_path: str):
        if not os.path.isdir(smart_contract_build_path):
            raise FileNotFoundError(f"Cartella {smart_contract_build_path} non trovata")
        self.smart_contract_build_path = smart_contract_build_path
        
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
        
        try:
            self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if not self.w3.is_connected():
                raise ConnectionError("Impossibile connettersi al nodo Ethereum")
            
            abi_path = os.path.join(smart_contract_build_path, 'SIDSmartContract/SIDSmartContract.json')

            if not os.path.isfile(abi_path):
                raise FileNotFoundError(f"File ABI mancante per il contratto SIDSmartContract")

            with open(abi_path, 'r') as f:
                abi = json.load(f)
                
            self.sid_contract_instance = self.w3.eth.contract(address=self.SID_contract_address, abi=abi)
        except Exception as e:
            print(f"Errore durante l'utilizzo del contratto: {e}")
            return
    
    @staticmethod
    def _deploy_contract(w3, private_key, account_address, contract_name, build_dir):
        contract_path = os.path.join(build_dir, contract_name)
        abi_path = os.path.join(contract_path, f"{contract_name}.json")
        bin_path = os.path.join(contract_path, f"{contract_name}.bin")

        if not os.path.isfile(abi_path) or not os.path.isfile(bin_path):
            raise FileNotFoundError(f"File ABI o BIN mancante per il contratto {contract_name}")

        with open(abi_path, 'r') as f:
            abi = json.load(f)
        with open(bin_path, 'r') as f:
            bytecode = f.read()

        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        transaction = contract.constructor().build_transaction({
            'from': account_address,
            'nonce': w3.eth.get_transaction_count(account_address),
            'gasPrice': w3.eth.gas_price,
            'gas': 1500000
        })

        print("\nTransazione di deploy costruita.")
        print(f"Nonce: {transaction['nonce']}")
        print(f"Gas Price: {w3.from_wei(transaction['gasPrice'], 'gwei')} Gwei")
        print(f"Gas Limit: {transaction['gas']}")

        print("Firmando la transazione...")
        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        print("Transazione di deploy firmata.")

        print("Invio della transazione...")
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
        print(f"Transazione di deploy inviata! Hash: {tx_hash.hex()}")

        print("In attesa che la transazione venga minata...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print("\n--- Ricevuta del Deploy ---")
        print(f"Stato della transazione (1 = successo, 0 = fallimento): {tx_receipt.status}")
        print(f"Block Number: {tx_receipt.blockNumber}")
        print(f"Gas Usato: {tx_receipt.gasUsed}")
        
        if tx_receipt.status == 1:
            deployed_contract_address = tx_receipt.contractAddress
            print(f"Contratto Greeter deployato con successo!")
            print(f"Indirizzo del contratto deployato: {deployed_contract_address}")
            return deployed_contract_address
        else: 
            raise Exception("Errore nel deploy")

    @staticmethod
    def create_university(base_path: str, smart_contract_build_path: str):
        if not os.path.isdir(smart_contract_build_path):
            raise FileNotFoundError(f"Cartella {smart_contract_build_path} non trovata")
        
        try:
            w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if not w3.is_connected():
                raise ConnectionError("Impossibile connettersi al nodo Ethereum")
        except Exception as e:
            print(f"Errore durante il deploy dei contratti: {e}")
            return
        
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

            SID_contract_address = University._deploy_contract(w3, chiave_account, ethereum_account_address, "SIDSmartContract", smart_contract_build_path)
            CID_contract_address = University._deploy_contract(w3, chiave_account, ethereum_account_address, "CIDSmartContract", smart_contract_build_path)

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
        
        register_student = self.sid_contract_instance.functions.registraSid('SID:UNISA:0002'.encode('utf-8')[:32].ljust(32, b'\0'), student.pub_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8'), True).build_transaction({
            'from': self.ethereum_account_address,
            'nonce': self.w3.eth.get_transaction_count(self.ethereum_account_address),
            'gasPrice': self.w3.eth.gas_price,
            'gas': 800000
        })

        signed_register_student = self.w3.eth.account.sign_transaction(register_student, private_key=self.chiave_account)
        register_student_hash = self.w3.eth.send_raw_transaction(signed_register_student.raw_transaction)

        register_student_receipt = self.w3.eth.wait_for_transaction_receipt(register_student_hash)
        print(f"Immatricolazione Studente Transazione completata. Stato: {register_student_receipt.status}")
        
        credential = Credential(
            certificateId="exampleCID",
            studentId="SID:UNISA:0001",
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
    