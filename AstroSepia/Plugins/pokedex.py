import lightbulb
import hikari
import aiohttp
from lightbulb.ext import filament


pokex = lightbulb.Plugin("Pokedex", "La database de pokemon original")

@pokex.command()
@lightbulb.option("pokemon", "El nombre del pokemon del que quieres saber su informacion", str, required=True, modifier = lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.command("pokedex", "Accede a la DataBase de la pokedex", auto_defer = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
@filament.utils.pass_options
async def pokedex(ctx: lightbulb.Context, pokemon) -> None:
    # -- Algunos pokemon se llaman distintos en la API, reemplazo los nombres distintos por los de la API
    pokemon = {
        'meloetta': 'Meloetta - Aria Forme',
        'keldeo': 'Keldeo - Ordinary Form',
        'burmy': 'Burmy - Plant Cloak',
        'wormadam': 'Wormadam - Plant Cloak',
        'cherrim': 'Cherrim - Overcast Form',
        'giratina': 'Giratina - Altered Forme',
        'shaymin': 'Shaymin - Land Forme',
        'basculin': 'Basculin - Red-Striped Form',
        'deerling': 'Deerling - Spring Form',
        'tornadus': 'Tornadus - Incarnate Forme',
        'thundurus': 'Thundurus - Incarnate Forme',
        'landorus': 'Landorus - Incarnate Forme',
        'flabebe': 'Flabébé',
        'zygarde': 'Zygarde - Complete Forme',
        'hoopa': 'Hoopa Confined',
        'oricorio': 'Oricorio - Baile Style',
        'lycanroc': 'Lycanroc - Midday Form',
        'wishiwashi': 'Wishiwashi - Solo Form',
        'minior': 'Minior - Meteor Form',
        'mimikyu': 'Mimikyu - Disguised Form',
    }.get(pokemon.lower())

    link = 'https://pokeapi.co/api/v2/pokemon/{pokemon}/'

    async with aiohttp.ClientSession() as session:
        async with session.get(link.format(pokemon = ctx.options.pokemon.lower())) as pokex_entry:
            if pokex_entry.status == 200:
                data = await pokex_entry.json()
            else:
                raise RuntimeError(f"Falló la conexion con el servidor externo. Codigo de error: {pokex_entry.status})")
        #-- Intentamos acceder y extraer info
        for x in data:
            try:
                poke_name = x['name']
                poke_no = x['number']
                poke_desc = x['description']
                poke_img = x['sprite']
                poke_height = x['height']
                poke_weight = x['weight']
                poke_species = x['species']
                poke_type1 = x['types'][0]
                poke_gen = str(x['gen'])
                poke_ability1 = x['abilities']['normal'][0]
                #--Vemos si tiene una segunda habilidad
                try:
                    poke_ability2 = x['abilities']['normal'][1]
                except IndexError:
                    poke_ability2 = None
                #--Habilidad escondida
                try:
                    poke_hiddenability = x['abilities']['hidden'][0]
                except IndexError:
                    poke_hiddenability = None
                #--Si tiene un segundo tipo
                    poke_type2 = x['types'][1]
                except IndexError:
                    poke_type2 = None

                embed = (

                    hikari.Embed(
                        title=f"Informacion de la pokedex sobre ``{poke_name}`` (#{poke_no})", 
                        description=poke_desc, 
                        color=0xd82626
                        )
                    .add_field(name='Alto', value=poke_height)
                    .add_field(name='Ancho', value=poke_weight)
                    .add_field(name='Especies', value=poke_species)
                )
                #--Detectamos si el pokemon tiene 2 tipos
                if poke_type2 is None:
                    embed.add_field(name='Tipo', value=poke_type1)
                else:
                    embed.add_field(name='Tipos', value=f"``{poke_type1}, {poke_type2}``")
                #--Detect if ability2 and hiddenability defined--#
                if poke_ability2 is None:
                    if poke_hiddenability is None:
                        embed.add_field(name='Habilidad', value=poke_ability1)
                    else:
                        embed.add_field(name='Habilidades', value=f"``{poke_ability1}``;\n**Hidden:** ``{poke_hiddenability}``")
                elif poke_hiddenability is None:
                    embed.add_field(name='Habilidad', value=f"``{poke_ability1}, {poke_ability2}``")
                else:
                    embed.add_field(name='Habilidades', value=f"``{poke_ability1}, {poke_ability2}``;\n**Hidden:** ``{poke_hiddenability}``")
                embed.add_field(name='Introducido en la generacion', value=f"Gen ``{poke_gen}``")
                embed.set_thumbnail(poke_img)
                await ctx.respond(embed=embed)
            except (KeyError, TypeError):
                raise ValueError(":x: No he encontrado ningun pokemon con ese nombre. Intentalo de nuevo y dame otra oportunidad")

def load(combot):
    combot.add_plugin(pokex)

def unload(combot):
    combot.remove_plugin(pokex)