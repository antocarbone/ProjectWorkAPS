import hashlib
from .fields import Property

class MerkleNode:
    def __init__(self, left=None, right=None, value=None):
        self.left = left
        self.right = right
        self.value = value

class MerkleTree:
    def __init__(self, properties: list[Property]):
        if not properties:
            raise ValueError("MerkleTree requires at least one property")
        
        self.leaves = [
            MerkleNode(value=hashlib.sha256(p.toHashString().encode()).hexdigest())
            for p in properties
        ]

        self.root = self.build_tree(self.leaves)

        for i, p in enumerate(properties):
            p.merkle_proof = self.get_proof(i)

    def build_tree(self, nodes):
        if len(nodes) == 1:
            return nodes[0]

        new_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
            combined = left.value + right.value
            parent_hash = hashlib.sha256(combined.encode()).hexdigest()
            parent_node = MerkleNode(left, right, parent_hash)
            new_level.append(parent_node)
        return self.build_tree(new_level)

    def get_proof(self, index):
        proof = []
        nodes = self.leaves.copy()
        while len(nodes) > 1:
            new_nodes = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                combined = left.value + right.value
                parent = hashlib.sha256(combined.encode()).hexdigest()
                new_nodes.append(MerkleNode(value=parent))

                if i == index or i + 1 == index:
                    sibling = right if index == i else left
                    proof.append(sibling.value)
                    index = len(new_nodes) - 1

            nodes = new_nodes
        return proof

    def get_root(self):
        return self.root.value

    @staticmethod
    def compute_root(leaf_hash: str, proof: list[str]):
        computed_hash = leaf_hash
        for sibling_hash in proof:
            combined = computed_hash + sibling_hash
            computed_hash = hashlib.sha256(combined.encode()).hexdigest()
        return computed_hash
