import os
import json
from web3 import Web3

def load_contract_interface(build_dir, contract_name):
    contract_path = os.path.join(build_dir, contract_name)
    abi_path = os.path.join(contract_path, f"{contract_name}.json")
    bin_path = os.path.join(contract_path, f"{contract_name}.bin")

    if not os.path.isfile(abi_path) or not os.path.isfile(bin_path):
        raise FileNotFoundError(f"File ABI o BIN mancante per il contratto {contract_name}")

    with open(abi_path, 'r') as f:
        abi = json.load(f)
    with open(bin_path, 'r') as f:
        bytecode = f.read()

    return abi, bytecode

def deploy_contract(w3: Web3, private_key: str, account_address: str, abi, bytecode):
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = contract.constructor().build_transaction({
        'from': account_address,
        'nonce': w3.eth.get_transaction_count(account_address),
        'gasPrice': w3.eth.gas_price,
        'gas': 2000000
    })

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise Exception("Deploy fallito")

    return receipt.contractAddress