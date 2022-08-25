from AstroSepia.Utils.consts import ATTENTION_EMBED, SUCCESS_EMBED, INFO_EMBED, ALERT_EMBED
from AstroSepia.logger import Logger
from AstroSepia.Utils.helpers import *

from typing import Optional
from asyncio import TimeoutError

import hikari
import lightbulb
import os
import lavasnek_rs


# Se utiliza el servidor Lavalink para buscar mediente una URL una cancion.
# Ver el application.yml para editar el puerto o la IP
# Puerto: 2333		IP: 127.0.0.1



# If True connect to voice with the hikari gateway instead of lavasnek_rs's
HIKARI_VOICE = False


class EventHandler:
	"""Events from the Lavalink server"""

	async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart) -> None | str:
		Logger("i", f"Pista iniciada en: {event.guild_id}")

	async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish) -> None | str:
		Logger("i", f"Pista finalizada en: {event.guild_id}")

	async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException) -> None | str:
		Logger("w", f"Track Exception in guild: {event.guild_id}")

		# If a track was unable to be played, skip it
		skip = await lavalink.skip(event.guild_id)
		node = await lavalink.get_guild_node(event.guild_id)

		if not node:
			return

		if skip and not node.queue and not node.now_playing:
			await lavalink.stop(event.guild_id)


music = lightbulb.Plugin("Music Commands", "Modulo de comandos para el uso de musica en el servidor", include_datastore= True)


async def _join(ctx: lightbulb.Context) -> Optional[hikari.Snowflake]:

	assert ctx.guild_id is not None

	states = music.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
	voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]

	if not voice_state:
		embed = hikari.Embed(
			title= "Espera . . .",
			description= "Tienes que conectarte a un canal de voz",
			color= ATTENTION_EMBED
		)
		await ctx.respond(embed)
		return None

	channel_id = voice_state[0].channel_id

	if HIKARI_VOICE:
		assert ctx.guild_id is not None

		await music.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
		connection_info = await music.bot.d.lavalink.wait_for_full_connection_info_insert(ctx.guild_id)

	else:
		try:
			connection_info = await music.bot.d.lavalink.join(ctx.guild_id, channel_id)
		except TimeoutError:

			embed = hikari.Embed(
				title= "Ops . . .",
				description= """El tiempo de espera para unirme se ha agotado o ha ocurrido un error.
				\nPosibles causas: ``Missing Perms: CONNECT | SPEAK``""",
				color= INFO_EMBED
			)
			await ctx.respond(embed)
			return None

	#* Creates a voice connection, who creates a node and inserts it, 
	#* node won't added to queue loops unless .queue() is ran
	await music.bot.d.lavalink.create_session(connection_info)

	return channel_id

async def is_running(guild_id: lightbulb.Context) -> bool:
	node = await music.bot.d.lavalink.get_guild_node(guild_id)
	connect = music.bot.d.lavalink.get_guild_gateway_connection_info(guild_id)
	return False if node or connect is None else True 



