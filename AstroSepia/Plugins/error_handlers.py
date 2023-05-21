from AstroSepia.combot import combot
import hikari
import lightbulb
from lightbulb.errors import MissingRequiredAttachmentArgument


def Embed(text, description):
    return hikari.Embed(title=text, description=description, color="#cc1616")


error_handlers = lightbulb.Plugin("Error handlers", "Bot setup errors")



@combot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:

    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            Embed(
                text="🤖 **Ops . . .**",
                description=f"Algo ha ido mal a la hora de ejecutar el comando `{event.context.invoked_with}`.",
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        raise event.exception
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.CommandIsOnCooldown):     
        await event.context.respond(
            Embed(
                "⚠️ **:cold_face: El comando posee cooldown.**",
                f"Intentalo de nuevo en `{exception.retry_after:.0f}` segundos.   ``({round(exception.retry_after) // 60}) minutos``",
            )
        )
    elif isinstance(exception, lightbulb.CommandAlreadyExists):   
        await event.context.respond(
            Embed(
                "❗ **Error al intentar crear el comando.**",
                f"El comando ``{event.context.invoked_with}`` ya existe.**",
            )
        )
    elif isinstance(exception, lightbulb.CommandNotFound):           
        await event.context.respond(Embed(
                f"❔ *El comando ``{event.context.invoked_with}`` no existe.*", 
                None
            )
        )
    elif isinstance(exception, lightbulb.MissingRequiredRole):  
        await event.context.respond(
            Embed(
                "🔒 **Se necesita unos determinados roles para ejecutar el comando**",
                None,
            )
        )
    elif isinstance(exception, lightbulb.MissingRequiredPermission): 
        await event.context.respond(
            Embed(
                "🔒 **Se necesita unos determinados permisos para ejecutar el comando.**",
                f"*Permisos requeridos:* ``{event.exception.missing_perms}``",
            )
        )
    elif isinstance(exception, MissingRequiredAttachmentArgument):
        await event.context.respond(
            Embed(
                "❗**Tienes que proporcionar un argumento adjunto**",
                f"Argumento requerido : ``{event.exception.missing_option}``",
            )
        )
    elif isinstance(exception, lightbulb.NotEnoughArguments):
        await event.context.respond(
            Embed(
                "❗ **Debes proporcionar los siguientes argumentos**",
                f"Argumentos faltantes: ``{[name.name for name in event.exception.missing_options]} --> {[desc.description for desc in event.exception.missing_options]}``.",
            )
        )
    elif isinstance(exception, lightbulb.NSFWChannelOnly):
        await event.context.respond(
            Embed(
                "⚠️ **Este comando solo puede ser utilizado en canales NSFW**",
                None,
            )
        )
    elif isinstance(exception, lightbulb.OnlyInDM):
        await event.context.respond(
            Embed("⚠️ **Este comando solo puede ser utilizado en DM's**", None)
        )
    elif isinstance(exception, lightbulb.OnlyInGuild):
        await event.context.respond(
            Embed(
                "⚠️ **Este comando solo puede ser utilizado en canales**", None
            )
        )
    elif isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(
            Embed(
                "🔒 **Debes ser Owner del bot para utilizar este comando.**",
                None,
            )
        )
    elif isinstance(exception, lightbulb.BotMissingRequiredPermission):
        await event.context.respond(
            Embed(
                "❗ **El bot no posee los permisos para ejecutar el comando.**",
                f"Permisos requeridos: ``{[perms.name for perms in event.exception.missing_perms]}``**",
            )
        )
    elif isinstance(exception, lightbulb.BotOnly):
        await event.context.respond(
            Embed("❗ **Solo el bot puede ejecutar este comando! **", None)
        )
    else:
        raise exception




#* Load the plugin in
def load(combot):
    combot.add_plugin(error_handlers)
#* Unload the plugin 
def unload(combot):
    combot.remove_plugin(error_handlers)