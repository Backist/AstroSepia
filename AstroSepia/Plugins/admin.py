import hashlib
from secrets import choice
from AstroSepia.Utils.consts import ATTENTION_EMBED, INFO_EMBED, SUCCESS_EMBED, ALERT_EMBED
from AstroSepia.Utils.helpers import RGB_REGEX, emojis
from AstroSepia.Utils.utils import *
from AstroSepia.descriptions import ADMIN_DESCRIPTION
from AstroSepia.combot import combot

import datetime
import re
from hashlib import sha512
from asyncio import create_task, wait, TimeoutError

import lightbulb
import hikari



admin = lightbulb.Plugin("Admin Commands | Tools", description= ADMIN_DESCRIPTION, include_datastore=True)


@admin.command()
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS, hikari.Permissions.MANAGE_GUILD))
@lightbulb.add_cooldown(20, 2, lightbulb.GuildBucket)
@lightbulb.option("name", "Nombre del canal. Valor REQUERIDO", required=True)
@lightbulb.option("category", "Indica la categoria donde se va a crear el comando", type = hikari.GuildCategory, required=True, channel_types= [hikari.ChannelType.GUILD_CATEGORY])
@lightbulb.option("position", "Posicion donde se va a crear el comando", type = int, required= True, min_value=0)
@lightbulb.option("type", "Indica el tipo de canal. TEXTO por defecto.", choices=["Voice", "Text", "News", "NSFW"], type= hikari.ChannelType, required=True)
@lightbulb.option("topic", "Indica los topicos del canal", type=str, required= False)
@lightbulb.add_checks(
    lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS),
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.add_cooldown(120.0, 2, lightbulb.GuildBucket)
@lightbulb.command("new_channel", "Crea un nuevo canal")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_channel(ctx: lightbulb.Context):

    if ctx.options.type == "Text":
        ch = await ctx.bot.rest.create_guild_text_channel(
            guild= ctx.guild_id, 
            name= ctx.options.name, 
            position= ctx.options.position, 
            topic= ctx.options.topic if ctx.options.topic else None, 
            category= ctx.options.category
        )
    elif ctx.options.type == "Voice":
        ch = await ctx.bot.rest.create_guild_voice_channel(
            guild= ctx.guild_id, 
            name= ctx.options.name, 
            position= ctx.options.position,
            category= ctx.options.category
        )
    elif ctx.options.type == "News":
        ch = await ctx.bot.rest.create_guild_news_channel(
            guild= ctx.guild_id,
            name = ctx.options.name,
            position= ctx.options.position,
            category= ctx.options.category,
            topic= ctx.options.topic if ctx.options.topic else None
        )
    elif ctx.options.type == "NSFW":
        ch = await ctx.bot.rest.create_guild_text_channel(
            guild = ctx.guild_id,
            name = ctx.options.name,
            nsfw= True,
            position= ctx.options.position,
            category= ctx.options.category,
            topic= ctx.options.topic if ctx.options.topic else None
        )

    embed= (
        hikari.Embed(
        title= "✅ Nuevo canal creado",
        description= f"Se ha creado el canal  <#{ch.id}>\nTipo: ``{ctx.options.type}``\nUbicacion: ``{ctx.options.category}``",
        color= "#52eb34",
        timestamp= datetime.datetime.now().astimezone()
    )
    .set_footer(f"Creado por {ctx.member.display_name}", icon= ctx.member.display_avatar_url)
    )
    await ctx.respond(embed= embed, flags= hikari.MessageFlag.EPHEMERAL)




