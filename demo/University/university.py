import os
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

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
        self.SCA_contract_address = data.get("SCA_contract_address")

        self.w3 = blockchain_utils.init_blockchain_connection('http://cavuotohome.duckdns.org:8545')

        sid_abi_path = os.path.join(smart_contract_build_path, 'SIDSmartContract/SIDSmartContract.json')
        sid_abi = load_json(sid_abi_path)
        self.sid_contract_instance = self.w3.eth.contract(address=self.SID_contract_address, abi=sid_abi)

        cid_abi_path = os.path.join(smart_contract_build_path, 'CIDSmartContract/CIDSmartContract.json')
        cid_abi = load_json(cid_abi_path)
        self.cid_contract_instance = self.w3.eth.contract(address=self.CID_contract_address, abi=cid_abi)
        
        if self.SCA_contract_address is not None:
            sca_abi_path = os.path.join(self.smart_contract_build_path, 'SmartContractAuthority/SmartContractAuthority.json')
            sca_abi = load_json(sca_abi_path)
            self.sca_contract_instance = self.w3.eth.contract(address=self.CID_contract_address, abi=sca_abi)

    def update_uid(self, uid):
        self.UID = uid
        self.update_university_data()
        
    def update_sca_contract_address(self, address):
        self.SCA_contract_address = address
        self.update_university_data()
        
        sca_abi_path = os.path.join(self.smart_contract_build_path, 'SmartContractAuthority/SmartContractAuthority.json')
        sca_abi = load_json(sca_abi_path)
        self.sca_contract_instance = self.w3.eth.contract(address=self.SCA_contract_address, abi=sca_abi)

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

        w3 = blockchain_utils.init_blockchain_connection('http://cavuotohome.duckdns.org:8545')

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

    def update_university_data(self):
        data = {
            "UID": self.UID,
            "nome": self.nome,
            "ethereum_account_address": self.ethereum_account_address,
            "chiave_account": self.chiave_account,
            "SID_counter": self.SID_counter,
            "CID_counter": self.CID_counter,
            "SID_contract_address": self.SID_contract_address,
            "CID_contract_address": self.CID_contract_address,
            "SCA_contract_address": self.SCA_contract_address 
        }
        save_json(data, self._json_path)

    def register_student(self, student: Student):
        self.SID_counter += 1
        self.CID_counter += 1
        self.update_university_data()

        rsa_key = student.pub_key.public_numbers()
        modulus_int = rsa_key.n
        exponent_int = rsa_key.e

        modulus_bytes = modulus_int.to_bytes((modulus_int.bit_length() + 7) // 8, byteorder='big')
        exponent_bytes = exponent_int.to_bytes((exponent_int.bit_length() + 7) // 8, byteorder='big')

        tx = self.sid_contract_instance.functions.registraSid(
            self.SID_counter,
            modulus_bytes,
            exponent_bytes,
            True
        ).build_transaction({
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
            certificateId="CID:" + self.UID + ":" + str(self.CID_counter),
            studentId="SID:" + self.UID + ":" + str(self.SID_counter),
            universityId=self.UID,
            issuanceDate="2023-10-01",
            properties=[info]
        )

        signature = sign_data(self.chiave_privata, credential.toJSON())
        credential.add_sign(signature)
        
        tx = self.cid_contract_instance.functions.registraCid(
            self.CID_counter,
            True
        ).build_transaction({
            'from': self.ethereum_account_address,
            'nonce': self.w3.eth.get_transaction_count(self.ethereum_account_address),
            'gasPrice': self.w3.eth.gas_price,
            'gas': 800000
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.chiave_account)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Registrazione credenziale completata. Stato: {receipt.status}")

        return credential

    def register_erasmus_student(self, student: Student, json_credential: str, signature):
        student_credential = Credential.fromJSON(json_credential)
        
        if student_credential.properties:
            subject_info_props = [p for p in student_credential.properties if isinstance(p, SubjectInfo)]
            if len(subject_info_props) == 1:
                subject_info = subject_info_props[0]
                
                sid_parts = student_credential.SID.split(':')
                if len(sid_parts) == 3 and all(sid_parts):
                    pub_key_modulus, pub_key_exponent, isValid = self.sca_contract_instance.functions.verificaSid(
                        sid_parts[1],
                        int(sid_parts[2])
                    ).call()
                    
                    if isValid:
                        print("Il SID contenuto nella credenziale è valido.")
                        modulus_int = int.from_bytes(pub_key_modulus, byteorder='big')
                        exponent_int = int.from_bytes(pub_key_exponent, byteorder='big')

                        public_numbers = rsa.RSAPublicNumbers(exponent_int, modulus_int)
                        public_key = public_numbers.public_key()

                        try:
                            public_key.verify(
                                signature,
                                json_credential.encode("utf-8"),
                                padding.PKCS1v15(),
                                hashes.SHA256()
                            )
                        except Exception as e:
                            print(f"Errore nella verifica della firma: {e}")
                            
                        print("Firma dello studente verificata correttamente.")
                    else:
                        raise Exception("La credenziale presenta un SID non valido.")
                else:
                    raise ValueError("Formato del SID errato")
                
            else:
                raise ValueError("La credenziale deve contenere esattamente una proprietà di tipo SubjectInfo.")

            