from credential import *
from merkle_tree import *
from hashlib import sha256

f = open("credenziale.JSON")
json = json.load(f)
credential1 = Credential.fromJSON(json)
print(credential1.hash())

#corso=Course('Analizee', True, 25, 6, "12-11-2026")
#print(sha256(corso.toString().encode()).hexdigest())