@admin.command
@lightbulb.option("user", "Usuario al que se le va a cambiar el nickname", type= hikari.Member, required= True)
@lightbulb.option("nickname", "Nuevo nickname del usuario", required= True)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD),
    lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES)
)
@lightbulb.command("nickname", "Cambia el nickname de un usuario")
@lightbulb.implements(lightbulb.SlashCommand)
async def nickname(ctx: lightbulb.Context) -> None:

    assert ctx.guild_id is not None

    if len(ctx.options.nickname) <= 0 or len(ctx.options.nickname) >= 32:
        embed = hikari.Embed(
            title="Nickname Error",
            description="**El nickname no puede ser mayor de 32 caracteres.**",
            timestamp=datetime.datetime.now().astimezone(),
            color="#ebe134",
        )
    else:
        await ctx.bot.rest.edit_member(
            ctx.guild_id,
            user= ctx.options.user, 
            nickname= ctx.options.nickname, 
            reason= f"Nickname cambiado via ``/nickname | /chnick`` por {ctx.member.display_name}"
        )
        embed = hikari.Embed(
            title = "✅ Nickname cambiado correctamente",
            description= f"Se ha cambiado el nickname del usuario por ``{ctx.options.nickname}`` vía ``/nickname``",
            timestamp= datetime.datetime.now().astimezone(),
            color= "#52eb34"
        )
        await ctx.respond(embed= embed)


@admin.command
@lightbulb.command("User Avatar", "Muestra el avatar del usuario", ephemeral= True, pass_options = True)
@lightbulb.implements(lightbulb.UserCommand)
async def user_avatar(ctx: lightbulb.UserContext, target: hikari.Member) -> None:

    embed = (
        hikari.Embed(
            title= f"Avatar de ``{target.nickname if target.nickname else target.username}``  |  ID: ``{target.id}``"
        )
        .set_image(target.display_avatar_url)
    )
    await ctx.respond(embed)


