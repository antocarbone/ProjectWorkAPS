from Credential import *
from MerkleTree import *
from hashlib import sha256

credential = Certificate('1234567890', '01-09-2026', Issuer('1234', 'UNISA'), Owner('Antonio', 'Carbone', 'CRBNTN02S29H163Q', 'a.carbone88@studenti.unisa.it', '29-11-2002'), [Course('Alanizee 2', True, 21, 12, '12-11-2026')])
print(credential.toJSON())