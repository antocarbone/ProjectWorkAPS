import os
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import hashes
import base64

from Credential.credential import Credential
from Credential.fields import SubjectInfo
from Student.student import Student

from SimulationUtils.simulationUtils import generate_random_properties

from University.utils.contract_utils import  load_contract_interface
from utils.file_utils import load_json,save_json, load_pem_key, save_pem_key_pair
from utils.crypto_utils import sign_hashed_data, gen_key_pair, recover_public_key_from_modulus_exponent, generate_random_nonce
from utils.identifiers_utils import *
from University.services.university_blockchain_manager import UniversityBlockchainManager


class University:
    DEFAULT_RPC_URL = 'http://127.0.0.1:7545'

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
        self.erasmus_students = data.get('erasmus_students')
        self.SID_contract_address = data.get("SID_contract_address")
        self.CID_contract_address = data.get("CID_contract_address")
        self.SCA_contract_address = data.get("SCA_contract_address")

        self.blockchain_manager = UniversityBlockchainManager(self.DEFAULT_RPC_URL)

        sid_abi_path = os.path.join(smart_contract_build_path, 'SIDSmartContract/SIDSmartContract.json')
        sid_abi = load_json(sid_abi_path)
        self.sid_contract_instance = self.blockchain_manager.get_contract_instance(self.SID_contract_address, sid_abi)

        cid_abi_path = os.path.join(smart_contract_build_path, 'CIDSmartContract/CIDSmartContract.json')
        cid_abi = load_json(cid_abi_path)
        self.cid_contract_instance = self.blockchain_manager.get_contract_instance(self.CID_contract_address, cid_abi)
        
        self.sca_contract_instance = None
        if self.SCA_contract_address:
            sca_abi_path = os.path.join(self.smart_contract_build_path, 'ISmartContractAuthorityPublic/ISmartContractAuthorityPublic.json')
            sca_abi = load_json(sca_abi_path)
            self.sca_contract_instance = self.blockchain_manager.get_contract_instance(self.SCA_contract_address, sca_abi)

    def update_uid(self, uid):
        self.UID = uid
        self.update_university_data()
        
    def update_erasmus_students(self, student: Student, cid: str):
        self.erasmus_students[student.SID] = cid
        self.update_university_data()
    
    def update_sca_contract_address(self, address):
        self.SCA_contract_address = address
        self.update_university_data()
        
        sca_abi_path = os.path.join(self.smart_contract_build_path, 'ISmartContractAuthorityPublic/ISmartContractAuthorityPublic.json')
        sca_abi = load_json(sca_abi_path)
        self.sca_contract_instance = self.blockchain_manager.get_contract_instance(self.SCA_contract_address, sca_abi)

    def update_university_data(self):
        data = {
            "UID": self.UID,
            "nome": self.nome,
            "ethereum_account_address": self.ethereum_account_address,
            "chiave_account": self.chiave_account,
            "SID_counter": self.SID_counter,
            "CID_counter": self.CID_counter,
            "erasmus_students": self.erasmus_students,
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
        
        try:
            self.blockchain_manager.register_sid_on_chain(
                sid_contract_instance=self.sid_contract_instance,
                university_address=self.ethereum_account_address,
                university_private_key=self.chiave_account,
                sid_counter=self.SID_counter,
                modulus_bytes=modulus_bytes,
                exponent_bytes=exponent_bytes
            )
        except Exception as e:
            raise Exception(f"Errore nella registrazione della chiave pubblica dello studente: {e}")
            

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

        my_uid = split_UID(self.UID)
        new_credential_cid = assemble_CID(my_uid, self.CID_counter)
        new_student_sid = assemble_SID(my_uid, self.SID_counter)
        credential = Credential(
            certificateId = new_credential_cid,
            studentId = new_student_sid,
            universityId=self.UID,
            issuanceDate="2023-10-01",
            properties=[info]
        )

        signature = sign_hashed_data(self.chiave_privata, credential.hash())
        credential.add_sign(signature)
        
        try:
            self.blockchain_manager.register_cid_on_chain(
                cid_contract_instance=self.cid_contract_instance,
                university_address=self.ethereum_account_address,
                university_private_key=self.chiave_account,
                cid_counter=self.CID_counter
            )
        except Exception as e:
            raise Exception(f"Errore nella registrazione della credenziale di immatricolazione: {e}")

        return credential,new_student_sid

    def register_erasmus_student(self, student: Student, json_credential: str):
        if not self.sca_contract_instance:
            raise Exception("Il contratto SmartContractAuthority (SCA) non è stato inizializzato. Impossibile verificare la credenziale Erasmus.")

        student_credential = Credential.fromJSON(json_credential)
        
        subject_info_props = [p for p in student_credential.properties if isinstance(p, SubjectInfo)]
        if len(subject_info_props) != 1:
            raise ValueError("La credenziale deve contenere esattamente una proprietà di tipo SubjectInfo.")

        if student_credential.UID == self.UID:
            raise Exception("Lo studente risulta già immatricolato presso questo ateneo e pertanto non può iniziare qui una carriera Erasmus.")
    
        origin_uid, origin_cid = split_CID(student_credential.CID)
        
        try:
            credential_is_valid = self.blockchain_manager.verify_cid_on_chain(
                self.sca_contract_instance,
                origin_uid,
                origin_cid
            )
            if not credential_is_valid:
                raise Exception("La credenziale associata a questo CID è stata revocata.")
            print("Il CID associato alla credenziale fornita risulta valido.")
        except Exception as e:
            raise Exception(f"Errore durante la verifica del CID sulla blockchain: {e}")

        try:
            origin_uni_pub_key_modulus, origin_uni_pub_key_exponent, is_revoked, _, _ = self.blockchain_manager.get_university_info_on_chain(
                self.sca_contract_instance,
                origin_uid
            )
            if is_revoked:
                raise Exception("L'UID dell'università che ha rilasciato questa credenziale è stato revocato!")
        except Exception as e:
            raise Exception(f"Errore durante il recupero delle informazioni dell'università di origine: {e}")

        try:
            origin_uni_public_key = recover_public_key_from_modulus_exponent(origin_uni_pub_key_modulus,origin_uni_pub_key_exponent)
            
            issuer_signature_bytes = base64.b64decode(student_credential.issuerSignature)
            hash_to_verify = bytes.fromhex(student_credential.hash())

            origin_uni_public_key.verify(
                issuer_signature_bytes,  
                hash_to_verify,          
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(hashes.SHA256()) 
            )
            print("Firma dell'issuer verificata correttamente.")
        except Exception as e:
            raise Exception(f"Errore durante la verifica della firma dell'issuer: {e}")

        _, sid = split_SID(student_credential.SID)
        
        try:
            pub_key_modulus, pub_key_exponent, is_sid_valid = self.blockchain_manager.verify_sid_on_chain(
                self.sca_contract_instance,
                origin_uid,
                sid
            )
            if not is_sid_valid:
                raise Exception("La credenziale presenta un SID non valido.")
            print("Il SID contenuto nella credenziale è valido.")
        except Exception as e:
            raise Exception(f"Errore durante la verifica del SID sulla blockchain: {e}")

        try:
            student_public_key = recover_public_key_from_modulus_exponent(pub_key_modulus,pub_key_exponent)

            nonce = generate_random_nonce() 
            signature_b64 = student.challenge(nonce) 
            
            signature_bytes = base64.b64decode(signature_b64)

            student_public_key.verify(
                signature_bytes,
                nonce,  
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )      
            print("Firma dello studente verificata correttamente.")
        except Exception as e:
            raise Exception(f"Errore durante la verifica della firma dello studente: {e}")
            
        print(f"Complimenti {student.name} {student.surname} \nImmatricolazione Erasmus completata!\n{self.nome} ti dà il benvenuto!")

    def request_career_credential(self, student: Student):
        self.CID_counter+=1
        self.update_university_data()
        erasmus_student_cid = self.erasmus_students[student.SID]
        _, sid = split_SID(student.SID)
        origin_uid, origin_cid = split_CID(erasmus_student_cid)
        if self.blockchain_manager.verify_cid_on_chain(self.sca_contract_instance, origin_uid, origin_cid):
            print("Credenziale di immatricolazione dello studente valida.")
            try:
                erasmus_student_pubkey_modulus, erasmus_student_pubkey_exponent, sid_is_valid = self.blockchain_manager.verify_sid_on_chain(
                    self.sca_contract_instance,
                    origin_uid,
                    sid
                )
                if not sid_is_valid:
                    raise Exception("Lo studene ha fornito un SID non valido.")
                print("Il SID fornito è valido.")
            except Exception as e:
                raise Exception(f"Errore durante la verifica del SID sulla blockchain: {e}")
            
            try:
                student_public_key = recover_public_key_from_modulus_exponent(erasmus_student_pubkey_modulus, erasmus_student_pubkey_exponent)

                nonce = generate_random_nonce() 
                signature_b64 = student.challenge(nonce) 
                
                signature_bytes = base64.b64decode(signature_b64)

                student_public_key.verify(
                    signature_bytes,
                    nonce,  
                    padding.PSS(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )      
                print("Challenge di autenticazione superata.")
            except Exception as e:
                raise Exception(f"Errore durante la verifica della firma dello studente: {e}")
            
            my_uid = split_UID(self.UID)
            properties = generate_random_properties(8)
            credential = Credential(
                certificateId=assemble_CID(my_uid, self.CID_counter),
                studentId=student.SID,
                universityId=self.UID,
                issuanceDate="2023-10-01",
                properties=properties
            )

            signature = sign_hashed_data(self.chiave_privata, credential.hash())
            credential.add_sign(signature)
            
            try:
                self.blockchain_manager.register_cid_on_chain(
                    cid_contract_instance=self.cid_contract_instance,
                    university_address=self.ethereum_account_address,
                    university_private_key=self.chiave_account,
                    cid_counter=self.CID_counter
                )
            except Exception as e:
                raise Exception(f"Errore nella registrazione della credenziale carriera: {e}")
            
            print(f"Complimenti {student.name} {student.surname} \nRichiesta della tua credenziale carriera completata!\nArrivederci da {self.nome}!")
            
            return credential
    
    def validate_shared_credential(self, student: Student, json_credential: str):
        if not self.sca_contract_instance:
            raise Exception("Il contratto SmartContractAuthority (SCA) non è stato inizializzato. Impossibile verificare la credenziale condivisa.")
            
        shared_credential = Credential.fromJSON(json_credential)
        
        issuer_uid = split_UID(shared_credential.UID)
        
        try:
            erasmus_uni_pubkey_modulus, erasmus_uni_pubkey_exponent, sid_isRevoked, _, _ = self.blockchain_manager.get_university_info_on_chain(self.sca_contract_instance, issuer_uid)
            if sid_isRevoked:
                raise Exception("L'università che ha rilasciato la credenziale condivisa non è più fidata.")
            print("L'università che ha rilasciato la credenziale condivisa è fidata.")
        except Exception as e:
            raise Exception(f"Errore nella verifica del'UID dell'università issuer: {e}")
        
        origin_uid, sid = split_SID(shared_credential.SID)
        try:
            student_pubkey_modulus, student_pubkey_exponent, sid_isValid = self.blockchain_manager.verify_sid_on_chain(self.sca_contract_instance, origin_uid, sid)
            if not sid_isValid:
                raise Exception("Il SID presente nella credenziale non è valido.")
            print("Il SID presente nella credenziale è valido.")
        except Exception as e:
            raise Exception(f"Errore nella verifica del SID contenuto nella credenziale: {e}")
        
        try:
            student_public_key = recover_public_key_from_modulus_exponent(student_pubkey_modulus, student_pubkey_exponent)

            nonce = generate_random_nonce() 
            signature_b64 = student.challenge(nonce) 
            
            challenge_signature_bytes = base64.b64decode(signature_b64)

            student_public_key.verify(
                challenge_signature_bytes,
                nonce,  
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )      
            print("Challenge di autenticazione superata.")
        except Exception as e:
            raise Exception(f"Errore durante la verifica della firma dello studente: {e}")    
        
        erasmus_uni_public_key = recover_public_key_from_modulus_exponent(erasmus_uni_pubkey_modulus, erasmus_uni_pubkey_exponent)

        issuer_signature = shared_credential.issuerSignature 
            
        issuer_signature_bytes = base64.b64decode(issuer_signature)
        try:
            final_hash = bytes.fromhex(shared_credential.hash())
            erasmus_uni_public_key.verify(
                issuer_signature_bytes,
                final_hash,  
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(hashes.SHA256()) 
            )      
            print("Le property sono state verificate correttamente!")
        except Exception as e:
            raise Exception(f"Errore durante la verifica della firma dell'issuer: {e}")
        
        print("La credenziale condivisa è valida")     
    
    def revoke_cid(self, full_cid: str):
        _, cid = split_CID(full_cid)
        try:
            self.blockchain_manager.modifica_cid(self.cid_contract_instance, self.ethereum_account_address, self.chiave_account, cid, False)
        except Exception as e:
            print(f"Errore durante la revoca del CID '{cid}' sulla blockchain: {e}")
            raise
        print(f"Credenziale {cid} revocata con successo!")
    
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

        temp_blockchain_manager = UniversityBlockchainManager(University.DEFAULT_RPC_URL)

        abi_sid, bytecode_sid = load_contract_interface(smart_contract_build_path, "SIDSmartContract")
        abi_cid, bytecode_cid = load_contract_interface(smart_contract_build_path, "CIDSmartContract")

        SID_contract_address = temp_blockchain_manager.deploy_new_contract(
            ethereum_account_address, chiave_account, abi_sid, bytecode_sid
        )
        print(f"SIDSmartContract deployed at: {SID_contract_address}")

        CID_contract_address = temp_blockchain_manager.deploy_new_contract(
            ethereum_account_address, chiave_account, abi_cid, bytecode_cid
        )
        print(f"CIDSmartContract deployed at: {CID_contract_address}")

        data = {
            "nome": nome,
            "ethereum_account_address": ethereum_account_address,
            "chiave_account": chiave_account,
            "SID_counter": 0,
            "CID_counter": 0,
            "erasmus_students": {},
            "SID_contract_address": SID_contract_address,
            "CID_contract_address": CID_contract_address
        }

        save_json(data, os.path.join(persistency_dir, "university_data.json"))
        print("Università creata con successo.")
        return University(root_dir, smart_contract_build_path)