@admin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.command("bot-exit", "Expulsar al bot del servidor. Este comando es peligroso", aliases = ["bkick"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def on_leave_guild(ctx: lightbulb.Context) -> None:
    
    assert ctx.guild_id is not None
    bot = ctx.bot.get_me()

    embed = (           
        hikari.Embed(
        title= "**``Hasta Pronto!``**",
        timestamp= datetime.datetime.now().astimezone()
        )
        .set_author(icon= bot.display_avatar_url)
        .set_footer(f"Enviado por {bot.username}", icon= bot.display_avatar_url)
    )
    await ctx.respond(embed= embed)
    await ctx.bot.rest.leave_guild(ctx.guild_id)


@admin.command
@lightbulb.add_cooldown(20, 2, lightbulb.ChannelBucket)
@lightbulb.add_checks(
    lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES, hikari.Permissions.READ_MESSAGE_HISTORY),
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
)
@lightbulb.option("user", "Solo elimina los mensajes de este usuario", type=hikari.User, required=False)
@lightbulb.option("regex", "Solo elimina los mensajes con esta expresion regular.", required=False)
@lightbulb.option("embeds", "Solo elimina los mensajes que sean de tipo embebido", type=bool, required=False)
@lightbulb.option("links", "Solo elimina los mensajes que sean o contengan links.", type=bool, required=False)
@lightbulb.option("invites", "Solo elimina los mensajes que sean o contengan invitaciones al servidor.", type=bool, required=False)
@lightbulb.option("attachments", "Solo elimina los mensajes que contengan archivos o imagenes.", type=bool, required=False)
@lightbulb.option("onlytext", "Solo elimina los mensajes que solo contengan texto.", type=bool, required=False)
@lightbulb.option("notext", "Solo elimina los mensajes que no contengan texto.", type=bool, required=False)
@lightbulb.option("endswith", "Solo elimina los mensajes que terminen por esta palabra o texto.", required=False)
@lightbulb.option("startswith", "Solo elimina los mensajes que comienzen por esta palabra o texto.", required=False)
@lightbulb.option("count", "La cantidad de mensajes que van a ser eliminados", type=int, min_value=1, max_value=400)
@lightbulb.option("since", "Elimina los mensajes a partir de una fecha.", type= int, min_value= 1, max_value= 30, required= False)
@lightbulb.command("purge", "Elimina los mensajes de este canal. \nEl comando eliminará los mensajes con una velocidad de 1msg/3s")
@lightbulb.implements(lightbulb.SlashCommand)
async def purge(ctx: lightbulb.Context) -> None:

    channel = ctx.get_channel() or await ctx.app.rest.fetch_channel(ctx.channel_id)
    assert isinstance(channel, hikari.TextableGuildChannel)

    predicator = [
        lambda message: not (hikari.MessageFlag.LOADING and message.flags)
    ]

    if ctx.options.regex:
        try:
            regex = re.compile(ctx.options.regex)
        except re.error as error:
            embed = hikari.Embed(
                title="❌ Expresion regular invalida",
                description=f"Fallo al analizar la expresion regular: ```{str(error)}```",
                color= "#ebe134"
            )
            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

            assert ctx.invoked is not None and ctx.invoked.cooldown_manager is not None
            return await ctx.invoked.cooldown_manager.reset_cooldown(ctx)

        else:
            predicator.append(lambda message, regex=regex: regex.match(message.content) if message.content else False)

    if ctx.options.startswith:
        predicator.append(
            lambda message: message.content.startswith(ctx.options.startswith) if message.content else False
        )

    if ctx.options.endswith:
        predicator.append(lambda message: message.content.endswith(ctx.options.endswith) if message.content else False)

    if ctx.options.notext:
        predicator.append(lambda message: not message.content)

    if ctx.options.onlytext:
        predicator.append(lambda message: message.content and not message.attachments and not message.embeds)

    if ctx.options.attachments:
        predicator.append(lambda message: bool(message.attachments)
        )
    if ctx.options.invites:
        predicator.append(
            lambda message: is_invite(message.content, fullmatch=False) if message.content else False
        )
    if ctx.options.links:
        predicator.append(
            lambda message: is_url(message.content, fullmatch=False) if message.content else False
        )
    if ctx.options.embeds:
        predicator.append(lambda message: bool(message.embeds)
        )
    if ctx.options.user:
        predicator.append(lambda message: message.author.id == ctx.options.user.id if ctx.options.user.id else None)

    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags= hikari.MessageFlag.EPHEMERAL)

    if messages := (
        ctx.app.rest.fetch_messages(channel)
        .take_until(
            lambda m: (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=ctx.options.since or 14)
            )
            > m.created_at
        )
        .filter(*predicator)
        .limit(int(ctx.options.count))
    ):
        try:

            tasks = []
            async for deletor in messages.chunk(150):
                task = create_task(combot.rest.delete_messages(channel, deletor))
                tasks.append(task)
                await wait(tasks)

            embed = hikari.Embed(
                title="🗑️ Mensajes eliminados",
                description=f"**{[sum(i) async for i in messages]}** mensajes han sido eliminados correctamente.",
                color= "#ebe134"
            )

        except hikari.BulkDeleteError as bulk_error:
            embed = hikari.Embed(
                title="🗑️ Mensajes eliminados",
                description=f"Solo **{len(bulk_error.messages_deleted)}/{len(messages)}** mensajes han sido eliminados debido a un error.",
                color= "#ebe134"
            )
            raise error
    else:
        embed = hikari.Embed(
            title="🗑️ No encontrado",
            description="No he encontrado mensajes con esas caracteristicas especificadas en las ultimas dos semanas",
            color="#ebe134",
        )

    await ctx.respond(embed=embed)


