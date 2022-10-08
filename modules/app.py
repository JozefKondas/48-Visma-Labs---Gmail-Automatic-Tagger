import os
import json
import time

from datetime import datetime

from interfaces.UI_handler import UI_handler

from modules.config import Config
from modules.logger import Logs
from modules.user import User
from modules.inbox import Inbox
from modules.ai import Brain

CONFIG_PATH = "./resources/config/config.json"

class App:
    def __init__(self):
        self.time = datetime.now()
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.LOG_filename = "{}.log".format(datetime.now().strftime("%d%m%y%H%M"))
        self.LOG_PATH = "./resources/log/"

        self.conf = Config(False if os.path.isfile(CONFIG_PATH) else True)
        self.config = self.conf.get_config()
        self.object_logger = Logs.create_logger(self.LOG_PATH, self.LOG_filename, "APP")

        self.ui_handler = UI_handler(self.config)
        self.user = User()
        self.inbox = Inbox()
        self.brain = Brain()


        self.start = self.config["start"]

    def isLeapYear(self, year):
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


    def generateUpdateTime(self, config):
        daysByMonth = {"1": 31, "2": 28, "3": 31, "4": 30, "5": 31, "6": 30, "7": 31, "8":31, "9":30, "10":31, "11":30, "12":31}
        if(self.isLeapYear(self.time.year)):
            daysByMonth["2"] = 29

        updateConfig = self.config["settings"]["update_interval"]
        actualDay = self.time.day
        actualMonth = self.time.month
        actualYear = self.time.year

        if updateConfig == 1:
            updateDay = actualDay + 1
            updateMonth = actualMonth
            updateYear = actualYear

            if updateDay > daysByMonth[str(actualMonth)]:
                updateDay = 1
                updateMonth = actualMonth + 1

            if updateMonth > 12:
                updateYear += 1
                updateMonth = 1
                updateDay = 1

        elif updateConfig == 2:
            updateDay = actualDay + 7
            updateMonth = actualMonth
            updateYear = actualYear
            if updateDay > 31:
                daysInCurrentMonth = daysByMonth[str(actualMonth)]
                tmp = updateDay - daysInCurrentMonth
                updateMonth += 1
                updateDay = tmp

            if updateMonth > 12:
                updateYear += 1
                updateMonth = 1

        elif updateConfig == 3:
            updateDay = actualDay
            updateMonth = actualMonth + 1
            updateYear = actualYear

            if updateMonth > 12:
                updateYear += 1
                updateMonth = 1
                updateDay = 1

            if updateDay == 31:
                updateDay = daysByMonth[str(actualMonth+1)]

        elif updateConfig == 4:
            updateDay = actualDay
            updateMonth = actualMonth
            updateYear = actualYear + 1

        updateTime = datetime(updateYear, updateMonth, updateDay).strftime("%d.%m.%Y %H:%M")
        config["settings"]["next_update"] = str(updateTime)

    '''
        Scenar pre uplne prve spustenie aplikacie
        - Prve prihlasenie
        - ulozi sa heslo a mail
        - Nastavi sa config file
        - Stiahne sa dataset + cistenie datasetu
        - Natrenuje sa model a ulozi sa
    '''
    def initStart(self):
        self.object_logger.info("[INIT]  App started")

        # LOGIN
        logged = False
        frontendData = self.ui_handler.render_login_interface()
        if frontendData["closed"]:
            exit()

        self.user.secret.setEmail(frontendData["email"])
        self.user.secret.setPassword(frontendData["password"])
        self.config["user"]["email"] = frontendData["email"]
        self.config["user"]["password"] = frontendData["password"]

        if self.inbox.connect(self.user):
            self.user.setInbox(self.inbox)
            self.brain.set_labels(self.user.inbox.getLabels())
            self.user.inbox.saveStatus(self.config)
            logged = True
            self.object_logger.info("[LOGIN] Connection OK")
        else:
            self.object_logger.error("[LOGIN] Connection Failed")


        # Dataset + Model preparing
        if logged:
            self.object_logger.info("[DATASET] Download")
            self.user.inbox.getMails()
            self.object_logger.info("[DATASET] Complete")

            self.object_logger.info("[DATASET] Data preprocessing")
            self.brain.clean_dataset()

            self.object_logger.info("[MODEL] Train")
            self.brain.train()
            self.object_logger.info("[MODEL] Saved")

            self.config["settings"]["last_update"] = str(datetime.now().strftime("%d.%m.%Y %H:%M"))
            self.config["start"] = "normal"
            self.object_logger.info("[CONFIG] Config file updated")
            self.ui_handler.render_main_interface()
            self.generateUpdateTime(self.config)

            try:
                self.conf.schedule(self.config["settings"]["mailbox_check_interval"])
                self.object_logger.info("[SCHEDULER] Task was scheduled")

            except:
                self.object_logger.error("[SCHEDULER] Failed")

        self.conf.create_config(self.config)



    '''
        Scenar pre bezne spustenie aplikacie
        - Prihlasenie
        - skontroluje ci netreba updatnut dataset a pretrenovat model
        - Ak hej stiahne new data a pretrenuje model
        - Nacita model
        - Skontroluje mailbox
        - Ak su nove maily predikuje a taguje
        - Zaspi a caka na dalsiu kontrolu
    '''
    def normalStart(self):
        self.object_logger.info("[INIT]  App started")

        self.user.secret.setEmail(self.config["user"]["email"])
        self.user.secret.setPassword(self.config["user"]["password"])
        logged = False
        if self.inbox.connect(self.user):
            self.user.setInbox(self.inbox)
            self.brain.set_labels(self.user.inbox.getLabels())
            logged = True
            self.object_logger.info("[LOGIN] Connection OK")
        else:
            self.object_logger.error("[LOGIN] Connection Failed")

        if logged:
            updateTime = datetime.strptime(self.config["settings"]["next_update"], '%d.%m.%Y %H:%M')
            if self.time > updateTime:
                self.object_logger.info("[DATASET] Update")
                self.object_logger.info("[DATASET] Download")
                self.user.inbox.getMails()
                self.object_logger.info("[DATASET] Complete")

                self.object_logger.info("[DATASET] Data preprocessing")
                self.brain.clean_dataset()
                self.object_logger.info("[MODEL] Pre trained")
                self.brain.train()
                self.object_logger.info("[MODEL] Saved")

                self.generateUpdateTime(self.config)
                self.config["settings"]["last_update"] = str(datetime.now().strftime("%d.%m.%Y %H:%M"))

            self.brain.load_model()
            self.object_logger.info("[MODEL] Load")

            mails = self.user.inbox.checkForNewMails()
            self.object_logger.info("[DATASET] Checked {} new".format(len(mails)))

            for uid in mails:
                body = self.user.inbox.getMailText(uid)
                prediction = self.brain.predict(body)

                if prediction != -1:
                    self.inbox.tagMail(uid, prediction)
                    self.object_logger.info("[MAILBOX] Mail (uid: {}) tagged: {}".format(uid, prediction))
                else:
                    self.object_logger.warning("[MAILBOX] Mail (uid: {}) can't be tagged because of wrong format".format(uid))
                
                self.user.inbox.saveStatus(self.config)
            self.conf.create_config(self.config)






