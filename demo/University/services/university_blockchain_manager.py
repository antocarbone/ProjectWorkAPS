from web3.contract import Contract
# Importa dalla posizione corretta della classe base
from services.blockchain_manager import BaseBlockchainManager

class UniversityBlockchainManager(BaseBlockchainManager):
    def __init__(self, rpc_url: str):
        super().__init__(rpc_url)

    def register_sid_on_chain(self, sid_contract_instance: Contract, university_address: str, university_private_key: str, 
                              sid_counter: int, modulus_bytes: bytes, exponent_bytes: bytes) -> dict:
        nonce = self.get_transaction_count(university_address)
        gas_price = self.get_gas_price()

        tx_sid_data = sid_contract_instance.functions.registraSid(
            sid_counter,
            modulus_bytes,
            exponent_bytes,
            True
        ).build_transaction({
            'from': university_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })
        
        return self._send_and_wait_for_transaction(tx_sid_data, university_private_key, "Registrazione SID")

    def register_cid_on_chain(self, cid_contract_instance: Contract, university_address: str, university_private_key: str,
                              cid_counter: int) -> dict:
        nonce = self.get_transaction_count(university_address)
        gas_price = self.get_gas_price()

        tx_cid_data = cid_contract_instance.functions.registraCid(
            cid_counter,
            True
        ).build_transaction({
            'from': university_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })

        return self._send_and_wait_for_transaction(tx_cid_data, university_private_key, "Registrazione CID")

    def modifica_cid(self, cid_contract_instance: Contract, university_address: str, university_private_key: str,
                 cid: int, new_is_valid: bool) -> dict:
        nonce = self.get_transaction_count(university_address)
        gas_price = self.get_gas_price()

        tx_modifica_cid_data = cid_contract_instance.functions.modificaCid(
            cid,
            new_is_valid
        ).build_transaction({
            'from': university_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 800000
        })

        return self._send_and_wait_for_transaction(tx_modifica_cid_data, university_private_key, "Modifica CID")


    def verify_cid_on_chain(self, sca_contract_instance: Contract, university_id: str, certificate_id: int) -> bool:
        return self.call_contract_function(sca_contract_instance, "verificaCid", university_id, certificate_id)

    def get_university_info_on_chain(self, sca_contract_instance: Contract, university_id: str):
        return self.call_contract_function(sca_contract_instance, "getUniversityInfo", university_id)

    def verify_sid_on_chain(self, sca_contract_instance: Contract, university_id: str, student_id: int):
        return self.call_contract_function(sca_contract_instance, "verificaSid", university_id, student_id)