@admin.command
@lightbulb.option("spam", "Veces que se llamara al usuario", required= True, type= int, max_value= 150)
@lightbulb.option("message", "Envia algun mensaje junto a las menciones", required= True, type= str)
@lightbulb.option("user", "Usuario a spamear", required= True, type= hikari.Member)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.add_cooldown(600, 2, lightbulb.ChannelBucket)
@lightbulb.command("hkey", "Spamea la mencion de un usuario durante x veces")
@lightbulb.implements(lightbulb.SlashCommand)
async def spam(ctx: lightbulb.Context) -> None:

    member = ctx.bot.cache.get_member(ctx.guild_id, ctx.options.user)

    for iter in range(ctx.options.spam):
        await ctx.bot.rest.create_message(ctx.channel_id, content= f"{member.mention}  **{ctx.options.message}**")
    embed = hikari.Embed(
            title= f"Se ha spameado ``{iter}`` veces al usuario {member.mention}",
            description= f"Atacante: {ctx.member.display_name if ctx.member.display_name else ctx.author}",
            timestamp= datetime.datetime.now().astimezone()
        )
    await ctx.respond(embed= embed)


@admin.command
@lightbulb.option("helpembed", "Envia un mensaje de informacion al usuario", required= False, choices= ["True", "False"])
@lightbulb.option("reason", "Motivo del DM con el usuario o el mensaje que le quieres hacer llegar", required= False)
@lightbulb.option("user", "Abre el Dm con un usuario", required= True, type= hikari.Member)
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("createdm", "Manda un DM de prueba")
@lightbulb.implements(lightbulb.SlashCommand)
async def UserDm(ctx: lightbulb.Context) -> None:

    
    dm = await ctx.bot.rest.create_dm_channel(ctx.options.user)

    if ctx.options.helpembed:

        guild = await ctx.bot.rest.fetch_guild(ctx.guild_id)

        embed = (
            hikari.Embed(
                title="**✨ Hola! Me alegra poder hablar contigo en privado . . . ! ✨**",
                description=f"""\n\nVeras, este DM ha sido creado por el siguiente motivo: 
            \n```{ctx.options.reason if ctx.options.reason else None}```""",
            )
            .add_field(
                "**ℹ️ __Informacion adicional:__**",
                f"\nEste DM ha sido creado por <@{ctx.author.id}>.\nCreado a las {format_dtime(datetime.datetime.now().astimezone(), 'f')}\n",
            )
            .add_field(
                "\n**__Politica de los DM__**",
                f"""\nLos DM son responsabilidad del servidor, esto quiere decir que el autor del bot no se hace responsable de actividades conflictivas que pueda ocasionar este mensaje.\nSi necesitas saber mas sobre la politica de los DM's, porfavor, ponte en contacto o bien con el autor de este mensaje (Servidor: ``{guild.name}`` | ``Usuario: ``{ctx.author.id}``) o si lo desea con el creador del bot --> <@714486105767936069>""",
            )
            .set_author(icon=await ctx.bot.get_me().display_avatar_url)
            .set_image(await ctx.bot.cache.get_guild(ctx.guild_id).banner_url)
        )

        await dm.send(embed= embed)

    elif ctx.options.reason:
        embed = hikari.Embed(
            description= f"{ctx.options.reason}",
            color= INFO_EMBED
        )
        await dm.send(embed= embed)

    embed= hikari.Embed(
        title= f"**✅ Se ha creado correctamente un DM con el usuario ``{ctx.options.user}``**",
        color= SUCCESS_EMBED,
        timestamp= datetime.datetime.now().astimezone()
    )
    await ctx.respond(embed)



