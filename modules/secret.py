class Secret:
    def __init__(self):
        self.__email = None
        self.__password = None

    def getEmail(self):
        return self.__email

    def getPassword(self):
        return self.__password

    def setEmail(self, email):
        self.__email = email

    def setPassword(self, pwd):
        self.__password = pwd


