from abc import ABC, abstractmethod
import random
import time
import json 

class Property(ABC):
    def __init__(self, merkle_proof=None):
        self.nonce = f"{int(time.time() * 1000)}{random.randint(1000, 9999)}"
        self.merkle_proof = merkle_proof if merkle_proof is not None else []

    def _dict_base(self, typology: str, data: dict) -> dict:
        out = {
            "typology": typology,
            "data": data,
            "nonce": self.nonce
        }
        if self.merkle_proof:
            out["merkle_proof"] = self.merkle_proof
        return out

    def set_merkle_proof(self, proof):
        self.merkle_proof = proof

    @abstractmethod
    def toString(self):
        pass

    @abstractmethod
    def toDict(self):
        pass

    @abstractmethod
    def toHashString(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        pass

class SubjectInfo(Property):
    def __init__(self, name, surname, birthDate, gender, nationality, documentNumber, documentIssuer, email, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.name = name
        self.surname = surname
        self.birthDate = birthDate
        self.gender = gender
        self.nationality = nationality
        self.documentNumber = documentNumber
        self.documentIssuer = documentIssuer
        self.email = email
        if nonce:
            self.nonce = nonce

    def toString(self):
        return self.name + self.surname + self.birthDate + self.gender + self.nationality + self.documentNumber + self.documentIssuer + self.email + str(self.nonce)

    def toDict(self):
        return self._dict_base("SubjectInfo", {
            "name": self.name,
            "surname": self.surname,
            "birthDate": self.birthDate,
            "gender": self.gender,
            "nationality": self.nationality,
            "documentNumber": self.documentNumber,
            "documentIssuer": self.documentIssuer,
            "email": self.email
        })

    def toHashString(self) -> str:
        data_str = (
            f"name{self.name}surname{self.surname}birthDate{self.birthDate}gender{self.gender}"
            f"nationality{self.nationality}documentNumber{self.documentNumber}"
            f"documentIssuer{self.documentIssuer}email{self.email}"
        )
        return f"typologySubjectInfoData{data_str}nonce{self.nonce}"

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["name"], data["surname"], data["birthDate"], data["gender"], data["nationality"], data["documentNumber"], data["documentIssuer"], data["email"], nonce, merkle_proof)

class ErasmusInfo(Property):
    def __init__(self, programName, startActivity, endActivity, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.programName = programName
        self.startActivity = startActivity
        self.endActivity = endActivity
        if nonce:
            self.nonce = nonce

    def toString(self):
        return self.programName + self.startActivity + self.endActivity + str(self.nonce)

    def toDict(self):
        return self._dict_base("ErasmusInfo", {
            "programName": self.programName,
            "startActivity": self.startActivity,
            "endActivity": self.endActivity
        })

    def toHashString(self) -> str:
        data_str = (
            f"programName{self.programName}startActivity{self.startActivity}endActivity{self.endActivity}"
        )
        return f"typologyErasmusInfoData{data_str}nonce{self.nonce}"

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["programName"], data["startActivity"], data["endActivity"], nonce, merkle_proof)

class Course(Property):
    def __init__(self, name, achieved, grade, cfu, achievementData, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.name = name
        self.achieved = achieved
        self.grade = grade
        self.cfu = cfu
        self.achievementData = achievementData
        if nonce:
            self.nonce = nonce

    def toString(self):
        return self.name + str(self.achieved) + str(self.grade) + str(self.cfu) + self.achievementData + str(self.nonce)

    def toDict(self):
        return self._dict_base("Course", {
            "name": self.name,
            "achieved": self.achieved,
            "grade": self.grade,
            "cfu": self.cfu,
            "achievementData": self.achievementData
        })

    def toHashString(self) -> str:
        return (
            f"typologyCourseData"
            f"name{self.name}"
            f"achieved{str(self.achieved)}"
            f"grade{str(self.grade)}"
            f"cfu{str(self.cfu)}"
            f"achievementData{self.achievementData}"
            f"nonce{self.nonce}"
        )

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["name"], data["achieved"], data["grade"], data["cfu"], data["achievementData"], nonce, merkle_proof)

class ExtraActivity(Property):
    def __init__(self, name, cfu, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.name = name
        self.cfu = cfu
        if nonce:
            self.nonce = nonce

    def toString(self):
        return self.name + str(self.cfu) + str(self.nonce)

    def toDict(self):
        return self._dict_base("ExtraActivity", {
            "name": self.name,
            "cfu": self.cfu
        })

    def toHashString(self) -> str:
        data_str = (
            f"name{self.name}cfu{str(self.cfu)}"
        )
        return f"typologyExtraActivityData{data_str}nonce{self.nonce}"

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["name"], data["cfu"], nonce, merkle_proof)

class Residence(Property):
    def __init__(self, typology, address, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.typology = typology
        self.address = address
        if nonce:
            self.nonce = nonce

    def toString(self):
        return self.typology + self.address + str(self.nonce)

    def toDict(self):
        return self._dict_base("Residence", {
            "typology": self.typology,
            "address": self.address
        })

    def toHashString(self) -> str:
        data_str = (
            f"typology{self.typology}address{self.address}"
        )
        return f"typologyResidenceData{data_str}nonce{self.nonce}"

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["typology"], data["address"], nonce, merkle_proof)

class Scholarship(Property):
    def __init__(self, amount, unit, payments, nonce=None, merkle_proof=None):
        super().__init__(merkle_proof)
        self.amount = amount
        self.unit = unit
        self.payments = payments
        if nonce:
            self.nonce = nonce

    def toString(self):
        return str(self.amount) + self.unit + str(self.payments) + str(self.nonce)

    def toDict(self):
        return self._dict_base("Scholarship", {
            "amount": self.amount,
            "unit": self.unit,
            "payments": self.payments
        })

    def toHashString(self) -> str:
        data_str = (
            f"amount{str(self.amount)}unit{self.unit}payments{str(self.payments)}"
        )
        return f"typologyScholarshipData{data_str}nonce{self.nonce}"

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        return cls(data["amount"], data["unit"], data["payments"], nonce, merkle_proof)