@admin.command
@lightbulb.set_help(
    "Este comando creara un embebido con botones personalizables. IMPORTANTE: Los botones seran eliminados en un maximo de 15 minutos como maximo."
)
@lightbulb.option(
    "button1",
    "Texto del boton 1. MAXIMO DE 4 BOTONES. Los botones iran en orden",
    type=str,
    required=True,
)
@lightbulb.option(
    "button2",
    "Texto del boton 2. MAXIMO DE 4 BOTONES. Los botones iran en orden",
    type=str,
    required=True,
)
@lightbulb.option(
    "button3",
    "Texto del boton 3. MAXIMO DE 4 BOTONES. Los botones iran en orden",
    type=str,
    required=True,
)
@lightbulb.option(
    "button4",
    "Texto del boton 4. MAXIMO DE 4 BOTONES. Los botones iran en orden",
    type=str,
    required=True,
)
@lightbulb.option(
    "colorb1",
    "Color de boton. COLORES PREDETERMINADOS DE DISCORD",
    required=True,
    choices=["Green", "Red", "Gray", "Blue"],
)
@lightbulb.option(
    "colorb2",
    "Color de boton. COLORES PREDETERMINADOS DE DISCORD",
    required=True,
    choices=["Green", "Red", "Gray", "Blue"],
)
@lightbulb.option(
    "colorb3",
    "Color de boton. COLORES PREDETERMINADOS DE DISCORD",
    required=True,
    choices=["Green", "Red", "Gray", "Blue"],
)
@lightbulb.option(
    "colorb4",
    "Color de boton. COLORES PREDETERMINADOS DE DISCORD",
    required=True,
    choices=["Green", "Red", "Gray", "Blue"],
)
@lightbulb.option(
    "message",
    "Mensaje a enviar junto los botones, si se establece",
    required=True,
    type= str,
    modifier= lightbulb.OptionModifier.CONSUME_REST
)
@lightbulb.option(
    "colormsg",
    "Color del embebido. Debe ser en formato RRR GGG BBB o en hexadecimal",
    type=hikari.Color,
    required=False,
)
@lightbulb.option(
    "link",
    "Agregar un link a un boton",
    required=False,
    choices=["Button1", "Button2", "Button3", "Button4"],
)
@lightbulb.option(
    "url",
    "Coloca la url",
    required=False,
    type= hikari.File.url,
)
@lightbulb.option(
    "timeout",
    "Duracion de los botones, al cabo de ese tiempo, los botones desaparecen. Minutos, ejemplo: 3m (0,3)",
    type=int,
    min_value=1,
    max_value=14,
    required=False,
)
@lightbulb.command("makepoll", "Crea una encuesta en el canal")
@lightbulb.implements(lightbulb.SlashCommand)
async def make_poll(ctx: lightbulb.Context) -> None:

    str_to_color = {
        "Blue": hikari.ButtonStyle.PRIMARY,
        "Gray": hikari.ButtonStyle.SECONDARY,
        "Green": hikari.ButtonStyle.SUCCESS,
        "Red": hikari.ButtonStyle.DANGER,
    }

    if ctx.options.colormsg and not RGB_REGEX.fullmatch(ctx.options.colormsg):
        embed = hikari.Embed(
            title="❌ Color Invalido",
            description="Los colores deben ser con el formato `RRR GGG BBB`, tres grupos de letras de tres letras.",
            color=ATTENTION_EMBED,
        )
        await ctx.respond(embed=embed)
        return

    if ctx.options.link and not isinstance(ctx.options.url, hikari.File):
        embed = hikari.Embed(
            title="❌ Direccion URL invalida",
            description="lA URL debe contener `HTTPS://`` en su direccion.",
            color=ATTENTION_EMBED,
        )
        await ctx.respond(embed=embed)
        return

    row = ctx.bot.rest.build_action_row()

    for i in range(1, 5):

        button = f"button{i}"
        text = ctx.options[button]

        if ctx.options.link == button:
            style = hikari.ButtonStyle.LINK
        else:
            style = str_to_color[ctx.options[f"colorb{i}"]]

        button = row.add_button(style, str(i)).set_label(text)

        if style == hikari.ButtonStyle.LINK:
            button.set_link(ctx.options.url)

        button.add_to_container()


    embed = hikari.Embed(title="✅ Encuesta Creada")
    await ctx.respond(embed=embed, flags= hikari.MessageFlag.EPHEMERAL)

    embed = hikari.Embed(description=f"{ctx.options.message}")
    msg = await ctx.respond(response_type= hikari.ResponseType.DEFERRED_MESSAGE_UPDATE, component= row, embed= embed)

    while True:
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, timeout= int(ctx.options.timeout*60) if ctx.options.timeout else 60)

        except TimeoutError:
            embed = hikari.Embed(
                title= ":hourglass_flowing_sand: **Se ha acabado el tiempo para votar**",
                color= ALERT_EMBED
            )
            await ctx.edit_last_response(embed= embed, components= [])
            break
        else:
            if event.interaction.custom_id == "1":
                await ctx.bot.rest.add_reaction(ctx.channel_id, await msg.message(), emoji= f"{emojis[ctx.options.colorb1]}")
                return
            elif event.interaction.custom_id == "2":
                await ctx.bot.rest.add_reaction(ctx.channel_id, await msg.message(), emoji= f"{emojis[ctx.options.colorb2]}")
                return
            elif event.interaction.custom_id == "3":
                await ctx.bot.rest.add_reaction(ctx.channel_id, await msg.message(), emoji= f"{emojis[ctx.options.colorb3]}")
                return
            elif event.interaction.custom_id == "4":
                await ctx.bot.rest.add_reaction(ctx.channel_id, await msg.message(), emoji= f"{emojis[ctx.options.colorb4]}")
                return


