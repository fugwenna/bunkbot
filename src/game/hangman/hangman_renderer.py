import asyncio
import time
from typing import List
from discord import Guild, Message, TextChannel, CategoryChannel, PermissionOverwrite, Embed

from ...core.bunk_user import BunkUser


GALLOWS: str = """
+________+
|     |              Guesses: {7}
|     {0}          
|    {2}{1}{3}
|    {4} {5}
|
=============

{6}
"""

"""
The primary rendering engine that will update
the hangman game based on guesses from users
"""
class HangmanRenderer:
    def __init__(self, channel: TextChannel):
        self.hangman_template: List[str] = ["o", "|", "/", "\\", "/", "\\", "", ""]
        self.hangman_render: List[str] = []
        self.hangman_channel: CategoryChannel = channel
        self.channel: TextChannel = channel
        self.server: Guild = None
        self.creator: BunkUser = None
        self.rendered_gallows: Message = None
        self.prompt: Message = None
        self.formatted_phrase: str = None


    # render a new game with empty gallows
    # and prompt the user for a word
    async def create_new_game(self, channel: CategoryChannel, creator: BunkUser) -> str:
        self.server = channel.guild
        self.creator = creator
        overrides: dict = self.get_channel_overrides(is_new=True)

        m: str = """
        {0} - You have started a new hangman game! Enter your word, or type `cancel` to cancel the game. For a random word and self-participation, type `random`. For a solo game type `solo`.
        """

        name: str = "hangman-{0}".format(creator.name)

        if self.rendered_gallows is None:
            self.channel = await self.hangman_channel.create_text_channel(name, overwrites=overrides, slowmode_delay=1)
        else:
            await self.channel.edit(overwrites=overrides, slowmode_delay=1)

        self.rendered_gallows = await self.channel.send(m.format(creator.mention))

        return name


    # "complete" a game and do not let anyone
    # enter any new values
    async def complete_game(self, is_win: bool) -> None:
        self.hangman_render = []

        if is_win:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_win=True))
            await self.prompt.edit(content="{0} WOOOOOOOOOOOOOOOOOOOOOOOOOOO".format(self.creator.mention), embed=None)
        else:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_win=False))
            await self.prompt.edit(content=":skull_crossbones: Hangman!! :skull_crossbones:", embed=None)
            await self.channel.send("The phrase was `{0}`!".format(self.formatted_phrase))

        await self.channel.send("This game will close in 10 seconds")


    # restart a new game and apply the proper
    # channel restrictions until the game is ready to be started
    async def restart_game(self) -> None:
        await self.channel.purge()
        await self.create_new_game(self.channel, self.creator)


    # if a user types "cancel" destroy
    # the channel from the server entirely
    async def cancel_game(self) -> None:
        await self.channel.delete()


    # when creating games, overrides will need to 
    # be placed on the channel so that players cannot
    # cheat and see the phrase
    def get_channel_overrides(self, **kwargs) -> dict:
        bot_role_id: int = 437263429057773608 # TODO - config
        vals: dict = {
            self.server.get_role(bot_role_id): PermissionOverwrite(read_messages=True, send_messages=True)
        }

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
        template: str = ""
        is_new: bool = kwargs.get("is_random") or kwargs.get("is_solo")
        is_custom: bool = kwargs.get("is_custom")
        is_added: bool = kwargs.get("is_added")
        full_phrase: str = ""

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
        gallows: str = GALLOWS.format(*render+[template, ""])

        if not is_new and not is_custom:
            if not is_added:
                self.hangman_render.append(self.hangman_template[len(self.hangman_render)])
                render = self.get_updated_render()
            gallows = GALLOWS.format(*render+[template, ", ".join(guesses)])
        
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
