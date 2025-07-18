import os

from Credential.fields import *
from University.university import University
from SmartContractAuthority.utils.contract_utils import load_contract_interface
from SmartContractAuthority.utils.file_utils import load_json, save_json
from SmartContractAuthority.services.sca_blockchain_manager import SCABlockchainManager

class SmartContractAuthority:
    DEFAULT_RPC_URL = 'http://cavuotohome.duckdns.org:8545'

    def __init__(self, sca_root_path: str, smart_contract_build_path: str):
        if not os.path.isdir(smart_contract_build_path):
            print(f"Errore: Cartella smart contract build '{smart_contract_build_path}' non trovata.")
            raise FileNotFoundError(f"Cartella {smart_contract_build_path} non trovata")

        self.smart_contract_build_path = smart_contract_build_path

        persistency_path = os.path.join(sca_root_path, "persistency")
        if not os.path.isdir(persistency_path):
            print(f"Errore: Cartella 'persistency' non trovata in: {sca_root_path}")
            raise FileNotFoundError(f"Cartella 'persistency' non trovata in: {sca_root_path}")

        json_path = os.path.join(persistency_path, "sca_data.json")
        if not os.path.isfile(json_path):
            print(f"Errore: File JSON '{json_path}' non trovato. SCA non configurata.")
            raise FileNotFoundError(f"File JSON non trovato: {json_path}")

        data = load_json(json_path)
        required = ["ethereum_account_address", "chiave_account"]
        if any(field not in data for field in required):
            print(f"Errore: Campi essenziali mancanti nel JSON di configurazione SCA: {required}. Configurazione SCA danneggiata o incompleta.")
            raise ValueError(f"Campi mancanti nel JSON: {required}")

        self._json_path = json_path
        self.ethereum_account_address = data["ethereum_account_address"]
        self.chiave_account = data["chiave_account"]
        self.UID_contract_address = data.get("UID_contract_address")
        self.registered_universities = data["registered_universities"]

        try:
            self.blockchain_manager = SCABlockchainManager(self.DEFAULT_RPC_URL)
        except ConnectionError as e:
            print(f"Errore di connessione alla blockchain: {e}")
            raise

        abi_path = os.path.join(smart_contract_build_path, 'SmartContractAuthority/SmartContractAuthority.json')
        try:
            abi = load_json(abi_path)
        except FileNotFoundError:
            print(f"Errore: ABI del contratto SmartContractAuthority non trovata: {abi_path}")
            raise

        self.uid_contract_instance = self.blockchain_manager.get_contract_instance(self.UID_contract_address, abi)

    @staticmethod
    def create_sca(base_path: str, smart_contract_build_path: str):
        ethereum_account_address = input("Indirizzo Ethereum: ").strip()
        chiave_account = input("Chiave dell'account: ").strip()

        root_dir = os.path.join(base_path, 'SCA')
        persistency_dir = os.path.join(root_dir, "persistency")
        
        try:
            os.makedirs(persistency_dir, exist_ok=False)
        except FileExistsError:
            print(f"Errore: La cartella di persistenza per SCA esiste già: {persistency_dir}. Si prega di rimuoverla o scegliere un percorso diverso.")
            raise

        try:
            temp_blockchain_manager = SCABlockchainManager(SmartContractAuthority.DEFAULT_RPC_URL)
        except ConnectionError as e:
            print(f"Errore di connessione alla blockchain durante la creazione della SCA: {e}")
            raise

        try:
            abi, bytecode = load_contract_interface(smart_contract_build_path, "SmartContractAuthority")
        except FileNotFoundError:
            print(f"Errore: File ABI/bytecode del contratto SmartContractAuthority non trovati in '{smart_contract_build_path}'. Assicurati che i contratti siano stati compilati.")
            raise

        try:
            UID_contract_address = temp_blockchain_manager.deploy_new_contract(
                ethereum_account_address, chiave_account, abi, bytecode
            )
            print(f"SmartContractAuthority deployed at address: {UID_contract_address}")
        except Exception as e:
            print(f"Errore durante il deploy del contratto SmartContractAuthority: {e}")
            raise

        data = {
            "ethereum_account_address": ethereum_account_address,
            "chiave_account": chiave_account,
            "UID_contract_address": UID_contract_address,
            "registered_universities": []
        }

        save_json(data, os.path.join(persistency_dir, "sca_data.json"))
        print("SCA creata con successo e configurazione salvata.")
        
        return SmartContractAuthority(root_dir, smart_contract_build_path)

    def save_json(self):
        data = {
            "ethereum_account_address": self.ethereum_account_address,
            "chiave_account": self.chiave_account,
            "UID_contract_address": self.UID_contract_address,
            "registered_universities": self.registered_universities
        }
        try:
            save_json(data, self._json_path)
        except Exception as e:
            print(f"Errore durante il salvataggio dei dati SCA nel file JSON '{self._json_path}': {e}")
            raise

    def register_university(self, uni: University):
        while True:
            UID = input("Inserisci l'UID (max 20 caratteri, senza spazi): ").strip()
            if " " in UID:
                print("Errore: L'UID non può contenere spazi.")
            elif len(UID) > 20:
                print("Errore: L'UID non può superare i 20 caratteri.")
            elif len(UID) == 0:
                print("Errore: L'UID non può essere vuoto.")
            elif UID in self.registered_universities:
                print("Errore: L'UID inserito risulta già utilizzato.")
            else:
                break

        self.registered_universities.append(UID)
        
        try:
            self.save_json()
        except Exception:
            print(f"Errore: Impossibile registrare l'Università '{uni.nome}' a causa di un errore di salvataggio persistente.")
            return None, None

        pub_numbers = uni.chiave_pubblica.public_numbers()
        modulus = pub_numbers.n
        exponent = pub_numbers.e

        pub_key_modulus_bytes = modulus.to_bytes((modulus.bit_length() + 7) // 8, byteorder='big')
        pub_key_exponent_bytes = exponent.to_bytes((exponent.bit_length() + 7) // 8, byteorder='big')

        try:
            receipt = self.blockchain_manager.register_university_on_chain(
                uid_contract_instance=self.uid_contract_instance,
                sca_address=self.ethereum_account_address,
                sca_private_key=self.chiave_account,
                uid=UID,
                pub_key_modulus_bytes=pub_key_modulus_bytes,
                pub_key_exponent_bytes=pub_key_exponent_bytes,
                sid_contract_address=uni.SID_contract_address,
                cid_contract_address=uni.CID_contract_address
            )
        except Exception as e:
            print(f"Errore durante la registrazione dell'Università '{uni.nome}' sulla blockchain: {e}")
            self.registered_universities.remove(UID)
            self.save_json()
            raise

        uni.update_uid(UID)
        uni.update_sca_contract_address(self.UID_contract_address)
        
        return UID, self.UID_contract_address

    def revoke_uid(self, uid):
        if uid not in self.registered_universities:
            print(f"Errore: L'UID '{uid}' non è registrato. Impossibile revocare.")
            return
        try:
            receipt = self.blockchain_manager.revoke_university_on_chain(
                uid_contract_instance=self.uid_contract_instance,
                sca_address=self.ethereum_account_address,
                sca_private_key=self.chiave_account,
                uid=uid
            )
        except Exception as e:
            print(f"Errore durante la revoca dell'UID '{uid}' sulla blockchain: {e}")
            raise
    def modify_university_info(self, uid: str, new_pub_key_modulus: bytes, new_pub_key_exponent: bytes,
                               new_is_revoked: bool, new_sid_contract_address: str, new_cid_contract_address: str):
        if uid not in self.registered_universities:
            print(f"Errore: L'UID '{uid}' non è registrato. Impossibile modificare le informazioni.")
            raise ValueError(f"University with UID '{uid}' is not registered.")

        try:
            self.blockchain_manager.modify_university_info_on_chain(
                uid_contract_instance=self.uid_contract_instance,
                sca_address=self.ethereum_account_address,
                sca_private_key=self.chiave_account,
                uid=uid,
                new_pub_key_modulus=new_pub_key_modulus,
                new_pub_key_exponent=new_pub_key_exponent,
                new_is_revoked=new_is_revoked,
                new_sid_contract_address=new_sid_contract_address,
                new_cid_contract_address=new_cid_contract_address
            )
            print(f"Informazioni Università (UID:{uid}) modificate con successo.")
        except Exception as e:
            print(f"Errore durante la modifica delle informazioni dell'Università '{uid}' sulla blockchain: {e}")
            raise

    def get_university_info(self, uid: str) -> tuple[bytes, bytes, bool, str, str]:
        if uid not in self.registered_universities:
            print(f"Errore: L'UID '{uid}' non è registrato. Impossibile recuperare informazioni.")
            raise ValueError(f"University with UID '{uid}' is not registered.")
        try:
            return self.blockchain_manager.get_university_info_on_chain(self.uid_contract_instance, uid)
        except Exception as e:
            print(f"Errore durante il recupero delle informazioni dell'Università '{uid}' dalla blockchain: {e}")
            raise

    def verify_sid(self, uid: str, sid: int) -> tuple[bytes, bytes, bool]:
        if uid not in self.registered_universities:
            print(f"Errore: L'UID '{uid}' non è registrato. Impossibile verificare SID.")
            raise ValueError(f"University with UID '{uid}' is not registered.")
        try:
            return self.blockchain_manager.verify_sid_on_chain(self.uid_contract_instance, uid, sid)
        except Exception as e:
            print(f"Errore durante la verifica del SID '{sid}' per l'Università '{uid}' dalla blockchain: {e}")
            raise

    def verify_cid(self, uid: str, cid: int) -> bool:
        if uid not in self.registered_universities:
            print(f"Errore: L'UID '{uid}' non è registrato. Impossibile verificare CID.")
            raise ValueError(f"University with UID '{uid}' is not registered.")
        try:
            return self.blockchain_manager.verify_cid_on_chain(self.uid_contract_instance, uid, cid)
        except Exception as e:
            print(f"Errore durante la verifica del CID '{cid}' per l'Università '{uid}' dalla blockchain: {e}")
            raise