@music.listener(hikari.ShardReadyEvent)
async def start_lavalink(event: hikari.ShardReadyEvent) -> None:
	"""Event that triggers when the hikari gateway is ready."""

	builder = (
		# Optional TOKEN if want to use lavalink discord gateway
		lavasnek_rs.LavalinkBuilder(event.my_user.id, token= os.environ["TOKEN"])
		# This is the default value, so this is redundant, but it's here to show how to set a custom one.
		.set_host("127.0.0.1").set_password("AsMusicConnectionServerPass")
	)

	if HIKARI_VOICE:
		builder.set_start_gateway(False)

	lava_client = await builder.build(EventHandler())

	music.bot.d.lavalink = lava_client


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("join", "![Deprecated] El bot entra al canal de voz que estes. Usa /play o <<play en su lugar.", aliases = ["go", "getin"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: lightbulb.Context) -> None:
	"""AstroSepia entra en el canal de voz en el que estes"""
	channel_id = await _join(ctx)

	if channel_id:
		embed = hikari.Embed(
			title= f"✅ AstroSepia se ha unido a un canal de voz",
			description= f"**Unido al canal** <#{channel_id}>",
			color= SUCCESS_EMBED
		)
		await ctx.respond(embed)



@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("leave", "El bot sale del canal borrando la queue", aliases = ["exit", "getout"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def leave(ctx: lightbulb.Context) -> None:
	"""El bot sale del canal borrando la queue"""

	#Take sure that bot have creates a node, if not, return no lavalink session
	if not await is_running(ctx.guild_id):
		embed= hikari.Embed(
			title= "AstroSepia no esta en ningun canal",
			color= ALERT_EMBED
		)
		await ctx.respond(embed)

	else:
		await music.bot.d.lavalink.destroy(ctx.guild_id)

		if HIKARI_VOICE:
			if ctx.guild_id is not None:
				await music.bot.update_voice_state(ctx.guild_id, None)
				await music.bot.d.lavalink.wait_for_connection_info_remove(ctx.guild_id)
		else:
			await music.bot.d.lavalink.leave(ctx.guild_id)

		# Destroy nor leave remove the node nor the queue loop, you should do this manually.
		await music.bot.d.lavalink.remove_guild_node(ctx.guild_id)
		await music.bot.d.lavalink.remove_guild_from_loops(ctx.guild_id)

		embed = hikari.Embed(
			title= f"✅ AstroSepia ha salido del canal",
			color= SUCCESS_EMBED
		)
		await ctx.respond(embed)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("query", "La consulta a buscar", modifier=lightbulb.OptionModifier.CONSUME_REST)	
@lightbulb.command("play", "Busca la consulta en Youtube o añade la URL a la cola", aliases = ["repr"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def play(ctx: lightbulb.Context) -> None:
	"""Busca la consulta en Youtube o añade la URL a la cola"""

	if not ctx.options.query:
		embed = hikari.Embed(
			title= f"Se te olvida algo . . .",
			description= f"Pasa una URL o pasa una consulta",
			color= ALERT_EMBED
		)
		await ctx.respond(embed)
		return None

	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)
	# Join the user's voice channel if the bot is not in one. Check if node was crated w connection info and getting guild node
	if not await is_running(ctx.guild_id):
		await _join(ctx)


	# Search the query, auto_search will get the track from a url if possible, otherwise,
	# it will search the query on youtube.
	query_information = await music.bot.d.lavalink.auto_search_tracks(ctx.options.query)

	if not query_information.tracks:  # tracks is empty
		embed = hikari.Embed(
			title= f":dash: No he podido encontrar ningun resultado",
			color= ATTENTION_EMBED
		)
		await ctx.respond(embed)
		return 

	try:
		# `.requester()` To set who requested the track, so you can show it on now-playing or queue.
		# `.queue()` To add the track to the queue rather than starting to play the track now.
		await music.bot.d.lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(ctx.author.id).queue()

	except lavasnek_rs.NoSessionPresent as error:
		embed = hikari.Embed(
			title= f"Usa `/join |<<join` Primero para que AstroSepia se una al canal de voz",
			color= ATTENTION_EMBED
		)
		await ctx.respond(embed)
		raise error

	else:

		if node.now_playing:

			embed = hikari.Embed(
				title= f"✅ Reproduciendo la pista",
				description= f"Se esta reproduciendo ``{query_information.tracks[0].info.title}``",
				color= SUCCESS_EMBED
			)
			await ctx.respond(embed)

		else:
			embed = hikari.Embed(
				title= f"✅ Pista añadida a la cola",
				description= f"Añadida ``{query_information.tracks[0].info.title}`` a la lista",
				color= SUCCESS_EMBED
			)
			await ctx.respond(embed)
		
        
@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("stop", "Elimina y quita la pista actual, borrando la queue", aliases = ["quit"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop(ctx: lightbulb.Context) -> None:
	"""Para la pista de audio (skip para pasar la siguiente)"""


	# Take sure that session is running, if not session running, return not in channel (bc any session is started)
	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)
	
	if not node:
		embed= hikari.Embed(
			title= "AstroSepia no esta en ningun canal",
			color= ALERT_EMBED
		)
		await ctx.respond(embed)

	else:

		await music.bot.d.lavalink.stop(ctx.guild_id)
		node.queue = []
	
		if not stop:
			embed = hikari.Embed(
				title= ":dash: No hay ninguna pista para saltar",
				color= INFO_EMBED
			)

		embed = hikari.Embed(
			title= f"✅ La pista se ha parado correctamente y se ha eliminado la queue",
			color= SUCCESS_EMBED
		)
		await ctx.respond(embed)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("continue", "Continua la pista pausada")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop(ctx: lightbulb.Context) -> None:
	"""Continua con la pista de audio"""

	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)

	if node is not None:

		await music.bot.d.lavalink.resume(ctx.guild_id)
		embed = hikari.Embed(
			title= f"✅ Pista sonando!",
			color= SUCCESS_EMBED
		)
		await ctx.respond(embed)
	

	embed = hikari.Embed(
		title= ":dash: No esta sonando ninguna pista ahora"
	)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("skip", "Reproduce la siguiente pista de la cola", aliases = ["end", "turn-off"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def skip(ctx: lightbulb.Context) -> None:
	"""Reproduce la siguiente pista de la cola"""

	skip = await music.bot.d.lavalink.skip(ctx.guild_id)
	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)
	
	# Nothing to skip
	if not skip:
		embed = hikari.Embed(
			title= f"Ops . . .",
			description= "No hay ninguna pista activa en este momento :dash:",
			color= ATTENTION_EMBED
		)
		await ctx.respond(embed)
	else:
		# If the queue is empty, the next track won't start playing (because there isn't any),
		# so we stop the player.
		if not node.queue and not node.now_playing:
			await music.bot.d.lavalink.stop(ctx.guild_id)
			embed = hikari.Embed(
				title= ":dash: No hay ninguna pista en la cola para saltar",
				color= ALERT_EMBED
			)
			await ctx.respond(embed)
		else:
			embed = hikari.Embed(
				title= f"✅ Se ha pasado a la siguiente pista de la cola",
				description= f"Pista saltada: {skip.track.info.title}",
				color= SUCCESS_EMBED
			)
			await ctx.respond(embed)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pause", "Pausa la pista actual", aliases = ["freeze"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause(ctx: lightbulb.Context) -> None:
	"""Pausa la pista actual"""

	await music.bot.d.lavalink.pause(ctx.guild_id)
	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)

	if not node or not node.now_playing:
		embed = hikari.Embed(
			title= ":dash: No se esta reproduciendo musica en este momento o los servidores estan apagados."
		)

	embed = hikari.Embed(
		title= f"✅ Pista pausada",
		color= SUCCESS_EMBED
	)
	await ctx.respond(embed)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("nowplaying", "Informa sobre la cancion que esta sonando", aliases=["np", "getps"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def now_playing(ctx: lightbulb.Context) -> None:
	"""Informa sobre la cancion que esta sonando"""

	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)

	if not node or not node.now_playing:
		embed = hikari.Embed(
			title= f":dash: No se esta reproduciendo ninguna pista en este momento",
			color= ATTENTION_EMBED
		)
		await ctx.respond(embed)
		return

	# for queue, iterate over `node.queue`, where index 0 is now_playing.
	embed = (
		hikari.Embed(
		title="ℹ️ Informacion sobre la pista",
		description= f"**Sonando ahora mismo:** ``{node.now_playing.track.info.title}``",
		color= INFO_EMBED
		)
		.add_field("**Sobre la pista:**", value= f"""Duracion: ``{node.now_playing.track.info}``""")
	)
	await ctx.respond(embed)


@music.command()
@lightbulb.add_checks(lightbulb.guild_only, lightbulb.owner_only)
@lightbulb.option(
	"args", "The arguments to write to the node data.", required=False, modifier=lightbulb.OptionModifier.CONSUME_REST
)
@lightbulb.command("data", "Load or read data from the node.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def data(ctx: lightbulb.Context) -> None:
	"""Load or read data from the node.

	If just `data` is ran, it will show the current data, but if `data <key> <value>` is ran, it
	will insert that data to the node and display it."""

	node = await music.bot.d.lavalink.get_guild_node(ctx.guild_id)

	if not node:
		await ctx.respond("No node found.")
		return None

	if args := ctx.options.args:
		args = args.split(" ")

		if len(args) == 1:
			node.set_data({args[0]: args[0]})
		else:
			node.set_data({args[0]: args[1]})
	await ctx.respond(node.get_data())


if HIKARI_VOICE:

	@music.listener(hikari.VoiceStateUpdateEvent)
	async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
		music.bot.d.lavalink.raw_handle_event_voice_state_update(
			event.state.guild_id,
			event.state.user_id,
			event.state.session_id,
			event.state.channel_id,
		)

	@music.listener(hikari.VoiceServerUpdateEvent)
	async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
		await music.bot.d.lavalink.raw_handle_event_voice_server_update(event.guild_id, event.endpoint, event.token)






def load(bot: lightbulb.BotApp) -> None:
	bot.add_plugin(music)


def unload(bot: lightbulb.BotApp) -> None:
	bot.remove_plugin(music)