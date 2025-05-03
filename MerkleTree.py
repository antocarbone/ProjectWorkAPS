import hashlib
import math
import Credential

class Node:
    def __init__(self, e):
        self.father = None
        self.right = None
        self.left = None
        self.elem = e
    
    def __str__(self):
        return self.elem
    
    def __repr__(self):
        return self.elem

class MerkleTree:
    def __init__(self, leaves:list):
        extendedLeaves=leaves.copy()
        inputLen = len(leaves)
        if inputLen == 0:
            raise ValueError()
        
        newLen = 2**(math.ceil(math.log2(inputLen)))
        for i in range(0,newLen-inputLen):
            extendedLeaves.append(leaves[-1])

        self.treeLeaves = []
        for i in range(0, newLen):
            if extendedLeaves[i] is Credential.HiddenProperty:
                self.treeLeaves.append(Node(extendedLeaves[i]))
            else:
                self.treeLeaves.append(Node(hashlib.sha256((extendedLeaves[i].toString()).encode()).hexdigest()))
        lastLayer = self.treeLeaves.copy()
        
        for j in range(0, int(math.log2(newLen))):    
            currentLayer = []
            for i in range(0, len(lastLayer), 2):
                node = Node(hashlib.sha256((lastLayer[i].elem + lastLayer[i+1].elem).encode()).hexdigest())
                node.left = lastLayer[i]
                node.right = lastLayer[i+1]
                lastLayer[i].father = node
                lastLayer[i+1].father = node
                currentLayer.append(node)
            lastLayer = currentLayer.copy()
        self.root = node