import re
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

import PIL
from PIL import ImageTk
from PIL import Image

from modules.config import Config

EMAIL_REGEX = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

class UI_login:
    def __init__(self):
        pass

    def render(self):
        self.view = Tk()
        self.view.title("Automatic Gmail Tagger")
        self.frontendData = {
            "email" : StringVar(self.view, ""),
            "password" : StringVar(self.view, ""),
            "save_data": IntVar(),
            "closed": False
        }

        w = 400
        h = 200
        ws = self.view.winfo_screenwidth()
        hs = self.view.winfo_screenheight()

        self.view.geometry('%dx%d+%d+%d' % (w, h, (ws/2) - (w/2), (hs/2) - (h/2)))
        self.view.register(0, 0)
        self.view.minsize(w, h)
        self.view.maxsize(w, h)

        self.view.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('./resources/img/icon24.png')))
        background = ImageTk.PhotoImage(Image.open("./resources/img/background.jpg"))
        myLabel = Label(image= background)
        myLabel.pack()

        Label(self.view, text="E-mail address", font=('calibri', 10, 'bold')).place(x=50, y=40)
        mail_input = Entry(self.view, textvariable=self.frontendData["email"])
        Label(self.view, text="Password", font=('calibri', 10, 'bold')).place(x=80, y=70)
        pwd_input = Entry(self.view, textvariable=self.frontendData["password"])

        mail_input.place(x=160, y=40)
        pwd_input.place(x=160, y=70)
        pwd_input.config(show="*")

        Style().configure('W.TButton', font=('calibri', 14, 'bold'))
        Button(self.view, text="Login", style='W.TButton', command=self.button_event).place(x=130, y=120)
        self.view.mainloop()

        return self.frontendData

    def button_event(self):

        fine = False
        if self.frontendData["email"].get() == "" or self.frontendData["password"].get() == "":
            messagebox.showinfo("Login Error", "Blank Not allowed")
        elif not (re.search(EMAIL_REGEX, self.frontendData["email"].get())):
            messagebox.showinfo("Login Error", "Invalid Email")
        else:
            fine = True

        if fine:
            self.frontendData["email"] = self.frontendData["email"].get()
            self.frontendData["password"] = self.frontendData["password"].get()
            self.frontendData["save_data"] = self.frontendData["save_data"].get()
            self.view.destroy()
