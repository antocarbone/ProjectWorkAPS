from Utils import *
import json

class Certificate:
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
    
    def fromJSON(json):
        pass