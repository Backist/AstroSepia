from ..logger import Logger
from ..combot import combot
from ..Utils.consts import INFO_EMBED, ALERT_EMBED, CHANNEL_EMBED
from asyncio import TimeoutError

import os
import datetime
import hikari
import lightbulb

"""
Extension para determinar los eventos de cualquier contexto

Caracteristias:

Database: Determinar
Completo: No

Para notificar los eventos en un lugar, es necesario un canal donde notificarlos.

Deberiamos obtener de la base de datos el servidor y de ahi obtener el canal donde el usuario ha configurado
el canal para este tipo de eventos. Sino no hay configurado ninguno, mandar los eventos en el canal de sistema.

Cuando la DataBase sea creada, haré una funcion para acceder rapidamente y limpiar el codigo un poco mas

"""

events = lightbulb.Plugin("AstroSepia Events", "Base para los eventos de AstroSepia")


#async def obtain_sys_ch(guild: hikari.GatewayGuild):
#   await self.app.db.execute(...):
#       sys_channel = (Obtenido de la Db)
#   return sys_channel

async def default_system_ch(guild: hikari.GatewayGuild) -> bool:
    """Retorna un booleano si el servidor posee un canal de sistema o no."""
    if guild.system_channel_id is not None:
        return True
    return False


@events.listener(hikari.MessageCreateEvent)
async def PingBot(event: hikari.MessageCreateEvent) -> None:
    
    bot = combot.get_me()

    if (event.content == bot.mention) or (bot.mention in event.message.content if event.message.content is not None else event.content):
        embed= hikari.Embed(
            title= "**Hola!**",
            description= "**Que necesitas?**",
            color= INFO_EMBED
        ).set_footer(icon= combot.get_me().display_avatar_url, text= "")
        row = combot.rest.build_action_row()
        help_buttons = (
            ("Ayuda", hikari.ButtonStyle.SUCCESS, "help"),
            ("Estado", hikari.ButtonStyle.SECONDARY, "state")
        )
        for label, style, custom_id in help_buttons:
            (
                row
                .add_button(style, custom_id)
                .set_label(label)
                .add_to_container()
            )
        message = await combot.rest.create_message(event.channel_id, embed= embed, component= row)

        while True:
            try:
                event = await combot.wait_for(hikari.InteractionCreateEvent, timeout=60)            

            except TimeoutError or hikari.NotFoundError:
                await message.edit(components = [])
                break

            if event.interaction.custom_id == "help":
                embed= hikari.Embed(
                    title= f"**Coloca ``/about`` para obtener una guia con todos los comandos que puedes utilizar**",
                    color= INFO_EMBED
                )
                await message.edit(embed= embed, components = [])

            elif event.interaction.custom_id == "state":
                embed= hikari.Embed(
                    title= f"**Gracias por preguntar! Estoy bien Bip Bop ✨👾**",
                    color= INFO_EMBED
                )
                await message.edit(embed= embed, components = [])


@events.listener(hikari.GuildChannelCreateEvent)
async def channel(event: hikari.GuildChannelCreateEvent) -> None:

    if isinstance(event.channel, hikari.GuildVoiceChannel):

        embed = hikari.Embed(
                title= f"✏️ Canal de voz creado",
                description= f"**Nombre:** <#{event.channel.id}>\n**ID:** ``{event.channel.id}``",
                color= CHANNEL_EMBED,
                timestamp= datetime.datetime.now().astimezone()
            )
        await combot.rest.create_message(os.environ["EVENTS_GUILD_ID"], embed= embed)

    elif isinstance(event.channel, hikari.GuildTextChannel):

        embed = hikari.Embed(
                title= f"✏️ Canal de texto creado",
                description= f"**Nombre:** <#{event.channel.id}>\n**ID:** ``{event.channel.id}``",
                color= CHANNEL_EMBED,
                timestamp= datetime.datetime.now().astimezone()
            )
        await combot.rest.create_message(os.environ["EVENTS_GUILD_ID"], embed= embed)

    elif isinstance(event.channel, hikari.GuildNewsChannel):

        embed = hikari.Embed(
                title= f"✏️ Canal de noticias creado",
                description= f"**Nombre:** <#{event.channel.id}>\n**ID:** ``{event.channel.id}``",
                color= CHANNEL_EMBED,
                timestamp= datetime.datetime.now().astimezone()
            )
        await combot.rest.create_message(os.environ["EVENTS_GUILD_ID"], embed= embed)

    elif isinstance(event.channel, hikari.GuildStageChannel):

        embed = hikari.Embed(
                title= f"✏️ Canal de esceniario creado",
                description= f"**Nombre:** <#{event.channel.id}>\n**ID:** ``{event.channel.id}``",
                color= CHANNEL_EMBED,
                timestamp= datetime.datetime.now().astimezone()
            )
        await combot.rest.create_message(os.environ["EVENTS_GUILD_ID"], embed= embed)


