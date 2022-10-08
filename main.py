from modules.app import App

app = App()
if app.start == "init":
    app.initStart()
else:
    app.normalStart()
