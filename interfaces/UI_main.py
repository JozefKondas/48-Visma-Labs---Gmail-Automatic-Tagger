import os
import math
import datetime
from datetime import datetime
from PIL import ImageTk
import PIL.Image as PILimage

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import tkinter as tk

from modules.config import Config

class Root():
    def __init__(self, config):
        #self.CONFIG = Config()
        self.conf = config
        self.status = None
        self.generateDate = False

    def render(self):
        self.root = Tk()
        self.root.title("GAT - Settings")
        w = 600
        h = 270
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()

        self.root.geometry('%dx%d+%d+%d' % (w, h, (ws / 2) - (w / 2), (hs / 2) - (h / 2)))
        self.root.register(0, 0)
        self.root.minsize(w, h)
        self.root.maxsize(w, h)

        hr_from_conf = math.floor(self.conf["settings"]["mailbox_check_interval"] / 60)

        mn_from_conf = self.conf["settings"]["mailbox_check_interval"] - (hr_from_conf*60)

        self.hourstr = tk.StringVar(self.root, hr_from_conf)
        self.minstr = tk.StringVar(self.root, mn_from_conf)

        self.root.wm_iconphoto(False, ImageTk.PhotoImage(PILimage.open('./resources/img/icon24.png')))
        background = ImageTk.PhotoImage(PILimage.open("./resources/img/background.jpg"))
        myLabel = Label(image=background)
        myLabel.pack()


        # mailbox checking interval
        Label(text="User: {}".format(self.conf["user"]["email"]), font=('calibri', 10, 'bold'), state="active").place(x=10, y=10)
        Label(text="Last update: {}".format(self.conf["settings"]["last_update"]), font=('calibri', 10, 'bold'), state="active").place(x=10, y=30)
        Label(text="Next update: {}".format(self.conf["settings"]["next_update"]), font=('calibri', 10, 'bold'), state="active").place(x=10, y=50)

        Label(text="---------------- SETTINGS ------------------", font=('calibri', 20, 'italic', 'bold'), state="active").place(x=100, y=70)
        Label(text="Checking new emails interval:", font=('calibri', 15, 'bold'), state="active").place(x=10, y=130)
        self.spin = Spinbox(self.root, from_=0, to=100, width=5, textvariable=self.hourstr, state="readonly").place(x=270,y=135)

        Label(text="hours ", font=('calibri', 15, 'bold')).place(x=330, y=130)

        self.spin1 = Spinbox(self.root, from_=0, to=60, width=5, textvariable=self.minstr, state="readonly").place(x=420,y=135)
        Label(text="minutes", font=('calibri', 15, 'bold')).place(x=480, y=130)
        Label(text="Retrain model interval", font=('calibri', 15, 'bold'), state="active").place(x=10, y=160)

        vlist = ["Every day", "Every week", "Every month", "Every year"]
        current = self.conf["settings"]["update_interval"]

        self.Combo = ttk.Combobox(self.root, values=vlist)
        self.Combo.current(current-1)
        self.Combo.pack(padx=10, pady=10)
        self.Combo.place(x=220, y=165)

        Button(text="Save and Exit", font=('calibri', 14, 'bold'), command=self.save_exit).place(x=165, y=210)
        Button(text="Reset", font=('calibri', 14, 'bold'), command=self.reset).place(x=365, y=210)

        self.root.mainloop()
        return self.conf, self.status, self.generateDate

    def trace_var(self,*args):
        if self.last_value == "59" and self.minstr.get() == "0":
            self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
        self.last_value = self.minstr.get()


    def save_exit(self):
        mailboxCheckInterval = int(self.hourstr.get()) * 60 + int(self.minstr.get())
        updateInterval = self.Combo.current() + 1

        if updateInterval != self.conf["settings"]["update_interval"]:
            self.generateDate = True

        self.conf["settings"]["mailbox_check_interval"] = mailboxCheckInterval
        self.conf["settings"]["update_interval"] = updateInterval

        self.status = "save"
        self.root.quit()


    def reset(self):
        self.conf["start"] = "init"
        self.status = "reset"
        self.root.destroy()


