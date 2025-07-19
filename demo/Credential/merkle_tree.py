import hashlib
from .fields import Property

class MerkleNode:
    def __init__(self, left=None, right=None, value=None):
        self.left = left
        self.right = right
        self.value = value

class MerkleTree:
    @staticmethod
    def _build_tree_nodes(nodes: list[MerkleNode]) -> MerkleNode:
        if not nodes:
            raise ValueError("Cannot build tree from empty list of nodes.")
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
        
        return MerkleTree._build_tree_nodes(new_level)

    @staticmethod
    def _get_proof_static(leaves: list[MerkleNode], index: int) -> list[tuple[str, str]]:
        if not (0 <= index < len(leaves)):
            raise IndexError("Leaf index out of range for Merkle proof generation.")

        proof = []
        current_level_nodes = leaves.copy()
        current_node_index_on_level = index 
        
        while len(current_level_nodes) > 1:
            new_level_nodes = []
            next_level_index_for_current_node = -1

            for i in range(0, len(current_level_nodes), 2):
                left_child = current_level_nodes[i]
                right_child = current_level_nodes[i + 1] if i + 1 < len(current_level_nodes) else left_child

                if current_node_index_on_level == i:
                    proof.append((right_child.value, 'R'))
                    next_level_index_for_current_node = len(new_level_nodes)
                elif current_node_index_on_level == i + 1:
                    proof.append((left_child.value, 'L'))
                    next_level_index_for_current_node = len(new_level_nodes)
                
                combined = left_child.value + right_child.value
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level_nodes.append(MerkleNode(value=parent_hash))
            
            current_level_nodes = new_level_nodes
            current_node_index_on_level = next_level_index_for_current_node
            
        return proof

    @staticmethod
    def compute_root_from_proof(leaf_hash: str, proof: list[tuple[str, str]]) -> str:
        computed_hash = leaf_hash
        for sibling_hash, sibling_position in proof:
            if sibling_position == 'R':
                combined = computed_hash + sibling_hash
            elif sibling_position == 'L':
                combined = sibling_hash + computed_hash
            else:
                raise ValueError("Posizione del fratello non valida nella prova. Deve essere 'L' o 'R'.")
            computed_hash = hashlib.sha256(combined.encode()).hexdigest()
        return computed_hash

    @staticmethod
    def get_merkle_root(properties: list[Property]) -> str:
        if not properties:
            raise ValueError("MerkleTree operations require at least one property.")
        if properties[0].merkle_proof:
            first_prop_hash = hashlib.sha256(properties[0].toHashString().encode()).hexdigest()
            expected_overall_merkle_root = MerkleTree.compute_root_from_proof(first_prop_hash, properties[0].merkle_proof)
            
            for i, prop in enumerate(properties):
                prop_hash = hashlib.sha256(prop.toHashString().encode()).hexdigest()
                computed_root_from_proof = MerkleTree.compute_root_from_proof(prop_hash, prop.merkle_proof)
                
                if computed_root_from_proof != expected_overall_merkle_root:
                    raise ValueError(
                        f"Inconsistency detected in Merkle proofs for property {i} "
                        f"(Typology: {prop.toDict()['typology'] if hasattr(prop, 'toDict') else 'N/A'}). "
                        f"Computed root: {computed_root_from_proof}, Expected root: {expected_overall_merkle_root}"
                    )
            return expected_overall_merkle_root
        else:
            leaves = [
                MerkleNode(value=hashlib.sha256(p.toHashString().encode()).hexdigest())
                for p in properties
            ]
            
            root_node = MerkleTree._build_tree_nodes(leaves)
            overall_merkle_root = root_node.value
            
            return overall_merkle_root
        

    @staticmethod
    def populate_proofs(properties: list[Property]) -> str:
        if not properties:
            raise ValueError("MerkleTree operations require at least one property.")

        if properties[0].merkle_proof:
            print("Ignoring this request because properties proofs are already populated")
        else:
            leaves = [
                MerkleNode(value=hashlib.sha256(p.toHashString().encode()).hexdigest())
                for p in properties
            ]
            root_node = MerkleTree._build_tree_nodes(leaves)
            for i, p in enumerate(properties):
                p.merkle_proof = MerkleTree._get_proof_static(leaves, i)
            