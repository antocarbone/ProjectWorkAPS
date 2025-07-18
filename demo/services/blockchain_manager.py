import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.contract import Contract

class BaseBlockchainManager:
    def __init__(self, rpc_url: str):
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if not self._w3.is_connected():
            raise ConnectionError(f"Impossibile connettersi alla blockchain all'URL: {rpc_url}")

    def get_web3_instance(self) -> Web3:
        return self._w3

    def get_contract_instance(self, contract_address: str, contract_abi: dict) -> Contract:
        if not contract_address:
            raise ValueError("L'indirizzo del contratto non può essere None.")
        if not contract_abi:
            raise ValueError("L'ABI del contratto non può essere vuota.")
        return self._w3.eth.contract(address=contract_address, abi=contract_abi)

    def get_transaction_count(self, account_address: str) -> int:
        return self._w3.eth.get_transaction_count(account_address)

    def get_gas_price(self) -> int:
        return self._w3.eth.gas_price

    def _send_and_wait_for_transaction(self, built_tx: dict, private_key: str, description: str = "Transazione") -> dict:
        try:
            signed_tx = self._w3.eth.account.sign_transaction(built_tx, private_key=private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                print(f"{description} completata con successo. Transaction Hash: {tx_hash.hex()}")
            else:
                raise Exception(f"{description} fallita. Transaction Hash: {tx_hash.hex()} Receipt: {receipt}")
            
            return receipt
        except Exception as e:
            print(f"Errore durante l'{description.lower()}: {e}")
            raise

    def deploy_new_contract(self, account_address: str, private_key: str, contract_abi: dict, contract_bytecode: str) -> str:
        contract = self._w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        
        transaction = contract.constructor().build_transaction({
            'from': account_address,
            'nonce': self._w3.eth.get_transaction_count(account_address),
            'gasPrice': self._w3.eth.gas_price,
            'gas': 3000000
        })

        signed_txn = self._w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = self._w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status != 1:
            raise Exception(f"Deploy del contratto fallito. Receipt: {tx_receipt}")

        return tx_receipt.contractAddress

    def call_contract_function(self, contract_instance: Contract, function_name: str, *args):
        if not hasattr(contract_instance.functions, function_name):
            raise AttributeError(f"Funzione '{function_name}' non trovata nel contratto.")
        
        return getattr(contract_instance.functions, function_name)(*args).call()