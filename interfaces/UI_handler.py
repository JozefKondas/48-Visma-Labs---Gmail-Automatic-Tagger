from tkinter import *
from tkinter.ttk import *

from interfaces.UI_login import UI_login
from interfaces.UI_main import Root

class UI_handler:
    def __init__(self, config):
        self.ui_login = UI_login()
        self.ui_main = Root(config)

    def render_login_interface(self):
        return self.ui_login.render()

    def render_main_interface(self):
        return self.ui_main.render()
