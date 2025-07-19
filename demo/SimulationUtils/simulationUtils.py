import random
import copy
from Credential.fields import *

PREDEFINED_COURSES = [
    "Matematica Discreta",
    "Algoritmi e Strutture Dati",
    "Sistemi Operativi",
    "Reti di Calcolatori",
    "Basi di Dati",
    "Intelligenza Artificiale",
    "Ingegneria del Software",
    "Machine Learning",
    "Cybersecurity",
    "Blockchain Technology"
]

DUPLICABLE_CLASSES = [Course, ExtraActivity]
UNIQUE_CLASSES = [Residence, Scholarship]

def generate_random_property(cls):
    if cls == ErasmusInfo:
        return ErasmusInfo(
            programName="Erasmus+ Europe",
            startActivity="2024-09-01",
            endActivity="2025-01-31"
        )
    elif cls == Course:
        course_name = random.choice(PREDEFINED_COURSES)
        return Course(
            name=course_name,
            achieved=random.choice([True, False]),
            grade=random.randint(18, 30),
            cfu=random.choice([3, 6, 9]),
            achievementData="2025-02-15"
        )
    elif cls == ExtraActivity:
        return ExtraActivity(
            name=random.choice(["Volunteering", "Debate Club", "Internship"]),
            cfu=random.choice([1, 2, 3])
        )
    elif cls == Residence:
        return Residence(
            typology=random.choice(["on-campus", "off-campus"]),
            address=f"Via Università {random.randint(1, 100)}, City"
        )
    elif cls == Scholarship:
        return Scholarship(
            amount=random.randint(1000, 5000),
            unit="EUR",
            payments=random.randint(1, 3)
        )

def generate_random_properties(total=10):
    properties = []

    properties.append(generate_random_property(ErasmusInfo))

    used_unique_classes = set()
    while len(used_unique_classes) < len(UNIQUE_CLASSES) and len(properties) < total:
        cls = random.choice([c for c in UNIQUE_CLASSES if c not in used_unique_classes])
        properties.append(generate_random_property(cls))
        used_unique_classes.add(cls)

    while len(properties) < total:
        cls = random.choice(DUPLICABLE_CLASSES)
        properties.append(generate_random_property(cls))

    return properties

def tamper_all_credential_properties(original_credential: dict):
    tampered_credential = copy.deepcopy(original_credential)

    for prop in tampered_credential.get("properties", []):
        data = prop.get("data", {})
        typology = prop.get("typology", "")

        if typology == "Course":
            if "grade" in data and isinstance(data["grade"], int):
                data["grade"] = min(data["grade"] + 2, 30)
            if "cfu" in data and isinstance(data["cfu"], int):
                data["cfu"] += 1

        elif typology == "Scholarship":
            if "amount" in data and isinstance(data["amount"], (int, float)):
                data["amount"] += 1000
            if "payments" in data and isinstance(data["payments"], int) and data["payments"] > 1:
                data["payments"] -= 1

        elif typology == "ErasmusInfo":
            if "endActivity" in data:
                data["endActivity"] = "2025-06-30"

        elif typology == "Residence":
            if "typology" in data:
                data["typology"] = "private apartment"
            if "address" in data:
                data["address"] = "Via Libertà 99, City"

        elif typology == "ExtraActivity":
            if "cfu" in data and isinstance(data["cfu"], int):
                data["cfu"] += 1
            if "name" in data and isinstance(data["name"], str):
                data["name"] = data["name"] + " (Advanced)"

    return tampered_credential
