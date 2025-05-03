from Credential import *
from MerkleTree import *
from hashlib import sha256

testLeaves = [
    ErasmusInfo('Erasmus+', '28-09-2026', '28-12-2026'), 
    HiddenProperty(sha256(b'ciao').hexdigest()),
    Course('Analisi 2', True, 27, 9, '02-08-2022')
    ]

tree = MerkleTree(testLeaves)
for elem in testLeaves:
    print(sha256(elem.toString().encode()).hexdigest())
print(tree.root)
print(tree.treeLeaves)