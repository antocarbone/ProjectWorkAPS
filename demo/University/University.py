import os
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from Credential.credential import Credential
from Credential.fields import *
from Student.student import Student
from utils import blockchain_utils
from University.utils.contract_utils import load_contract_interface, deploy_contract
from University.utils.file_utils import load_json, save_json, load_pem_key, save_pem_key_pair
from University.utils.crypto_utils import sign_data, gen_key_pair

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

        data = load_json(json_path)
        required = ["nome", "ethereum_account_address", "chiave_account", "SID_counter", "CID_counter"]
        if any(field not in data for field in required):
            raise ValueError(f"Campi mancanti nel JSON: {required}")

        keys_dir = os.path.join(persistency_path, "keys")
        self.chiave_pubblica = load_pem_key(os.path.join(keys_dir, "public.pem"))
        self.chiave_privata = load_pem_key(os.path.join(keys_dir, "private.pem"), private=True)

        self._json_path = json_path
        self.UID = data.get("UID")
        self.nome = data["nome"]
        self.ethereum_account_address = data["ethereum_account_address"]
        self.chiave_account = data["chiave_account"]
        self.SID_counter = data["SID_counter"]
        self.CID_counter = data["CID_counter"]
        self.SID_contract_address = data.get("SID_contract_address")
        self.CID_contract_address = data.get("CID_contract_address")

        self.w3 = blockchain_utils.init_blockchain_connection('http://127.0.0.1:7545')

        abi_path = os.path.join(smart_contract_build_path, 'SIDSmartContract/SIDSmartContract.json')
        abi = load_json(abi_path)
        self.sid_contract_instance = self.w3.eth.contract(address=self.SID_contract_address, abi=abi)

    @staticmethod
    def create_university(base_path: str, smart_contract_build_path: str):
        nome = input("Nome università: ").strip()
        ethereum_account_address = input("Indirizzo Ethereum: ").strip()
        chiave_account = input("Chiave dell'account: ").strip()

        chiave_privata, chiave_pubblica = gen_key_pair()

        root_dir = os.path.join(base_path, 'University_' + nome)
        persistency_dir = os.path.join(root_dir, "persistency")
        keys_dir = os.path.join(persistency_dir, "keys")
        os.makedirs(keys_dir, exist_ok=False)

        save_pem_key_pair(keys_dir, chiave_privata, chiave_pubblica)

        w3 = blockchain_utils.init_blockchain_connection('http://127.0.0.1:7545')

        abi_sid, bytecode_sid = load_contract_interface(smart_contract_build_path, "SIDSmartContract")
        abi_cid, bytecode_cid = load_contract_interface(smart_contract_build_path, "CIDSmartContract")

        SID_contract_address = deploy_contract(w3, chiave_account, ethereum_account_address, abi_sid, bytecode_sid)
        CID_contract_address = deploy_contract(w3, chiave_account, ethereum_account_address, abi_cid, bytecode_cid)

        data = {
            "nome": nome,
            "ethereum_account_address": ethereum_account_address,
            "chiave_account": chiave_account,
            "SID_counter": 0,
            "CID_counter": 0,
            "SID_contract_address": SID_contract_address,
            "CID_contract_address": CID_contract_address
        }

        save_json(data, os.path.join(persistency_dir, "university_data.json"))
        print("Università creata con successo.")

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
        save_json(data, self._json_path)

    def register_student(self, student: Student):
        sid = '0003'.encode('utf-8')[:32].ljust(32, b'\0')
        pubkey_str = student.pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        tx = self.sid_contract_instance.functions.registraSid(sid, pubkey_str, True).build_transaction({
            'from': self.ethereum_account_address,
            'nonce': self.w3.eth.get_transaction_count(self.ethereum_account_address),
            'gasPrice': self.w3.eth.gas_price,
            'gas': 800000
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.chiave_account)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Registrazione studente completata. Stato: {receipt.status}")

        info = SubjectInfo(
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
            studentId="SID:UNISA:0001",
            universityId=self.UID,
            issuanceDate="2023-10-01",
            properties=[info]
        )

        signature = sign_data(self.chiave_privata, credential.toJSON())
        credential.add_sign(signature)

        return credential