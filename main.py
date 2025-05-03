from Credential import *
from MerkleTree import *
from hashlib import sha256

f = open("credenziale.JSON")
json = json.load(f)
credential = Certificate.fromJSON(json)
print(credential.toJSON())