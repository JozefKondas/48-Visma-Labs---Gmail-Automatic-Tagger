from modules.app import App

app = App()

frontendData = app.ui_handler.render_main_interface()
if frontendData[1] == "save":

    if frontendData[2]:
        app.generateUpdateTime(frontendData[0])

    app.conf.create_config(frontendData[0])
elif frontendData[1] == "reset":
    app.initStart()