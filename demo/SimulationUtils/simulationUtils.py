import random
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
