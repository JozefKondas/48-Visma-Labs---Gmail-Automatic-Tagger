import os
import json

import datetime
import win32com.client

class Config:
    def __init__(self, create=False):
        self.CONFIG_PATH = "./resources/config/config.json"
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = {
            "date": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
            "start": "init",
            "user":{"email": None,"password": None},
            "inbox":{
                "status_date": None,
                "status":{
                    "messages": None,
                    "recent": None,
                    "uidnext": None,
                    "uidvalidity": None,
                    "unseen": None
                }
            },
            "settings": {
                "mailbox_check_interval": 60,
                "update_interval": 2,
                "last_update": None,
                "next_update": None
            }
        }

        if create:
            self.create_config(self.config)

    def create_config(self, config):
        with open(self.CONFIG_PATH, 'w') as config_file:
            json.dump(config, config_file, indent=2)

    def get_config(self):
        with open(self.CONFIG_PATH) as config_file:
            return json.load(config_file)

    def isExist(self):
        return True if os.path.isfile(self.CONFIG_PATH) else False

    def schedule(self, freq):
        frequency = freq
        frequency = str(frequency)
        frequency = 'PT' + frequency + 'M'

        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        task_def = scheduler.NewTask(0)

        # Create trigger
        start_time = datetime.datetime.now()
        TASK_TRIGGER_TIME = 1

        trigger = task_def.Triggers.Create(TASK_TRIGGER_TIME)
        trigger.StartBoundary = start_time.isoformat()

        # Create action
        TASK_ACTION_EXEC = 0
        action = task_def.Actions.Create(TASK_ACTION_EXEC)

        path = os.path.dirname(os.path.realpath(__file__)) + "/Tagger.exe" 
        print(path)

        # action.ID = 'DO NOTHING'
        # #action.Path = 'cmd.exe'
        # action.Path = path
        # action.Arguments = '/c "exit"'

        path = os.path.dirname(os.path.realpath(__file__)) + "/Tagger.exe" 
        #print(path)

        action.ID = 'tag email'
        #action.Path = 'cmd.exe'
        action.Path = path
        action.Arguments = '/c "exit"'



        # Set parameters
        task_def.RegistrationInfo.Description = 'This task check your mailbox and tag every new mail'
        task_def.Settings.Enabled = True
        task_def.Settings.StopIfGoingOnBatteries = False

        task_def.Settings.ExecutionTimeLimit = "PT60M"; # maximalna dlzka ako dlh bude bezat script
        task_def.Settings.Hidden = True

        trigger.Repetition.Interval = frequency

        task_def.Settings.RunOnlyIfNetworkAvailable = True

        # Register task
        # If task already exists, it will be updated
        TASK_CREATE_OR_UPDATE = 6
        TASK_LOGON_NONE = 0
        root_folder.RegisterTaskDefinition(
            'Gmail Automatic Tagger',  # Task name
            task_def,
            TASK_CREATE_OR_UPDATE,
            '',  # No user
            '',  # No password
            TASK_LOGON_NONE)

