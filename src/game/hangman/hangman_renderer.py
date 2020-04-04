from typing import List
from discord import Message, TextChannel, PermissionOverwrite, CategoryChannel
from discord.ext.commands import Context
from random_word import RandomWords

from ...bunkbot import BunkBot
from ...core.bunk_user import BunkUser
from ...core.event_hook import EventHook


GALLOWS: str = """
+________+
|     |
|     {0}          Guesses:
|    {2}{1}{3}     \t   {7}
|    {4} {5}
|
=============

{6}
"""

# Simle class that will be the primary
# rendering agent for the game
class HangmanRenderer:
    def __init__(self, bot: BunkBot, user: BunkUser, channel: TextChannel, users: List[BunkUser], name: str):
        self.guesses: List[str] = []
        self.template: List[str] = ["o", "|", "/", "\\", "/", "\\", ""]
        self.user: BunkUser = user
        self.users: List[BunkUser] = []
        self.parent_channel: CategoryChannel = channel
        self.channel: TextChannel = None
        self.bot: BunkBot = bot
        self.name: str = name
        self.gallows: Message = None
        self.word: List[str] = None
        self.guess: List[str] = []
        self.message: Message = None
        self.is_cancelled = False
        self.is_completed = False
        self.is_random = False
        self.r = RandomWords()


    async def start_game(self) -> None:
        overwrites = {
            self.bot.server.default_role: PermissionOverwrite(read_messages=False),
            self.bot.server.get_member(self.user.id): PermissionOverwrite(read_messages=True),
            self.bot.server.get_role(437263429057773608): PermissionOverwrite(read_messages=True) # TODO - don't hard code
        }

        self.channel = await self.parent_channel.create_text_channel(self.name, overwrites=overwrites)
        m: str = "{0} - You have started a new hangman game! Enter your word, or type `cancel` to cancel the game. For a random word and self-participation, type `random`"
        self.gallows = await self.channel.send(m.format(self.user.mention))


    # create the skeleton of the hangman with 
    # the target points where the bot will draw
    async def update(self, message: Message) -> None:
        guess: str = message.content.lower()

        if message.author.id == self.user.id and guess.lower() == "cancel":
            self.is_cancelled = True
            await self.channel.delete()
        elif not self.word:
            if guess.lower() == "random":
                self.is_random = True
                guess = self.r.get_random_word(hasDictionaryDef=True,includePartOfSpeech="noun,verb",minCorpusCount=1,maxCorpusCount=10,minDictionaryCount=1,maxDictionaryCount=10,maxLength=10).lower()

            self.word = list(guess)
            blanks: str = ""

            for _ in range(0, len(self.word)):
                self.guess.append("-")
                blanks += "_ "

            empty_gallows: str = GALLOWS.format("","","","","","",blanks,"")
            await self.gallows.edit(content="```{0}```".format(empty_gallows))
            self.message = await self.channel.send("Hangman game started! Waiting for guess.")
            await message.delete()

            overwrites = {
                self.bot.server.default_role: PermissionOverwrite(send_messages=True, read_messages=True),
                self.bot.server.get_role(437263429057773608): PermissionOverwrite(read_messages=True) # TODO - don't hard code
            }
            await self.channel.edit(overwrites=overwrites)
        else:
            await self.analyze_guess(message)


    # analyze individual guesses - if the guess is longer
    # than a length of one, assume an attempt at guessing the word
    async def analyze_guess(self, message: Message) -> None:
        guess: str = message.content.lower()
        await message.delete()

        if self.is_random or message.author.id != self.user.id:
            if len(guess) > 1:
                await self.check_if_lost(guess)
                await self.check_if_won(next((u for u in self.users in u.id == message.author.id), None), guess)
            else:
                await self.check_guess(message)


    async def check_guess(self, message: Message) -> None:
        guess = message.content.lower()

        try:
            self.guesses.index(guess)
            await self.message.edit(content="`{0}` has already been used! Waiting for guess.".format(guess))
        except Exception:
            try:
                self.guess.index(guess)
                await self.message.edit(content="`{0}` has already been used! Waiting for guess.".format(guess))
            except Exception:
                await self.check_word(message)


    async def check_word(self, message: Message) -> None:
        found: bool = False
        guess = message.content.lower()
        word_value: str = ""

        for i in range(0, len(self.word)):
            if self.word[i] == self.guess[i]:
                word_value += "{0} ".format(self.guess[i])
            else:
                char = "_ "
                if self.word[i] == guess:
                    found = True
                    self.guess[i] = guess
                    char = "{0} ".format(guess)
        
                word_value += char

        if found:
            await self.message.edit(content="Correct, {0}! (guess: {1})".format(message.author.mention, guess))
        else:
            await self.message.edit(content="Incorrect, {0}! (guess: {1})".format(message.author.name, guess))
            self.guesses.append(guess)

        await self.check_if_lost()
        word_value = await self.check_if_won(next((u for u in self.users if u.id == message.author.id), None))
        await self.update_hangman_render(word_value)

    # update the actual render - code is ugly but oh well
    async def update_hangman_render(self, val: str) -> None:
        hm: List[str] = []
        gi: int = len(self.guesses)

        for i in range(0, len(self.template) - 1):
            if gi > i:
                if (gi == 2):
                    if i == 1:
                        hm.append(" {0}".format(self.template[i]))
                    else:
                        hm.append(self.template[i])
                else:
                    hm.append(self.template[i])
            else:
                hm.append("")

        hm.append(val)
        hm.append(", ".join(self.guesses))

        gallows: str = GALLOWS.format(*hm)
        await self.gallows.edit(content="```{0}```".format(gallows))


    async def check_if_lost(self, full_guess: str = None) -> None:
        guessed: bool = False

        if full_guess is not None:
            if full_guess.lower() != "".join(self.word):
                guessed = True

        if guessed or (len(self.guesses) == len(self.template) - 1):
            content: str = ":skull_crossbones: Hangman!! :skull_crossbones:"

            if guessed:
                content = ":skull_crossbones: Hangman!! (guessed: {0}) :skull_crossbones:".format(full_guess)

            await self.message.edit(content=content)
            await self.channel.send("The word was: `{0}`".format("".join(self.word)))
            await self.channel.send("This game will close in 15 seconds")

            overwrites = {
                self.bot.server.default_role: PermissionOverwrite(send_messages=False, read_messages=True),
                self.bot.server.get_role(437263429057773608): PermissionOverwrite(read_messages=True) # TODO - don't hard code
            }

            await self.channel.edit(overwrites=overwrites)
            self.is_completed = True


    async def check_if_won(self, user: BunkUser, full_guess: str = None) -> str:
        word = "".join(self.word)

        if full_guess is None:
            full_guess = "".join(self.guess)

        if word == full_guess:
            woo: str = "WOOOOOOOOOOOOOOOOOOOOOOOOOOO!!!"

            if user is not None:
                woo = "{0} WOOOOOOOOOOOOOOOOOOOOOOOOOOO!!!".format(user.mention)

            await self.message.edit(content=woo)
            await self.channel.send("This game will close in 15 seconds")

            overwrites = {
                self.bot.server.default_role: PermissionOverwrite(send_messages=False, read_messages=True),
                self.bot.server.get_role(437263429057773608): PermissionOverwrite(read_messages=True) # TODO - don't hard code
            }
            await self.channel.edit(overwrites=overwrites)
            self.is_completed = True

        return full_guess


    async def complete_game(self) -> None:
        await self.channel.delete()