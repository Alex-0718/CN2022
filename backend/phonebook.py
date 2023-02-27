from datetime import datetime

class phonebook():
    def __init__(self, username = None, sdp = None, candidates = None, target = None):
        self.username = username
        self.sdp = sdp
        self.candidates = candidates
        self.target = target
        self.create_time = datetime.now()

    def to_json(self):
        return {
            "username": self.username,
            "sdp": self.sdp,
            "candidates": self.candidates,
            "target": self.target
        }