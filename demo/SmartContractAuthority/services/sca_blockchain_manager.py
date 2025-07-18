from web3.contract import Contract
# Importa dalla posizione corretta della classe base
from services.blockchain_manager import BaseBlockchainManager

class SCABlockchainManager(BaseBlockchainManager):
    def __init__(self, rpc_url: str):
        super().__init__(rpc_url)

    def register_university_on_chain(self, uid_contract_instance: Contract, sca_address: str, sca_private_key: str,
                                     uid: str, pub_key_modulus_bytes: bytes, pub_key_exponent_bytes: bytes,
                                     sid_contract_address: str, cid_contract_address: str) -> dict:
        nonce = self.get_transaction_count(sca_address)
        gas_price = self.get_gas_price()

        tx_data = uid_contract_instance.functions.registraUniversita(
            uid,
            pub_key_modulus_bytes,
            pub_key_exponent_bytes,
            False,
            sid_contract_address,
            cid_contract_address
        ).build_transaction({
            'from': sca_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })

        return self._send_and_wait_for_transaction(tx_data, sca_private_key, f"Registrazione Università (UID: {uid})")

    def revoke_university_on_chain(self, uid_contract_instance: Contract, sca_address: str, sca_private_key: str,
                                   uid: str) -> dict:
        nonce = self.get_transaction_count(sca_address)
        gas_price = self.get_gas_price()

        tx_data = uid_contract_instance.functions.setRevokeStatusUniversita(
            uid,
            True
        ).build_transaction({
            'from': sca_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })

        return self._send_and_wait_for_transaction(tx_data, sca_private_key, f"Revoca Università (UID: {uid})")
    
    def modify_university_info_on_chain(self, uid_contract_instance: Contract, sca_address: str, sca_private_key: str,
                                        uid: str, new_pub_key_modulus: bytes, new_pub_key_exponent: bytes,
                                        new_is_revoked: bool, new_sid_contract_address: str, new_cid_contract_address: str) -> dict:
        nonce = self.get_transaction_count(sca_address)
        gas_price = self.get_gas_price()

        tx_data = uid_contract_instance.functions.modificaInfoUniversita(
            uid,
            new_pub_key_modulus,
            new_pub_key_exponent,
            new_is_revoked,
            new_sid_contract_address,
            new_cid_contract_address
        ).build_transaction({
            'from': sca_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })

        return self._send_and_wait_for_transaction(tx_data, sca_private_key, f"Modifica Info Università (UID: {uid})")

    def get_university_info_on_chain(self, uid_contract_instance: Contract, uid: str) -> tuple[bytes, bytes, bool, str, str]:
        return self.call_contract_function(uid_contract_instance, "getUniversityInfo", uid)

    def verify_sid_on_chain(self, uid_contract_instance: Contract, uid: str, sid: int) -> tuple[bytes, bytes, bool]:
        return self.call_contract_function(uid_contract_instance, "verificaSid", uid, sid)

    def verify_cid_on_chain(self, uid_contract_instance: Contract, uid: str, cid: int) -> bool:
        return self.call_contract_function(uid_contract_instance, "verificaCid", uid, cid)    