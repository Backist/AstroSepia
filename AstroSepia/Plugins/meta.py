from ..Utils.helpers import RGB_REGEX
from ..Utils.consts import INFO_EMBED, ALERT_EMBED, STATS_EMBED, SUCCESS_EMBED, ATTENTION_EMBED
from ..Utils.utils import format_dtime, get_badges, get_file_lines, get_roles
from ..combot import combot, __version__, current_mode
from ..descriptions import  *

import math
import asyncio
import os
import hikari
import lightbulb
import datetime
import psutil
from pathlib import Path

meta = lightbulb.Plugin("Meta commands", description= META_DESCRIPTION, include_datastore= True)



@meta.command
@lightbulb.add_cooldown(30, 2, lightbulb.ChannelBucket)
@lightbulb.command("about", "Sobre AstroSepia y sus funciones", aliases= ["asinfo"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def about(ctx: lightbulb.Context) -> None:

    embed = (
        hikari.Embed(
            title= "Sobre AstroSepia",
            description= f"Hola ``{ctx.member.display_name if ctx.member.display_name else ctx.author}`` !\n\n{ABOUT_DESCRIPTION_I}",
            color= INFO_EMBED
            )        
        .add_field("Meta Commands", ABOUT_DESCRIPTION_MC, inline= True)
        .add_field("Music Commands", ABOUT_DESCRIPTION_MCC, inline= True)
        .add_field("Admin Commands", ABOUT_DESCRIPTION_AC, inline= True)
        .add_field("Game Commands", ABOUT_DESCRIPTION_GC)
        .add_field(
            "Todos estos comandos son accesibles mediante el prefijo ``<<`` y con la barra diagonal ``[/]`` en algunos casos.",
            "\nSi necesitas la informacion detallada de un determinado comando, solo coloca ``/help`` o ``<<help`` mas el comando del que deseas saber mas informacion. \n\nComo dato útil, se recomienda utilizar ``/help | <<help`` en comandos que contengan el símbolo ``*`` para entender su funcionamiento. \nAdemás algunos comandos pueden ser llamados de diferentes maneras, es decir, tienen alias. De nuevo esta acción es recomendable para entender el funcionamiento de todos los comandos de forma general."
        )
        .add_field(
            "IMPORTANTE",
            "Actuamente el bot se encuentra en desarrollo, esto quiere decir que el bot no posee todos los commandos que terminará teniendo el bot.\nPor favor, si encuentras algún fallo, haznoslo saber mediante un reporte a los administradores del servidor o poniéndote en contacto con ``SKEYLODA#5040``."
        )
        .set_thumbnail("https://i.pinimg.com/originals/43/be/fe/43befe71d26c08819cbfe2b9c90c48bd.png")
        .set_footer("A proyect of SKEYLODA#5040")
    )
    await ctx.respond(embed= embed)



@meta.command
@lightbulb.command("invite", "Invita a AstroSepia a otro servidor", aliases = ["invlink"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def invitation(ctx: lightbulb.Context) -> None:

    invitation_link = f"https://discord.com/api/oauth2/authorize?client_id=956651574422282290&permissions=1541355859063&scope=bot%20applications.commands"
    
    embed = hikari.Embed(
        description= f"Haz click **[aqui]({invitation_link})** para invitarme!\n\n📩 **[Invitar]({invitation_link})**",
        color= INFO_EMBED
    )
    await ctx.respond(embed)



@meta.command
@lightbulb.command("source", "Entra en lo mas profundo del corazon de AstroSepia.", aliases = ["botcode", "github"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def invitation(ctx: lightbulb.Context) -> None:

    github = os.environ["GITHUB_LINK"]

    embed = hikari.Embed(
        description= f"[AQUI]({github}) tienes el codigo!\n\n🔮 **[Github]({github})**",
        color= INFO_EMBED
    )
    await ctx.respond(embed)



@meta.command
@lightbulb.command("version", "Version de AstroSepia", aliases = ["v", "botversion"])
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def invitation(ctx: lightbulb.Context) -> None:

    embed = hikari.Embed(
        title= f"**🔋 AstroSepia's Status**",
        description= f"**Version de AstroSepia: ``{__version__}``**\n**Current Mode: ``{current_mode}``**\n**Owners: ``{combot.owner_ids}``**",
        color= INFO_EMBED,
        timestamp= datetime.datetime.now().astimezone()
    )
    await ctx.respond(embed)


@meta.command
@lightbulb.set_help("Es necesario que el archivo contenga texto y este guardado en tu disco local, de lo contrario, no funcionara o retornara error.")
@lightbulb.option("filedoc", "El archivo en el que contar las lines. DEBE SER UN ARCHIVO DE TEXTO", type= hikari.Attachment)
@lightbulb.command("getlines", "Cuenta las lineas de un archivo", aliases = ["filelines"])
@lightbulb.implements(lightbulb.SlashCommand)
async def reader(ctx: lightbulb.Context) -> None:

    file = await ctx.options.filedoc.read()
    embed = hikari.Embed(
        title= f"**File Reader**",
        description= f"**Nombre de archivo:** {ctx.options.filedoc.filename}\n**Lineas escritas:{ctx.options.filedoc.extension}** \n**Lineas en blanco:** {ctx.options.filedoc.media_type}\n{len([i for i in file])}",
        color= INFO_EMBED,
        timestamp= datetime.datetime.now().astimezone()
    )
    await ctx.respond(embed)



@meta.command
@lightbulb.command("hello", "Deja que el bot se presente!", aliases= ["saludo", "yepa" , "tuki"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def display_greeting(ctx: lightbulb.Context) -> None:

    assert ctx.channel_id is not None

    embed = hikari.Embed(
        title= f"**Hola, {ctx.member.display_name if ctx.member.display_name else ctx.author}, soy tu Frikibot de confianza!**",
        color= INFO_EMBED
    )

    row = ctx.bot.rest.build_action_row()
    (
        row
        .add_button(hikari.ButtonStyle.PRIMARY, "saluda")
        .set_label("Hola!")
        .set_emoji("👋")
        .add_to_container()
    )
    await ctx.respond(embed= embed, component= row, attachment= Path("Images\qvideo.mp4"))

    while True:
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, timeout= 60)
        except asyncio.TimeoutError:
            await ctx.edit_last_response(components= [])
        else:
            if event.interaction.custom_id == "saluda":
                await ctx.bot.rest.add_reaction(ctx.channel_id, ctx.event.message, emoji= "🥳")
                await ctx.edit_last_response(components= [])
            return
             


@meta.command
@lightbulb.add_cooldown(15, 2, lightbulb.ChannelBucket)
@lightbulb.command("ping", "Muestra la latencia del bot", aliases = ["latency", "dsp"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def display_latency(ctx: lightbulb.Context) -> None:

    embed = (
        hikari.Embed(
            title="🏓 PONG",
            description= f"Latencia interna: ``{combot.heartbeat_latency * 1000:.0f} ms``",
            color= STATS_EMBED
        )
    )
    await ctx.respond(embed=embed)



@meta.command
@lightbulb.add_cooldown(10, 3, lightbulb.UserBucket)
@lightbulb.option("text", "Escribe lo que quieres que el bot repita", type= str, required= True)
@lightbulb.option("strikethrough", "Quieres que aparezca tachado?", choices = ["Yes", "No"], required= False)
@lightbulb.option("hidden", "Quieres que aparezca como spoiler?", choices = ["Yes", "No"], required= False)
@lightbulb.command("say", "El bot te repite!")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def display_text(ctx: lightbulb.Context) -> None:

    if ctx.options.hidden == "Yes":
        await ctx.respond(f"|| {ctx.options.text} ||")
    elif ctx.options.strikethrough == "Yes":
        await ctx.respond(f"~~{ctx.options.text}~~")
    else:
        await ctx.respond(ctx.options.text)



@meta.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.command("Raw content", "Muestra el contenido de un mensaje sin procesar", pass_options = True)
@lightbulb.implements(lightbulb.MessageCommand)
async def raw_content(ctx: lightbulb.MessageContext, target: hikari.Message) -> None:

    if target.content:
        await ctx.respond(f"```{target.content}```")

    else:
        embed = (
            hikari.Embed(
                title= "Ops!",
                description= "Parece que el mensaje esta vacio :dash:",
                color = ATTENTION_EMBED
            )
        )
        await ctx.respond(embed)



@meta.command
@lightbulb.add_cooldown(10, 5, lightbulb.ChannelBucket)
@lightbulb.command("get", "Grupo de comandos para obtener informacion general")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def get(ctx: lightbulb.Context) -> None:
    pass

@get.child
@lightbulb.option("user", "El usuario del que quieres saber informacion", required= True, type = hikari.User)
@lightbulb.command("ui", "Muestra toda la informacion sobre un usuario")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_user_info(ctx: lightbulb.Context) -> None:

    member = ctx.bot.cache.get_member(ctx.guild_id, ctx.options.user)
    top_role = get_roles(member, top_role=True, guild_id= ctx.guild_id)
    roles = get_roles(member, guild= ctx.guild_id)

    if member.get_presence().visible_status == 'idle':
        presence = "🟠 Ausente"
    elif member.get_presence().visible_status == 'dnd':
        presence = "🔴 No molestar"
    else:	
        presence = "🟢 Online"

    embed = (
        hikari.Embed(
            title= f"👤 Informacion del usuario  |  {member.display_name if member.display_name else member.username}",
            color= "#8f34eb"
        )

        .add_field("• Nombre:", f"``{member}``", inline= True)
        .add_field("• Nickname:", f"``{member.nickname or '❔'}``", inline= True)
        .add_field("• ID:",  f"``{member.id}``", inline= True)
        .add_field("• Presencia:", f"``{presence}``", inline= True)
        .add_field("• Bot:", f"``{member.is_bot}``", inline= True)
        .add_field("• Insignias:", f"{'   '.join(get_badges(member)) or '❔'}", inline= True)
        .add_field("• Cuenta creada el:", f"{format_dtime(member.created_at, style= 'D')}", inline= True)
        .add_field("• Se unió al servidor:", f"{format_dtime(member.joined_at, style= 'R')}", inline= True)
        .add_field("• Rol mas alto:", f"{top_role}", inline= True)
        .add_field("• Roles:", f"{roles}")
        .add_field("• Aceptó las normas:", f"``{member.is_pending if member.is_pending else '❔'}``", inline= True)

        .set_thumbnail(member.avatar_url)
        .set_footer(text= f"Requested by {ctx.member.display_name}", icon= ctx.member.display_avatar_url)
    )
    await ctx.respond(embed= embed, flags= hikari.MessageFlag.EPHEMERAL)

@get.child
@lightbulb.option("user", "El usuario del que quieres saber informacion", required= True, type = hikari.User)
@lightbulb.command("ua", "Muestra el avatar de un usuario")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_user_info(ctx: lightbulb.Context) -> None:
    
    user = ctx.bot.cache.get_member(ctx.guild_id, ctx.options.user)

    embed = (
        hikari.Embed(
        title= f"Avatar de {user.display_name if user.display_name else user.nickname}",
        color= INFO_EMBED
        )
        .set_image(user.display_avatar_url)
    )

    await ctx.respond(embed)


@get.child
@lightbulb.command("si", "Muestra la informacion del servidor")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_server_info(ctx: lightbulb.Context) -> None:

    assert ctx.guild_id is not None
    guild = ctx.app.cache.get_available_guild(ctx.guild_id)
    memb = guild.get_members()
    owner = await guild.fetch_owner()
    channels = guild.get_channels().values()

    presences = ctx.bot.cache.get_presences_view_for_guild(ctx.guild_id)
    online = [m for m in presences.values() if m.visible_status == "online"]
    idle = [m for m in presences.values() if m.visible_status == "idle"]
    dnd = [m for m in presences.values() if m.visible_status == "dnd"]
    ls = []
    ls.extend(online)
    ls.extend(idle)
    ls.extend(dnd)
    offline_invisible = len(guild.get_members()) - len(ls)

    count_static = len([emoji for emoji in guild.get_emojis().values() if not emoji.is_animated])
    count_animated = len([emoji for emoji in guild.get_emojis().values() if emoji.is_animated])
    emoji_slots = int((
        (1 + (sqrt_5 := math.sqrt(5))) ** (n := guild.premium_tier + 2) - (1 - sqrt_5) ** n) / (2**n * sqrt_5) * 50 - (count_animated + count_static)
    )
    total_emoji = int((
            (1 + (sqrt_5 := math.sqrt(5))) ** (n := guild.premium_tier + 2) - (1 - sqrt_5) ** n) / (2**n * sqrt_5) * 50 * 2
    )

    everyone = guild.get_role(guild.id)
    everyone_perms = everyone.permissions.value

    hidden_voice = 0
    hidden_text = 0
    all_channels = 0

    for channel in channels:
        perms_value = everyone_perms
        if everyone in channel.permission_overwrites:
            overwrites = channel.permission_overwrites[everyone]
            allow, deny = overwrites.allow, overwrites.deny
            perms_value &= -deny.value
            perms_value |= allow.value
        perms = str(hikari.Permissions(perms_value)).split(" | ")
        all_channels += 1
        if (
            isinstance(channel, hikari.GuildVoiceChannel)
            and "VIEW_CHANNEL" not in perms
        ):
            hidden_text += 1
        elif (
            isinstance(channel, hikari.GuildVoiceChannel)
            and not perms_value & hikari.Permissions.CONNECT
        ):
            hidden_voice += 1

    embed = (

        hikari.Embed(

            title= f"Informacion sobre {guild.name}",
            description= f""" 
            **• ID:** ``{guild.id}``
            **• Creador:** ``{owner} ({owner.id})``
            **• Creado el:** {format_dtime(guild.created_at, style= 'D')}
            **• Nitro Boost level:** ``{guild.premium_tier or '❌'}``
            **• Nitro Boost count:** ``{guild.premium_subscription_count or '❌'}``
            **• Localidad preferida:** ``{guild.preferred_locale}``
            **• About:**\n```Communidad: {'✅' if 'COMMUNITY' in guild.features else '❌'}
Verificado: {'✅' if 'VERIFIED' in guild.features else '❌'}
Monetización: {'✅' if 'MONETIZATION_ENABLED' in guild.features else '❌'}
Partner: {'✅' if 'PARTNERED' in guild.features else '❌'}
Nitro: {'✅' if guild.premium_tier or guild.premium_subscription_count >= 1 else '❌'}```\n""",    
            color= "#8f34eb",
            timestamp= datetime.datetime.now().astimezone()
        )
        .add_field(name= "• Presences", value= f"""🟢: {len(online)}\n🟠: {len(idle)}\n🔴: {len(dnd)}\n⚫: {offline_invisible}""", inline= True)
        .add_field("• Emojis", f"**• Estaticos:** ``{count_static}``\n**• Animados:** ``{count_animated}``\n**• Free Solts:** {emoji_slots}\n**• Total:** ``{total_emoji}``", inline=True)
        .add_field(name= "• 💬 Canales", 
        value=  f"""**• Texto:** {len([tch for tch in channels if isinstance(tch, hikari.TextableGuildChannel)])}
        **• Voz:** {len([tch for tch in channels if isinstance(tch, hikari.GuildVoiceChannel)])}
        **• News:** {len([tch for tch in channels if isinstance(tch, hikari.GuildNewsChannel)])}\n**• Canales ocultos:** {hidden_text+hidden_voice}""")
        
        .add_field(name="• Rule Channel", value=f"<#{guild.rules_channel_id}>", inline= True)
        .add_field(name="• AFK Channel", value=f"<#{guild.afk_channel_id}> ({guild.afk_timeout} horas)", inline= True)
        
        .set_thumbnail(guild.icon_url)

    )
    
    await ctx.respond(embed=embed, flags= hikari.MessageFlag.EPHEMERAL)


@get.child
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR, hikari.Permissions.MANAGE_GUILD))
@lightbulb.command("psu", "Muestra la carga del bot")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def bot_proccess(ctx: lightbulb.Context):

    process = psutil.Process()
    t_memory = psutil.virtual_memory()
    freq = psutil.cpu_freq(percpu=False)

    embed= (
        hikari.Embed(
            title="🤖  AstroSepia Processes"
        )
        .add_field("📉 CPU", f"`{round(psutil.cpu_percent(interval=None))} %`", inline= True)
        .add_field("🚀 Memory", f"`{round(process.memory_info().vms / 1048576)} MB`", inline= True)
        .add_field("💻 Total Memory", f"``{round(t_memory.total / 1048576)} MB``", inline= True)  #1B == 1048576 MB
        .add_field("🟢 Servers", f"``{len(combot.shards.keys())}``", inline= True)
        .add_field("🔧 Threading", f"``{psutil.cpu_count(logical=True)} Cores``", inline= True)
        .add_field("📊 CPU Freq", f"``{round(freq.current)} Mhz``", inline= True)
        .add_field(f"Comandos activos:", f"```Slash: {len([f for f in combot.slash_commands.values()])}    |     Prefix: {len([f.name for f in combot.prefix_commands.values()])}```")
        .add_field(f"Permisos:", f"```{combot.intents}```", inline= True)
        .add_field("Plugins", f"```{len([f.name for f in combot.plugins.values()])}```", inline= True)
        .set_footer("El bot realiza procesos de una sola dirección.")
    )
    await ctx.respond(embed= embed)


@meta.command
@lightbulb.option("separate", "Envia en embebido separado de la llamada del comando.", type=bool, required=False)
@lightbulb.option("color","Color del embebido. Debe ser en formato [RRR GGG BBB].",type=hikari.Color,required=False)
@lightbulb.option("author_url", "URL a la que se redeccionara a los usuarios que cliquen en el author.", required=False)
@lightbulb.option("thumbnail_url","URL para ser usada como imagen de la miniatura del embebido.",required=False)
@lightbulb.option("footer", "Pie de página del embebido.", required=False)
@lightbulb.option("description", "Descripcion del embebido.", required=False)
@lightbulb.option("author_image_url","URL para usar como avatar del author. Debe ser una URL",required=False)
@lightbulb.option("author", "El autor del embedbido. Se dispondrá arriba del título", required=False)
@lightbulb.option("footer_image_url","URL para ser usada como imagen para el pie de pagina",required=False)
@lightbulb.option("image_url","Imagen principal via URL",required=False)
@lightbulb.option("main_image","Imagen principal via Local para el embebido",required=False)
@lightbulb.option("ext_image1","Imagen que acompaña al embebido",type= hikari.OptionType.ATTACHMENT, required=False)
@lightbulb.option("ext_image2","Segunda Imagen que acompaña al embebido",type= hikari.OptionType.ATTACHMENT,required=False)
@lightbulb.option("title", "El título del embebido. Opcion REQUERIDA.")
@lightbulb.add_cooldown(30.0, 2, lightbulb.ChannelBucket)
@lightbulb.command("embed", "Genera un embebido con los parametros dados")
@lightbulb.implements(lightbulb.SlashCommand)
async def embed(ctx: lightbulb.Context) -> None:

    url_options = [
        ctx.options.image_url,
        ctx.options.thumbnail_url,
        ctx.options.footer_image_url,
        ctx.options.author_image_url,
        ctx.options.author_url,
    ]

    valid_extensions = [".png", ".jpeg", ".jpg", ".gif", ".webp"]
    file_images = []
    try:
        if ctx.options.ext_image1:
            file_images.append(ctx.options.ext_image1)
        if ctx.options.ext_image2:
            file_images.append(ctx.options.ext_image2)
    except not ctx.options.ext_image1.extension or ctx.options.ext_image2.extension in valid_extensions:
        await ctx.respond(embed= hikari.Embed(title="Error", description="No se pudo cargar la imagen."))
        return

    for option in url_options:
        if option and not type(hikari.File.url):
            embed = hikari.Embed(
                title="❌ Invalid URL",
                description=f"Proporciona una URL válida",
                color=ctx.options.colors,
            )
            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
            return

    if ctx.options.color is not None and not RGB_REGEX.fullmatch(ctx.options.color):
        embed = hikari.Embed(
            title="❌ Color Invalido",
            description=f"Los colores deben ser con el formato `RRR GGG BBB`, tres grupos de letras de tres letras.",
            color=ctx.options.color,
        )
        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        return

    embed = (
        hikari.Embed(
            title=ctx.options.title,
            description=ctx.options.description,
            color=ctx.options.color or SUCCESS_EMBED,
        )
        .set_footer(ctx.options.footer, icon=ctx.options.footer_image_url)
        .set_image(ctx.options.image_url)
        .set_thumbnail(ctx.options.thumbnail_url)
        .set_author(
            name=ctx.options.author,
            url=ctx.options.author_url,
            icon=ctx.options.author_image_url,
        )
    )
    await ctx.app.rest.create_message(ctx.channel_id, embed=embed)
    if len(file_images) > 0:
        await ctx.app.rest.create_message(ctx.channel_id, attachments= [file for file in file_images])
    embed = hikari.Embed(title="✅ Embebido creado!")
    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)



def load(combot):
    combot.add_plugin(meta)
def unload(combot):
    combot.remove_plugin(meta)


