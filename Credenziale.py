class Issuer:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
class Owner:
    def __init__(self, name, surname, cf, birthDate):
        self.name = name
        self.surname = surname
        self.cf = cf
        self.birthDate = birthDate

class ErasmusInfo:
    def __init__(self, programName, startActivity, endActivity):
        self.programName = programName
        self.startActivity = startActivity
        self.endActivity = endActivity
        
class Course:
    def __init__(self, name, achieved, grade, cfu, achievementData):
        self.name = name
        self.achieved = achieved
        self.grade = grade
        self.cfu = cfu
        self.achievementData = achievementData

class ExtraActivity:
    def __init__(self, name, cfu):
        self.name = name
        self.cfu = cfu

class  Career:
    def __init__(self, departmentName, courses, extraActivivties):
        self.departmentName = departmentName
        self.courses = courses
        self.extraActivivties = extraActivivties
     
class Residence:
    def __init__(self, typology, address):
        self.typology = typology
        self.address = address

class Scholarship:
    def __init__(self, amount, unit, payments):
        self.amount = amount
        self.unit = unit
        self.payments = payments
    
class Properties:
    def __init__(self, erasmusInfo, careerInfo, residenceInfo, scholarshipInfo):
        self.erasmusInfo = erasmusInfo
        self.careerInfo = careerInfo
        self.residenceInfo = residenceInfo
        self.scholarshipInfo = scholarshipInfo
        
class Credential:
    def __init__(self, credentialId, issuranceDate, issuerData, ownerData, properties):
        self.credentialId = credentialId
        self.issuranceDate = issuranceDate
        self.issuerData = issuerData
        self.ownerData = ownerData
        self.properties = properties
    
    def release():
        pass
        