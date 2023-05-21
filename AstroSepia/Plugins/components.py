from ..combot import combot

import lightbulb
import hikari

import miru
from miru.ext import nav

# This contains all the class when we do import *
# Also, the private class methods (_method | __method) won't be loaded if u do import *

__all__ = [
    "MyNavButton",
    "Navegator"
]

c = lightbulb.Plugin("Components")

class YesButton(miru.Button):
    """Simple boton de afirmacion (Si)"""

    def __init__(self, cid: str, emoji: hikari.Emoji = None, row: int = None) -> None:
        super().__init__(style= hikari.ButtonStyle.SUCCESS, label= "Si", emoji= emoji, row= row, custom_id= cid)    #* Pasamos algunas propiedades indefinidas
    
    #* Si estoy subclaseando, debo llamar 'callback' a la repsuesta que da el boton cuando es presionado
    async def callback(self, ctx: miru.Context) -> None:
        await ctx.respond("Recibido SI", flags= hikari.MessageFlag.EPHEMERAL)

        self.view.answer = True
        #* Paramos de escuchar interacciones
        self.view.stop()


class NoButton(miru.Button):
    """Simple boton de negacion (No)"""

    def __init__(self, *args, **kwargs):    
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.Context) -> None:
        
        await ctx.respond("Recibido NO", flags= hikari.MessageFlag.EPHEMERAL)
        self.view.answer = False
        self.view.stop()


class LinkButton(miru.Button):
    """Siple boton para colocar links"""

    def __init__(self, link: hikari.URL, label: str = None, emoji: hikari.URL = None, row: int = None) -> None:
        super().__init__(style= hikari.ButtonStyle.LINK, url= link, label= label, emoji= emoji, row= row)
    
    async def callback(self, ctx: miru.Context) -> None:
        await ctx.respond("Esto es una prueba")
        self.view.answer = False


#* //////////////////////////////


class ModalView(miru.View):

    # Create a new button that will invoke our modal
    @miru.button(label="Shh clicka ...", style=hikari.ButtonStyle.PRIMARY)

    async def modal_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = MyModal("Dime un secreto")
        modal.add_item(miru.TextInput(label="De parte de:", placeholder="Escribe algo!", required=True))
        modal.add_item(miru.TextInput(label="Cuentame tus penurias", value=None, style=hikari.TextInputStyle.PARAGRAPH))
        # You may also use Modal.send() if not working withhin a miru context. (e.g. slash commands)
        # Keep in mind that modals can only be sent in response to interactions.
        await ctx.respond_with_modal(modal)


class MyModal(miru.Modal):

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # ModalContext.values is a mapping of {TextInput: value}
        values = list(ctx.values.values())
        await ctx.respond(
            "He enviado tus penurias a el infierno para que se hagan realidad"
        )
    # You may also access the values the modal holds by using Modal.values


class MyNavButton(nav.NavButton):
    # This is how you can create your own navigator button
    # The extension also comes with the following nav buttons built-in:
    #
    # FirstButton - Goes to the first page
    # PrevButton - Goes to previous page
    # IndicatorButton - Indicates current page number
    # StopButton - Stops the navigator session and disables all buttons
    # NextButton - Goes to next page
    # LastButton - Goes to the last page

    async def callback(self, ctx: miru.Context) -> None:
        await ctx.respond("You clicked me!", flags=hikari.MessageFlag.EPHEMERAL)

    async def before_page_change(self) -> None:
        # This function is called before the new page is sent by
        # NavigatorView.send_page()
        self.label = f"Pagina: {self.view.current_page+1}"


class Persistence(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)  # Setting timeout to None

    @miru.button(label="Button 1", custom_id="my_unique_custom_id_1")
    async def button_one(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.respond("You pressed button 1.")

    @miru.button(label="Button 2", custom_id="my_unique_custom_id_2")
    async def button_two(self, button: miru.Button, ctx: miru.Context) -> None:
        await ctx.respond("You pressed button 2.")




@combot.listen()
async def startup_views(event: hikari.StartedEvent) -> None:
    # You must reinstantiate the view in the same state it was before shutdown (e.g. same custom_ids)
    view = Persistence()
    # Restart the listener for the view, you may optionally pass in a message_id to further improve
    # accuracy and allow for after-the-fact view message edits
    view.start_listener()


@combot.listen()
async def buttons(event: hikari.GuildMessageCreateEvent) -> None:

    # Do not process messages from bots or empty messages
    if event.is_bot or not event.content:
        return

    if event.content.startswith("<persistent"):
        view = Persistence()
        message = await event.message.respond(
            "This is a persistent component menu, and works after bot restarts!",
             components=view.build(),
        )

        view.start(message)


@combot.listen(hikari.GuildMessageCreateEvent)
async def modals(event: hikari.GuildMessageCreateEvent) -> None:

    # Do not process messages from bots or empty messages
    if event.is_bot or not event.content:
        return

    if event.content.startswith("<modal"):
        view = ModalView()
        message = await event.message.respond(
            "Prueba de build menu context!", components=view
        )
        view.start(message)

    elif event.content.startswith("<nav"):
        embed = hikari.Embed(title="I'm the second page!", description="Also an embed!")
        pages = ["I'm the first page!", embed, "I'm the last page!"]
        # Define our navigator and pass in our list of pages
        navigator = nav.NavigatorView(pages=pages)
        # You may also pass an interaction object to this function
        await navigator.send(event.channel_id)

    elif event.content.startswith("<custom"):
        embed = hikari.Embed(title="I'm the second page!", description="Also an embed!")
        pages = ["I'm a customized navigator!", embed, "I'm the last page!"]
        # Define our custom buttons for this navigator
        # All navigator buttons MUST subclass NavButton
        buttons = [nav.PrevButton(), nav.StopButton(), nav.NextButton(), MyNavButton(label="Page: 1", row=1)]
        # Pass our list of NavButton to the navigator
        navigator = nav.NavigatorView(pages=pages, buttons=buttons)

        await navigator.send(event.channel_id)

def load(combot):
    combot.add_plugin(c)
def unload(combot):
    combot.remove_plugin(c)
