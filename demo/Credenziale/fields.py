from abc import ABC, abstractmethod

class Property(ABC):
    def __init__(self, nonce, merkle_proof=None):
        self.nonce = nonce
        self.merkle_proof = merkle_proof if merkle_proof is not None else []

    @abstractmethod
    def toString(self):
        pass

    @abstractmethod
    def toDict(self):
        pass

    @classmethod
    @abstractmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        pass

class SubjectInfo(Property):
    def __init__(self, name: str, surname: str, birthDate: str, gender: str, nationality: str, documentNumber: str, documentIssuer: str, email: str, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.name = name
        self.surname = surname
        self.birthDate = birthDate
        self.gender = gender
        self.nationality = nationality
        self.documentNumber = documentNumber
        self.documentIssuer = documentIssuer
        self.email = email

    def toString(self):
        return (
            self.name +
            self.surname +
            self.birthDate +
            self.gender +
            self.nationality +
            self.documentNumber +
            self.documentIssuer +
            self.email +
            str(self.nonce)
        )

    def toDict(self):
        return {
            "typology": "SubjectInfo",
            "data": {
                "name": self.name,
                "surname": self.surname,
                "birthDate": self.birthDate,
                "gender": self.gender,
                "nationality": self.nationality,
                "documentNumber": self.documentNumber,
                "documentIssuer": self.documentIssuer,
                "email": self.email
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(
                data["name"],
                data["surname"],
                data["birthDate"],
                data["gender"],
                data["nationality"],
                data["documentNumber"],
                data["documentIssuer"],
                data["email"],
                nonce,
                merkle_proof
            )
        except KeyError as e:
            raise ValueError(f"Missing key in SubjectInfo data: {e}")


class ErasmusInfo(Property):
    def __init__(self, programName: str, startActivity: str, endActivity: str, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.programName = programName
        self.startActivity = startActivity
        self.endActivity = endActivity

    def toString(self):
        return self.programName + self.startActivity + self.endActivity + str(self.nonce)

    def toDict(self):
        return {
            "typology": "ErasmusInfo",
            "data": {
                "programName": self.programName,
                "startActivity": self.startActivity,
                "endActivity": self.endActivity
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(data["programName"], data["startActivity"], data["endActivity"], nonce, merkle_proof)
        except KeyError as e:
            raise ValueError(f"Missing key in ErasmusInfo data: {e}")

class Course(Property):
    def __init__(self, name: str, achieved: bool, grade: int, cfu: int, achievementData: str, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.name = name
        self.achieved = achieved
        self.grade = grade
        self.cfu = cfu
        self.achievementData = achievementData

    def toString(self):
        return self.name + str(self.achieved) + str(self.grade) + str(self.cfu) + self.achievementData + str(self.nonce)

    def toDict(self):
        return {
            "typology": "Course",
            "data": {
                "name": self.name,
                "achieved": self.achieved,
                "grade": self.grade,
                "cfu": self.cfu,
                "achievementData": self.achievementData
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(data["name"], data["achieved"], data["grade"], data["cfu"], data["achievementData"], nonce, merkle_proof)
        except KeyError as e:
            raise ValueError(f"Missing key in Course data: {e}")

class ExtraActivity(Property):
    def __init__(self, name: str, cfu: int, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.name = name
        self.cfu = cfu

    def toString(self):
        return self.name + str(self.cfu) + str(self.nonce)

    def toDict(self):
        return {
            "typology": "ExtraActivity",
            "data": {
                "name": self.name,
                "cfu": self.cfu
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(data["name"], data["cfu"], nonce, merkle_proof)
        except KeyError as e:
            raise ValueError(f"Missing key in ExtraActivity data: {e}")

class Residence(Property):
    def __init__(self, typology: str, address: str, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.typology = typology
        self.address = address

    def toString(self):
        return self.typology + self.address + str(self.nonce)

    def toDict(self):
        return {
            "typology": "Residence",
            "data": {
                "typology": self.typology,
                "address": self.address
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(data["typology"], data["address"], nonce, merkle_proof)
        except KeyError as e:
            raise ValueError(f"Missing key in Residence data: {e}")

class Scholarship(Property):
    def __init__(self, amount: float, unit: str, payments: int, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.amount = amount
        self.unit = unit
        self.payments = payments

    def toString(self):
        return str(self.amount) + self.unit + str(self.payments) + str(self.nonce)

    def toDict(self):
        return {
            "typology": "Scholarship",
            "data": {
                "amount": self.amount,
                "unit": self.unit,
                "payments": self.payments
            },
            "nonce": self.nonce,
            "merkle_proof": self.merkle_proof
        }

    @classmethod
    def fromDict(cls, data, nonce, merkle_proof=None):
        try:
            return cls(data["amount"], data["unit"], data["payments"], nonce, merkle_proof)
        except KeyError as e:
            raise ValueError(f"Missing key in Scholarship data: {e}")
