import asyncio
import time
from typing import List
from discord import Guild, Message, TextChannel, CategoryChannel, PermissionOverwrite, Embed

from .hangman_constants import GALLOWS, HANGMAN_TEMPLATE
from ...core.bunk_user import BunkUser

"""
The primary rendering engine that will update
the hangman game based on guesses from users
"""
class HangmanRenderer:
    def __init__(self, channel: TextChannel):
        self.hangman_render: List[str] = []
        self.hangman_channel: CategoryChannel = channel
        self.channel: TextChannel = channel
        self.server: Guild = channel.guild
        self.creator: BunkUser = None
        self.rendered_gallows: Message = None
        self.prompt: Message = None
        self.formatted_phrase: str = None
        self.game_type: str = "Random Word"
        self.last_user: BunkUser = None


    # render a new game with empty gallows
    # and prompt the user for a word
    async def create_game(self, creator: BunkUser) -> str:
        self.creator = creator

        m: str = """
        {0} - You have started a new hangman game! Enter your word, or type `cancel` to cancel the game. For a random word and self-participation, type `random`. For a solo game type `solo`.
        """

        name: str = "hangman-{0}".format(creator.name)
        self.rendered_gallows = await self.channel.send(m.format(creator.mention))

        return name


    # "complete" a game and do not let anyone
    # enter any new values
    async def complete_game(self, is_win: bool) -> None:
        self.hangman_render = []

        if is_win:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_win=True))
            await self.prompt.edit(content="{0} WOOOOOOOOOOOOOOOOOOOOOOOOOOO".format(self.last_user.mention), embed=None)
        else:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_win=False))
            await self.prompt.edit(content=":skull_crossbones: Hangman!! :skull_crossbones:", embed=None)
            await self.channel.send("The phrase was `{0}`!".format(self.formatted_phrase))

        await self.channel.send("This game will close in 15 seconds")


    # if a user types "cancel" destroy
    # the channel from the server entirely
    async def cancel_game(self) -> None:
        await self.channel.delete()


    # when creating games, overrides will need to 
    # be placed on the channel so that players cannot
    # cheat and see the phrase
    def get_channel_overrides(self, **kwargs) -> dict:
        vals = self.channel.overwrites

        if kwargs.get("is_new", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=False, send_messages=False)
            vals[self.server.get_member(self.creator.id)] = PermissionOverwrite(read_messages=True, send_messages=True)
        elif kwargs.get("is_solo", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=True, send_messages=False)
            vals[self.server.get_member(self.creator.id)] = PermissionOverwrite(read_messages=True, send_messages=True)
        elif kwargs.get("is_random", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=True, send_messages=True)
        elif kwargs.get("is_win", False) or kwargs.get("is_loss"):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=True, send_messages=False)

        return vals


    # render the contents of the given 
    # phrase, guesses, and matches and update
    # the template accordingly
    async def update(self, phrase: List[List[str]], guesses: List[str], matches: List[str], **kwargs) -> None:
        if kwargs.get("g_type", None):
            self.game_type = kwargs.get("g_type")

        template: str = ""
        is_new: bool = kwargs.get("is_random") or kwargs.get("is_solo")
        is_custom: bool = kwargs.get("is_custom")
        is_added: bool = kwargs.get("is_added")
        user: BunkUser = kwargs.get("user", None)
        username: str = ""
        full_phrase: str = ""

        if user:
            self.last_user = user
            username = user.name

        if kwargs.get("is_solo"):
            await self.channel.edit(overwrites=self.get_channel_overrides(is_solo=True))
        elif kwargs.get("is_random") or is_custom:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_random=True))

        for i in range(0, len(phrase)):
            for j in range(0, len(phrase[i])):
                p_letter: str = phrase[i][j]
                template += "{0} ".format(p_letter if p_letter in matches else "_")
                full_phrase += p_letter

            if i != len(phrase):
                template += "  "
                full_phrase += "  "

        self.formatted_phrase = full_phrase.strip()

        render: List[str] = self.get_updated_render()
        gallows: str = GALLOWS.format(*render+[template, "", username, self.game_type])

        if not is_new and not is_custom:
            if not is_added:
                self.hangman_render.append(HANGMAN_TEMPLATE[len(self.hangman_render)])
                render = self.get_updated_render()
            gallows = GALLOWS.format(*render+[template, ", ".join(guesses), username, self.game_type])
        
        if is_new or is_custom:
            self.prompt = await self.channel.send("Waiting for guess")
        elif is_added:
            await self.prompt.edit(content=":white_check_mark: Correct!")
        else:
            await self.prompt.edit(content=":x: Incorrect!")

        await self.rendered_gallows.edit(content="```{0}```".format(gallows))


    # called directly from the game if a user has already
    # guessed a letter, show them this prompt
    async def show_already_guessed_prompt(self, guess: str) -> None:
        await self.prompt.edit(content=":warning: `{0}` has already been used".format(guess))


    # get an updated render based on the 
    # length of the current render
    def get_updated_render(self) -> List[str]:
        render = 6*[""]
        if len(self.hangman_render) > 0:
            render = self.hangman_render[:]+([""]*(6-len(self.hangman_render)))
            if len(self.hangman_render) == 2:
                render[1] = " {0}".format(render[1])
            else:
                render[1] = render[1].strip()

        return render
