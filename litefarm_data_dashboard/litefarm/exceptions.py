class NoDatabaseError(Exception):
    def __init__(self, location):
        self.location = location
        super().__init__("Could not find LiteFarm database")
