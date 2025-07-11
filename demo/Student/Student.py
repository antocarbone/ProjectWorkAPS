

class Student:
    def __init__(self, name: str, surname: str, birthDate: str, gender: str, nationality: str, documentNumber: str, documentIssuer: str, email: str, nonce=None, merkle_proof=None):
        super().__init__(nonce, merkle_proof)
        self.SID = None
        self.pub_key = None
        self.priv_key = None
        self.name = name
        self.surname = surname
        self.birthDate = birthDate
        self.gender = gender
        self.nationality = nationality
        self.documentNumber = documentNumber
        self.documentIssuer = documentIssuer
        self.email = email
        self.credentials = []
        
    def set_sid(self, sid):
        self.SID = sid
        
    def challenge(self, nonce):
        #TODO: Implement challenge logic
        pass
    
    def generate_keys(self):
        if self.pub_key is None and self.priv_key is None:
            self.pub_key, self.priv_key = self.generate_keypair()
    
    def credentials_list(self):
        print("Credentials List:")
        for cred in self.credentials:
            print(cred.toJson())