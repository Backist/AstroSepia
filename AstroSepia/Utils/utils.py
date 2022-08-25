from .helpers import *
from AstroSepia.combot import combot as bot
import mmap
import datetime
from time import strftime, sleep




def format_dtime(time: datetime.datetime, style: str = None) -> str:
    """Formatea la fecha segun el tipo:
    
        't' - Short time\n
        'T' - Long time\n
        'd' - Short date\n
        'D' - Long Date\n
        'f' - Short Datetime\n
        'F' - Long Datetime\n
        'R' - Relative\n
    """

    valid_styles = ["t", "T", "d", "D", "f", "F", "R"]

    if style:
        return f"<t:{int(time.timestamp())}:{style}>"

    return f"<t:{int(time.timestamp())}>"


def is_invite(string: str, *, fullmatch: bool = True) -> bool:
    """
    Retorna True si el objeto es una invitacion, sino False
    """

    if fullmatch and INVITE_REGEX.fullmatch(string):
        return True
    elif not fullmatch and INVITE_REGEX.match(string):
        return True

    return False


def is_url(string: str, *, fullmatch: bool = True) -> bool:
    """
    Retorna True si el objeto es una URL, sino False
    """

    if fullmatch and LINK_REGEX.fullmatch(string):
        return True
    elif not fullmatch and LINK_REGEX.match(string):
        return True

    return False


def get_badges(user: hikari.User) -> list[str]:
    """Retorna los emoji que tiene un usuario. Devuelve una lista"""
    return [emoji for flag, emoji in BADGE_EMOJI_MAPPING.items() if flag & user.flags]

def get_roles(user: hikari.Snowflake,guild_id: hikari.SnowflakeishOr[hikari.PartialGuild] ,top_role: bool = False):
    """Retorna una lista con los roles del usuario. Si se pasa como `true` el parametro `top_role`, solo enviará el rol mas alto del usuario.
    Recuerda que puedes mencionar los roles una vez contenidos en una lista.
    
    DEBES pasar el usuario con su ID sino dara error
    """
    
    #assert isinstance((user, guild), hikari.Snowflake)
    
    target = bot.cache.get_member(guild_id, user)
    roles = [rol.mention for rol in target.get_roles()]
    roles.remove(f"<&{guild_id}>")
    
    if top_role:
        return user.get_top_role().mention if roles else None  
    return ", ".join(roles) if roles else "`❌`"


def get_file_lines(file) -> int:
    """Devuelve el numero total de linas de un archivo."""

    mm = mmap.mmap(file.fileno(), 0)
    total_lines = 0

    while mm.readline(): 
        total_lines += 1

    return total_lines




