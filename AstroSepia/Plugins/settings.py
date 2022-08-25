from AstroSepia.combot import combot
from AstroSepia.Utils.consts import INFO_EMBED, ATTENTION_EMBED, ALERT_EMBED
from AstroSepia.Utils.utils import *
from AstroSepia.Utils.helpers import *

import hikari
import lightbulb
import datetime
import asyncio

"""
Extension para configurar o modificar los ajustes prestablecidos por el bot.

Caracteristicas:

Database: Si
Completo: No

Necesito hacer una clase para crear un embebido por cada boton presionado. (Mirar bot de referencia)
URL -> https://github.com/HyperGH/snedbot/blob/98ff10bc5527531e97d384b4d3efbdd79b510cd6/extensions/settings.py#L1236

Ademas, en esta extension iran todos los comandos relacionados con la configuracion de los ajustes.

"""

setts = lightbulb.Plugin("Settings", "Permite modificar los ajustes del bot | Internals", include_datastore= True)


async def privilege_usage(user: hikari.Member, guild: hikari.GatewayGuild) -> bool:
    """Verificar con un booleano que el usuario tiene permisos de administrador o creador para ejecutar comandos"""
    
    if user.id == guild.owner_id:
        return True

    u = await combot.cache.get_member(guild, user.id)
    ur = [role.id for role in u.get_roles()]
    for roles in ur:
        infrol = combot.cache.get_role(roles)
        if hikari.Permissions.ADMINISTRATOR or hikari.Permissions.MANAGE_GUILD in infrol.permissions:
            return True 
        return False

@setts.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.add_cooldown(600, 2, lightbulb.GuildBucket)
@lightbulb.command("settings", "Menu para modificar los ajustes del bot", aliases = ["internals"])
@lightbulb.implements(lightbulb.SlashCommandGroup, lightbulb.PrefixCommandGroup)
#async def settings(ctx : lightbulb.Context) -> None:



@setts.command
@lightbulb.option("extension", "Reiniciar una extension en especifico", choices= [exts for exts in combot.extensions])
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.add_cooldown(3600, 1, lightbulb.GuildBucket)
@lightbulb.command("refresh", "Reinicia las extensiones y vuelve a iniciarlas.", aliases= ["reloadext"], ephemeral= True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def reload_ext(ctx: lightbulb.Context) -> None:

    assert ctx.guild_id is not None

    if ctx.options.extension:
        combot.reload_extensions(f"AstroSepia.Plugins.{ctx.options.extension}")
    combot.reload_extensions()

    embed = hikari.Embed(
        title= "Extensiones Reiniciadas correctamente.",
        timestamp= datetime.datetime.now().astimezone()
    )
    await ctx.respond(embed)

@setts.command
@lightbulb.option("extension", "Remover una extension en especifico", choices= [exts for exts in combot.extensions])
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.add_cooldown(3600, 1, lightbulb.GuildBucket)
@lightbulb.command("removext", "Reinicia las extensiones y vuelve a iniciarlas.", aliases= ["unloadext"], ephemeral= True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def reload_ext(ctx: lightbulb.Context) -> None:

    assert ctx.guild_id is not None

    if ctx.options.extension:
        combot.unload_extensions(f"AstroSepia.Plugins.{ctx.options.extension}")

    embed = hikari.Embed(
        title= f"Extension {ctx.options.extension} removida correctamente.",
        timestamp= datetime.datetime.now().astimezone()
    )
    await ctx.respond(embed)




def load(combot):
    combot.add_plugin(setts)
def unload(combot):
    combot.remove_plugin(setts)