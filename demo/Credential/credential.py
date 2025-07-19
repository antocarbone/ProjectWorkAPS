from .fields import *
import json
from .merkle_tree import MerkleTree
from hashlib import sha256

class Credential:
    def __init__(self, certificateId: str, studentId: str, universityId: str, issuanceDate: str, properties: list, issuerSignature: str = None):
        self.CID = certificateId
        self.SID = studentId
        self.UID = universityId
        self.issuanceDate = issuanceDate
        self.properties = properties
        self.issuerSignature = issuerSignature

    def toJSON(self):
        outJson = {
            "certificateId": self.CID,
            "studentId": self.SID,
            "universityId": self.UID,
            "issuanceDate": self.issuanceDate,
            "properties": [p.toDict() for p in self.properties]
        }
        
        if self.issuerSignature:
            outJson["issuerSignature"] = self.issuerSignature
            
        return json.dumps(outJson, indent=4)

    @staticmethod
    def fromJSON(inJsonStr: str):
        try:
            inJsonDict = json.loads(inJsonStr)
            certificateId = inJsonDict["certificateId"]
            studentId = inJsonDict["studentId"]
            universityId = inJsonDict["universityId"]
            issuanceDate = inJsonDict["issuanceDate"]
            properties = []
            issuerSignature = inJsonDict.get("issuerSignature")

            for prop in inJsonDict["properties"]:
                typology = prop["typology"]
                data = prop["data"]
                nonce = prop.get("nonce")
                merkle_proof = prop.get("merkle_proof", [])

                if typology == "ErasmusInfo":
                    newProp = ErasmusInfo.fromDict(data, nonce, merkle_proof)
                elif typology == "Course":
                    newProp = Course.fromDict(data, nonce, merkle_proof)
                elif typology == "ExtraActivity":
                    newProp = ExtraActivity.fromDict(data, nonce, merkle_proof)
                elif typology == "Residence":
                    newProp = Residence.fromDict(data, nonce, merkle_proof)
                elif typology == "Scholarship":
                    newProp = Scholarship.fromDict(data, nonce, merkle_proof)
                elif typology == "SubjectInfo":
                    newProp = SubjectInfo.fromDict(data, nonce, merkle_proof)    
                else:
                    raise ValueError(f"Unsupported typology: {typology}")
                properties.append(newProp)

            return Credential(certificateId, studentId, universityId, issuanceDate, properties, issuerSignature)

        except KeyError as e:
            raise ValueError(f"Missing key in credential JSON: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    def hash(self):
        fixed_data = "credentialID" + self.CID + \
                     "issuerID" + self.UID + \
                     "issuanceDate" + self.issuanceDate + \
                     "studentID" + self.SID

        fixed_hash = sha256(fixed_data.encode()).hexdigest()
        merkle_root = MerkleTree.get_merkle_root(self.properties)
        final_hash = sha256((fixed_hash + merkle_root).encode()).hexdigest()
        return final_hash
    
    def add_sign(self, signature):
        self.issuerSignature = signature