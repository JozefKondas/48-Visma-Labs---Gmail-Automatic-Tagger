import os
import json
from datetime import datetime
from imap_tools import MailBox, AND

import pandas as pd

from modules.config import Config

SERVER = "imap.gmail.com"
CONFIG = Config()
LOAD = 5

class Inbox:
    def __init__(self):
        self.date = datetime.now().strftime("%d %b %Y %H:%M")
        self.conf = CONFIG.get_config()

        self.DATASET_PATH = "./resources/data/dataset.csv"

        self.mails = []

    def connect(self, new_user):
        status = None
        try:
            with MailBox(SERVER).login(new_user.secret.getEmail(), new_user.secret.getPassword()) as mailbox:
                status = mailbox.folder.status('INBOX')
        except:
            pass

        if status == None:
            return False

        self.user = new_user
        return True

    def getStatus(self, from_conf=False):
        if from_conf:
            return self.conf["inbox"]

        with MailBox(SERVER).login(self.user.secret.getEmail(), self.user.secret.getPassword()) as mailbox:
            status = mailbox.folder.status("INBOX")
        return status

    def saveStatus(self, config):
        status = self.getStatus()

        config["inbox"]["status_date"] = datetime.now().strftime("%d %b %Y %H:%M")
        for i, j in zip(config["inbox"]["status"], status):
            config["inbox"]["status"][i] = status[j]

    def getLabels(self):
        labels = []
        with MailBox(SERVER).login(self.user.secret.getEmail(), self.user.secret.getPassword()) as mailbox:
            for folder_info in mailbox.folder.list():
                label = folder_info.get('name')
                if 'Gmail' not in label and 'INBOX' not in label:
                    labels.append(label)
        return labels

    def getMails(self):
        self.mails = []
        for label in self.getLabels():
            # if len(self.mails) > LOAD:
            #     break
            mailbox = MailBox(SERVER)
            mailbox.login(self.user.secret.getEmail(), self.user.secret.getPassword(), initial_folder=label)
            for msg in mailbox.fetch(reverse=True):
                # if len(self.mails) > LOAD:
                #     break
                self.mails.append([label, msg.from_, msg.subject, msg.text])
        mailbox.logout()

        dataset = pd.DataFrame(self.mails, columns = ['tag','from','subject','body'])
        dataset.to_csv(self.DATASET_PATH)#, index=False);

    def checkForNewMails(self):
        untagged_mails = []
        current_status = self.getStatus()["MESSAGES"]
        local_status = CONFIG.get_config()["inbox"]["status"]["messages"]
        new_mails = current_status - local_status

        if new_mails > 0:
            with MailBox(SERVER).login(self.user.secret.getEmail(), self.user.secret.getPassword(), initial_folder="INBOX") as mailbox:
                for i, msg in enumerate(mailbox.fetch(reverse=True)):
                    untagged_mails.append(msg.uid)
                    if i == (new_mails-1):
                        break

        return untagged_mails

    def tagMail(self, uid, tag):
        with MailBox(SERVER).login(self.user.secret.getEmail(), self.user.secret.getPassword(), initial_folder="INBOX") as mailbox:
            # for msg in mailbox.fetch(AND(uid=uid), reverse=True):
            mailbox.seen(uid, False)
            mailbox.copy(uid, tag)

    def getMailText(self, uid):
        with MailBox(SERVER).login(self.user.secret.getEmail(), self.user.secret.getPassword(), initial_folder="INBOX") as mailbox:
            for msg in mailbox.fetch(AND(uid=uid), reverse=True):
                return msg.text



