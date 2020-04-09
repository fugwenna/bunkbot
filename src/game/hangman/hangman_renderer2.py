import asyncio
import time
from typing import List
from discord import Guild, Message, TextChannel, CategoryChannel, PermissionOverwrite, Embed

from ...core.bunk_user import BunkUser


GALLOWS: str = """
+________+
|     |
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
class HangmanRenderer2:
    def __init__(self, channel: TextChannel):
        self.hangman_template: List[str] = ["o", "|", "/", "\\", "/", "\\", ""]
        self.hangman_render: List[str] = []
        self.hangman_channel: CategoryChannel = channel
        self.channel: TextChannel = channel
        self.server: Guild = None
        self.creator: BunkUser = None
        self.rendered_gallows: Message = None
        self.prompt: Message = None


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
            self.channel = await self.hangman_channel.create_text_channel(name, overwrites=overrides)

        self.rendered_gallows = await self.channel.send(m.format(creator.mention))

        return name


    # "complete" a game and do not let anyone
    # enter any new values
    async def complete_game(self, is_win: bool) -> None:
        if is_win:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_complete=is_win))
            await self.prompt.edit(content="{0} WOOOOOOOOOOOOOOOOOOOOOOOOOOO".format(self.creator.mention), embed=None)
        else:
            await self.prompt.edit(content=":skull_crossbones: Hangman!! :skull_crossbones:", embed=None)

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
        vals: dict = {}

        if kwargs.get("is_new", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=False)
            vals[self.server.get_member(self.creator.id)] = PermissionOverwrite(read_messages=True, send_messages=True)
        elif kwargs.get("is_pause", False):
            vals[self.server.default_role] = PermissionOverwrite(send_messages=False)
            vals[self.server.get_member(self.creator.id)] = PermissionOverwrite(send_messages=False)
        elif kwargs.get("is_resume", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=True, send_messages=True)
            vals[self.server.get_member(self.creator.id)] = PermissionOverwrite(read_messages=True, send_messages=True)
        elif kwargs.get("is_win", False):
            vals[self.server.default_role] = PermissionOverwrite(read_messages=True, send_messages=False)

        bot_role_id: int = 437263429057773608 # TODO - config
        vals[self.server.get_role(bot_role_id)] = PermissionOverwrite(read_messages=True, send_messages=True)

        return vals


    # render the contents of the given 
    # phrase, guesses, and matches and update
    # the template accordingly
    async def update(self, phrase: List[List[str]], guesses: List[str], matches: List[str], **kwargs) -> None:
        template: str = ""
        is_new: bool = kwargs.get("is_random") or kwargs.get("is_solo")
        is_added: bool = kwargs.get("is_added")

        if not is_new:
            await self.reset_prompt(is_added, guesses)

        for i in range(0, len(phrase)):
            for j in range(0, len(phrase[i])):
                p_letter: str = phrase[i][j]
                template += "{0} ".format(p_letter if p_letter in matches else "_")

            if i != len(phrase):
                template += " "

        render: List[str] = self.get_updated_render()
        gallows: str = GALLOWS.format(*render+[template])

        if not is_new:
            if not is_added:
                self.hangman_render.append(self.hangman_template[len(self.hangman_render)])
                render = self.get_updated_render()
            gallows = GALLOWS.format(*render+[template])
        else:
            print(phrase)

        if len(guesses) > 0 or is_added:
            embed: Embed = self.create_embed_prompt_from_response(is_added, guesses)
            await self.pause_prompt(embed)
        elif is_new:
            await self.channel.edit(overwrites=self.get_channel_overrides(is_resume=True))
            self.prompt = await self.channel.send("Waiting for guess")

        await self.rendered_gallows.edit(content="```{0}```".format(gallows))


    # "pause" the prompt when a user guesses after
    # updating so they can see the result
    async def pause_prompt(self, embed: Embed) -> None:
        await self.prompt.edit(embed=embed, content=None)
        await self.channel.edit(overwrites=self.get_channel_overrides(is_pause=True))


    # reset the color of the prompt to nothing so
    # there is a slight update when a guess is made
    async def reset_prompt(self, is_added: bool, guesses: List[str]) -> None:
        embed = self.create_embed_prompt_from_response(is_added, guesses, True)
        await self.prompt.edit(embed=embed, content=None)
        await self.channel.edit(overwrites=self.get_channel_overrides(is_resume=True))


    # called directly from the game if a user has already
    # guessed a letter, show them this prompt
    async def show_already_guessed_prompt(self, guess: str) -> None:
        embed: Embed = Embed(title="Already Guessed!", description="{0} has already been used".format(guess), color=int("F45900", 16))
        await self.prompt.edit(embed=embed)


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


    def create_embed_prompt_from_response(self, is_added: bool, guesses: List[str], blank: bool = False) -> Embed:
        color_val: str = "00E63E" if is_added else "CC181E"
        title_val: str = "Correct!" if is_added else "Incorrect!"

        if blank:
            embed: Embed = Embed(title=title_val)
        else:
            embed: Embed = Embed(title=title_val, color=int(color_val, 16))#, description="fartslol\nbrolol")

        #embed.add_field(name="User", value="huh", inline=True)

        if len(guesses) > 0:
            embed.add_field(name="Last Wrong Guess", value=guesses[len(guesses)-1], inline=True)
            embed.add_field(name="Total Guesses", value=",".join(guesses), inline=True)

        return embed
