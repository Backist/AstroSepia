import AstroSepia.Utils.consts as consts

import re
import hikari


#! Regular expressions

MESSAGE_LINK_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)channels[\/][0-9]{1,}[\/][0-9]{1,}[\/][0-9]{1,}"
)

LINK_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)"
)

INVITE_REGEX = re.compile(r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?")

RGB_REGEX = re.compile(r"[0-9]{1,3} [0-9]{1,3} [0-9]{1,3}")

#! EMOJI MAPPING

BADGE_EMOJI_MAPPING = {
    hikari.UserFlag.BUG_HUNTER_LEVEL_1: consts.EMOJI_BUGHUNTER,
    hikari.UserFlag.BUG_HUNTER_LEVEL_2: consts.EMOJI_BUGHUNTER_GOLD,
    hikari.UserFlag.DISCORD_CERTIFIED_MODERATOR: consts.EMOJI_CERT_MOD,
    hikari.UserFlag.EARLY_SUPPORTER: consts.EMOJI_EARLY_SUPPORTER,
    hikari.UserFlag.EARLY_VERIFIED_DEVELOPER: consts.EMOJI_VERIFIED_DEVELOPER,
    hikari.UserFlag.HYPESQUAD_EVENTS: consts.EMOJI_HYPESQUAD_EVENTS,
    hikari.UserFlag.HYPESQUAD_BALANCE: consts.EMOJI_HYPESQUAD_BALANCE,
    hikari.UserFlag.HYPESQUAD_BRAVERY: consts.EMOJI_HYPESQUAD_BRAVERY,
    hikari.UserFlag.HYPESQUAD_BRILLIANCE: consts.EMOJI_HYPESQUAD_BRILLIANCE,
    hikari.UserFlag.PARTNERED_SERVER_OWNER: consts.EMOJI_PARTNER,
    hikari.UserFlag.DISCORD_EMPLOYEE: consts.EMOJI_STAFF,
}

emojis = {
    "Number1": "1️⃣",
    "Number2": "2️⃣",
    "Number3": "3️⃣",
    "Number4": "4️⃣",
    "Red": "🔴",
    "Blue": "🔵",
    "Green": "🟢",
    "Gray": "⚪"
}







