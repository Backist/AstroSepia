from .combot import combot, current_mode, __mode__, __version__


import hikari
import datetime




if __name__ == "__main__":

    if current_mode == __mode__[0]:

        combot.run(
            activity= hikari.Activity(name= "tus servidores | <<about", type= hikari.ActivityType.WATCHING),
            asyncio_debug= True,
            check_for_updates= True,    #default True
            idle_since= datetime.datetime.now().astimezone()
        )

    elif current_mode == __mode__[1]:

        combot.run(
            activity= hikari.Activity(name= "⭕️ maintenance", type= hikari.ActivityType.PLAYING),
            asyncio_debug= True,
            check_for_updates= True,    #default True
            idle_since= datetime.datetime.now().astimezone()
        )
