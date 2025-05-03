from utils import *
import json
from merkle_tree import *
from hashlib import sha256

class Credential:
    def __init__(self, certificateId:str, issuranceDate:str, issuerInfo:Issuer, credentialSubject:Owner, properties:list):
        self.certificateId = certificateId
        self.issuranceDate = issuranceDate
        self.issuerInfo = issuerInfo
        self.credentialSubject = credentialSubject
        self.properties = properties
    
    def toJSON(self):
        outJson = {}
        outJson["certificateId"] = self.certificateId
        outJson["issuranceDate"] = self.issuranceDate
        outJson["issuerInfo"] = self.issuerInfo.__dict__
        outJson["credentialSubject"] = self.credentialSubject.__dict__
        propertiesJSON = []
        for property in self.properties:
            propertiesJSON.append(property.toDict())
        outJson["properties"] = propertiesJSON
        return json.dumps(outJson)
    
    def fromJSON(inJsonDict):
        certificateId = inJsonDict["certificateId"]
        issuranceDate = inJsonDict["issuranceDate"]
        
        issuerInfo = Issuer(
            inJsonDict["issuerInfo"]["id"], 
            inJsonDict["issuerInfo"]["name"]
        )
        
        credentialSubject = Owner(
            inJsonDict["credentialSubject"]["name"],
            inJsonDict["credentialSubject"]["surname"],
            inJsonDict["credentialSubject"]["cf"],
            inJsonDict["credentialSubject"]["email"],
            inJsonDict["credentialSubject"]["birthDate"]    
        )
        
        properties = []
        for property in inJsonDict["properties"]:
            if property["typology"] == "HiddenProperty":
                newProperty=HiddenProperty(
                        property["data"]["hash"]
                    )
            elif property["typology"] == "ErasmusInfo":
                newProperty=ErasmusInfo(
                        property["data"]["programName"], 
                        property["data"]["startActivity"], 
                        property["data"]["endActivity"]
                    )
            elif property["typology"] == "Course":
                newProperty=Course(
                        property["data"]["name"],
                        property["data"]["achieved"],
                        property["data"]["grade"],
                        property["data"]["cfu"],
                        property["data"]["achievementData"]
                    )
            elif property["typology"] == "ExtraActivity":
                newProperty=ExtraActivity(
                        property["data"]["name"],
                        property["data"]["cfu"] 
                    )
            elif property["typology"] == "Residence":
                newProperty=Residence(
                        property["data"]["typology"],
                        property["data"]["address"] 
                    )
            elif property["typology"] == "Scholarship":
                newProperty=Scholarship(
                        property["data"]["amount"],
                        property["data"]["unit"],
                        property["data"]["payments"]
                    )
            properties.append(newProperty)
        return Credential(certificateId, issuranceDate, issuerInfo, credentialSubject, properties)
    
    def hash(self):
        fixedPartHash = sha256((self.certificateId+self.issuranceDate+self.issuerInfo.__str__()+self.credentialSubject.__str__()).encode()).hexdigest()
        propertiesTree = MerkleTree(self.properties)
        propertiesHash = propertiesTree.root.elem
        return sha256((fixedPartHash+propertiesHash).encode()).hexdigest()