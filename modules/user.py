from modules.secret import Secret
from modules.inbox import Inbox

class User:
    def __init__(self):
        self.secret = Secret()
        self.inbox = None

    def setInbox(self, inbox):
        self.inbox = inbox

