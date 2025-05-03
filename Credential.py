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
        return Certificate(certificateId, issuranceDate, issuerInfo, credentialSubject, properties)