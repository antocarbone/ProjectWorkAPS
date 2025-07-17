import os

from Credential.fields import *
from utils import blockchain_utils
from University.university import University
from SmartContractAuthority.utils.contract_utils import load_contract_interface, deploy_contract
from SmartContractAuthority.utils.file_utils import load_json, save_json

class SmartContractAuthority:
    def __init__(self, sca_root_path: str, smart_contract_build_path: str):
        if not os.path.isdir(smart_contract_build_path):
            raise FileNotFoundError(f"Cartella {smart_contract_build_path} non trovata")

        self.smart_contract_build_path = smart_contract_build_path

        persistency_path = os.path.join(sca_root_path, "persistency")
        if not os.path.isdir(persistency_path):
            raise FileNotFoundError(f"Cartella 'persistency' non trovata in: {sca_root_path}")

        json_path = os.path.join(persistency_path, "sca_data.json")
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"File JSON non trovato: {json_path}")

        data = load_json(json_path)
        required = ["ethereum_account_address", "chiave_account"]
        if any(field not in data for field in required):
            raise ValueError(f"Campi mancanti nel JSON: {required}")

        self._json_path = json_path
        self.ethereum_account_address = data["ethereum_account_address"]
        self.chiave_account = data["chiave_account"]
        self.UID_contract_address = data.get("UID_contract_address")
        self.registered_universities = data["registered_universities"]

        self.w3 = blockchain_utils.init_blockchain_connection('http://cavuotohome.duckdns.org:8545')

        abi_path = os.path.join(smart_contract_build_path, 'SmartContractAuthority/SmartContractAuthority.json')
        abi = load_json(abi_path)
        self.uid_contract_instance = self.w3.eth.contract(address=self.UID_contract_address, abi=abi)

    @staticmethod
    def create_sca(base_path: str, smart_contract_build_path: str):
        ethereum_account_address = input("Indirizzo Ethereum: ").strip()
        chiave_account = input("Chiave dell'account: ").strip()

        root_dir = os.path.join(base_path, 'SCA')
        persistency_dir = os.path.join(root_dir, "persistency")
        os.makedirs(persistency_dir, exist_ok=False)

        w3 = blockchain_utils.init_blockchain_connection('http://cavuotohome.duckdns.org:8545')

        abi, bytecode = load_contract_interface(smart_contract_build_path, "SmartContractAuthority")

        UID_contract_address = deploy_contract(w3, chiave_account, ethereum_account_address, abi, bytecode)

        data = {
            "ethereum_account_address": ethereum_account_address,
            "chiave_account": chiave_account,
            "UID_contract_address": UID_contract_address,
            "registered_universities": []
        }

        save_json(data, os.path.join(persistency_dir, "sca_data.json"))
        print("Università creata con successo.")

    def save_json(self):
        data = {
            "ethereum_account_address": self.ethereum_account_address,
            "chiave_account": self.chiave_account,
            "UID_contract_address": self.UID_contract_address,
            "registered_universities": self.registered_universities
        }
        save_json(data, self._json_path)

    def register_university(self, uni: University):
        while True:
            UID = input("Inserisci l'UID (max 20 caratteri, senza spazi): ").strip()
            if " " in UID:
                print("L'UID non può contenere spazi.")
            elif len(UID) > 20:
                print("L'UID non può superare i 20 caratteri.")
            elif len(UID) == 0:
                print("L'UID non può essere vuoto.")
            elif UID in self.registered_universities:
                print("L'UID inserito risulta già utilizzato.")
            else:
                break

        self.registered_universities.append(UID)
        self.save_json()

        pub_numbers = uni.chiave_pubblica.public_numbers()
        modulus = pub_numbers.n
        exponent = pub_numbers.e

        pub_key_modulus_bytes = modulus.to_bytes((modulus.bit_length() + 7) // 8, byteorder='big')
        pub_key_exponent_bytes = exponent.to_bytes((exponent.bit_length() + 7) // 8, byteorder='big')

        tx = self.uid_contract_instance.functions.registraUniversita(
            UID,
            pub_key_modulus_bytes,
            pub_key_exponent_bytes,
            False,
            uni.SID_contract_address,
            uni.CID_contract_address
        ).build_transaction({
            'from': self.ethereum_account_address,
            'nonce': self.w3.eth.get_transaction_count(self.ethereum_account_address),
            'gasPrice': self.w3.eth.gas_price,
            'gas': 800000
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.chiave_account)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Registrazione università completata.")
        
        return UID, self.UID_contract_address

    def revoke_uid(self, uid):
        tx = self.uid_contract_instance.functions.setRevokeStatusUniversita(
            uid,
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

        print(f"Registrazione università completata.")