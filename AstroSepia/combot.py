from .logger import Logger

import os
import hikari
import lightbulb
import miru

combot = lightbulb.BotApp(
    token= os.environ["TOKEN"],        
    prefix= "<<", #* Options: $, >, --, .. 
    default_enabled_guilds= int(os.environ["DEBUG_GUILD_ID"]),
    owner_ids= [714486105767936069, 389446419016187907, 674620644389945425], #* SKEYLODA#5040
    help_slash_command= True,
    intents = hikari.Intents.ALL
)
miru.load(combot)

# AstroSepia's Version
__version__ = "1.1.1"
__mode__ = {0: "running", 1: "maintenance", 2: "sleeping", 3: "Developing"}

current_mode = __mode__[1]


#* ///////////////
#*     LOGGING
#* ///////////////

@combot.listen(hikari.StartingEvent)
async def is_starting(event: hikari.StartingEvent) -> None:
    Logger("w", "Initializing the bot")

@combot.listen(hikari.StartedEvent)
async def started(event: hikari.StartedEvent) -> None:
    Logger("w", "AstroSepia running!")

@combot.listen(hikari.StoppingEvent)
async def is_closing(event: hikari.StoppingEvent) -> None:
    Logger("w", "Stopping AstroSepia")
    
@combot.listen(hikari.StoppedEvent)
async def is_stopped(event: hikari.StoppedEvent) -> None:
    Logger("w", "AstroSepia was stopped correctly")



#* ///////////////////////
#*     EXTENSIONS
#* //////////////////////


combot.load_extensions(    
    "AstroSepia.Plugins.meta",
    "AstroSepia.Plugins.error_handlers",
    "AstroSepia.Plugins.admin",
    "AstroSepia.Plugins.pokedex",
    "AstroSepia.Plugins.settings",
    "AstroSepia.Plugins.music",
    "AstroSepia.Plugins.events",
    "AstroSepia.Plugins.components"
    #"AstroSepia.Plugins.permadeath"
    )



