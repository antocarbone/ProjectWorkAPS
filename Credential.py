from abc import ABC, abstractmethod

class Issuer:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def __str__(self):
        return self.id+self.name 
        
class Owner:
    def __init__(self, name, surname, cf, email, birthDate):
        self.name = name
        self.surname = surname
        self.cf = cf
        self.email = email
        self.birthDate = birthDate
        
    def __str__(self):
        return self.name+self.surname+self.cf+self.email+self.birthDate

class Property(ABC):
    @abstractmethod
    def toString(self):
        pass
    
class HiddenProperty(Property):
    def __init__(self, hash:str):
        self.hash = hash
    
    def toString(self):
        return self.hash
    
class ErasmusInfo(Property):
    def __init__(self, programName:str, startActivity:str, endActivity:str):
        self.programName = programName
        self.startActivity = startActivity
        self.endActivity = endActivity
        
    def toString(self):
        return self.programName+self.startActivity+self.endActivity
    
class Course(Property):
    def __init__(self, name:str, achieved:bool, grade:int, cfu:int, achievementData:str):
        self.name = name
        self.achieved = achieved
        self.grade = grade
        self.cfu = cfu
        self.achievementData = achievementData
        
    def toString(self):
        return self.name+str(self.achieved)+str(self.grade)+str(self.cfu)+self.achievementData

class ExtraActivity(Property):
    def __init__(self, name:str, cfu:int):
        self.name = name
        self.cfu = cfu

    def toString(self):
        return self.name+str(self.cfu)
     
class Residence(Property):
    def __init__(self, typology:str, address:str):
        self.typology = typology
        self.address = address
        
    def toString(self):
        return self.typology+self.address

class Scholarship(Property):
    def __init__(self, amount:float, unit:str, payments:int):
        self.amount = amount
        self.unit = unit
        self.payments = payments
    
    def toString(self):
        return str(self.amount)+self.unit+str(self.payments)
            
class Credential:
    def __init__(self, credentialId:str, issuranceDate:str, issuerData:Issuer, ownerData:Owner, properties:list):
        self.credentialId = credentialId
        self.issuranceDate = issuranceDate
        self.issuerData = issuerData
        self.ownerData = ownerData
        self.properties = properties
    
    def release():
        pass
        