#! ARREGLAR NUKE COMMAND. MAXIMO 500 CANALES CREADOS
@admin.command
@lightbulb.add_cooldown(10000, 1, lightbulb.GlobalBucket)
@lightbulb.command("nuke", "THE OFFICIAL NUKE BOMB", aliases=["nukeall"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def nuke(ctx: lightbulb.Context) -> None:

    hashed_msgs = [
        sha512("SI ALGUN DIA LLEGAS A DESCIFRAR DE MANERA IMPOSIBLE ESTO QUE SEPAS QUE TU SERVIDOR FUE DESTRUIDO. SUBCODIGO DE DESTRUCCION: 0x0qaqwdfg3530895623".encode('utf-8')).hexdigest(),
        sha512("ESTO ES OTRO DE UNOS DE LOS TANTOS MENSAJES DE DESTRUCCION CON SUBCODIGO DE DESTRUCCION: 0x0asdasdapñklndfgsakplsnfghslkfnsdfgsl".encode('utf-8')).hexdigest()
    ]

    for i in range(1000):
        textChannel = await combot.rest.create_guild_text_channel(ctx.guild_id, f"Destruction {i}"),
        categories = await combot.rest.create_guild_category(ctx.guild_id, f"Destructioner {i}"),
        voiceChannel = await combot.rest.create_guild_voice_channel(ctx.guild_id, f"Destruction Voicer {i}"),
        # await combot.rest.create_role(ctx.guild_id, f"ROLE_MANAGER_{i}"),
        msgs = await combot.rest.create_message(textChannel[0],  f"""MENSAJE CIFRADO DE DESTRUCCION NUMERO {i}.
        CODIGO DE DESTRUCCION: {choice(hashed_msgs)}""")
    await ctx.respond("Comando creado correctamente")


#* //////////////////////////////
#*          PRUEBAS
#* //////////////////////////////


@admin.command
@lightbulb.option("message", "Mandar el objecto con un mensaje", required= False)
@lightbulb.option("video", "video a subir", type= hikari.Attachment, required= False)
@lightbulb.option("url", "URL del video/archivo", type= hikari.files.URL, required= False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD, hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.command("video", "Mandar un video para que los demas usuarios lo puedan descargar")
@lightbulb.implements(lightbulb.SlashCommand)
async def obtain(ctx: lightbulb.Context):

    embed = hikari.Embed(
        title= "📽️ Se ha subido un video!",
        description= f"``{ctx.member if ctx.member else ctx.author}`` ha subido un video! Si quieres verlo, copia la direccion del mensaje y coloca ``<<obtain``",
        color= SUCCESS_EMBED
    )

    await ctx.respond(embed= embed)


def load(combot):
    combot.add_plugin(admin)
def unload(combot):
    combot.remove_plugin(admin)

