from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
    
def init_blockchain_connection(address: str = 'http://127.0.0.1:7545'):
    connection = Web3(Web3.HTTPProvider(address))
    connection.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not connection.is_connected():
        raise ConnectionError("Impossibile connettersi a Ganache")
    return connection