@events.listener(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent) -> None:
        """Mensaje de bienvenida del bot"""

        guild = event.get_guild()
        assert guild is not None

        if await default_system_ch(guild):

            bot = event.guild.get_my_member()
            channel = event.guild.get_channel(event.guild.system_channel_id)

            assert bot is not None
            assert isinstance(channel, hikari.TextableGuildChannel)

            if not channel or not (hikari.Permissions.SEND_MESSAGES & lightbulb.utils.permissions_in(channel, bot)):
                return
            try:
                await channel.send(
                    embed= (
                        hikari.Embed(
                            title="Hola! Soy AstroSepia !",
                            description="""Puedes ver de todo lo que soy capaz y saber sobre mi escribiendo `/about` o `<<about`""",
                            color= INFO_EMBED,
                            )
                        .set_thumbnail(bot.avatar_url).set_image(bot.avatar_url)
                    )
                )
            except hikari.ForbiddenError:
                pass
            Logger(f"El bot ha entrado en el servidor: {event.guild.name} ({event.guild_id}).", "w")
        Logger(f"El servidor {event.guild_id}, no tiene un canal de sistema", "c")


@events.listener(hikari.MemberCreateEvent)
async def on_user_join(event: hikari.MemberCreateEvent) -> None:
    """Envia un mensaje privado al usuario que se a unido a un servidor"""

    guild = event.get_guild()
    assert guild is not None

    if await default_system_ch(guild):
        # if event.member.is_bot:
        #     await combot.rest.edit_member(event.guild_id, event.member.id, nickname= f"[<bot_prefix>]{event.member.name}")

        embed = (hikari.Embed(
                title= f"Bienvenido a ``{guild.name}``!",
                description= f"""Hola <@{event.member.mention if event.member else event.user_id}>,\nEste mensaje es generado automaticamente por {combot.get_me().mention}.
                Para acceder a todos los canales del servidor, visita <#{guild.system_channel_id if await default_system_ch(guild) else None}> y reacciona con un emoji.\n\nRecuerda que puedes contactar con los administradores del servidor para saber mas y consultar mis funciones dentro de el con ``/about`` o ``<<about``. Disfruta!!""",
                timestamp= datetime.datetime.now().astimezone(),
                color= INFO_EMBED
            )
            .set_author(name= f"Informacion de bienvenida de ``{guild.name}``",icon= guild.banner_url if guild.banner_url else None)
            .set_footer(text= f"Mensaje de bienvenida",icon= combot.get_me().display_avatar_url)
            .set_image(guild.banner_url if guild.banner_url else None)
            .set_thumbnail(guild.banner_url if guild.banner_url else None)
        )

        dm = await combot.rest.create_dm_channel(event.member.id if event.member else event.user_id)
        await dm.send(embed=embed)

    Logger(f"El servidor {event.guild_id}, no tiene un canal de sistema", "c")

    
def load(combot):
    combot.add_plugin(events)
def unload(combot):
    combot.remove_plugin(events)
