import asyncio
from typing import List
from discord import Message, TextChannel, PermissionOverwrite, CategoryChannel
from random_words import RandomWords, RandomNicknames

from .hangman_renderer import HangmanRenderer
from ...core.bunk_exception import BunkException
from ...core.bunk_user import BunkUser
from ...core.functions import roll_int


"""
Class that represents the actual game of hangman
"""
class HangmanGame:
    def __init__(self, creator: BunkUser):
        self.creator: BunkUser = creator
        self.renderer: HangmanRenderer = None
        self.random: RandomWords = RandomWords()
        self.nicks: RandomNicknames = RandomNicknames()
        self.set_defaults()


    # set the defaults for a new game, consisting
    # of the gallows, phrase/template, guesses and matches
    def set_defaults(self) -> None:
        self.phrase: List[List[str]] = []
        self.flat_phrase: List[str] = []
        self.guesses: List[str] = []
        self.matches: List[str] = []
        self.is_active = False
        self.is_cancelled = False
        self.is_win = False
        self.is_loss = False
        self.name = None
        self.participants: List[BunkUser] = []
        self.game_type: str = "Random word"


    # start a new or re-created game
    async def start(self, hangman_channel: CategoryChannel) -> None:
        if self.renderer is None:
            self.renderer = HangmanRenderer(hangman_channel)
            self.name = await self.renderer.create_new_game(hangman_channel, self.creator)
        else:
            await self.renderer.restart_game()
            self.set_defaults()


    # update the state of the game based on the
    # content of the user input
    async def update(self, message: Message) -> None:
        await message.delete()
        l_content: str = message.content.lower()
        
        if l_content == "cancel":
            self.is_cancelled = True
            await self.renderer.cancel_game()
        else:
            if self.is_active:
                status: int = await self.check_if_match(l_content)
                is_added: bool = status == 1

                if status != 2:
                    await self.renderer.update(self.phrase, self.guesses, self.matches, is_added=is_added, username=message.author.name)

                if self.is_win:
                    await self.restart_game(True)
                elif self.is_loss:
                    await self.restart_game(False)
            else:
                self.is_active = True
                is_random = l_content == "random"
                is_solo = l_content == "solo"
                is_custom = not is_random and not is_solo

                if is_random or is_solo:
                    l_content = self.get_random_word_or_name()
                    if is_solo:
                        l_content += " (solo game)"
                elif is_custom:
                    self.game_type = "Custom word/phrase by {0}".format(message.author.name)

                self.phrase = [list(x) for x in l_content.split()]
                self.flat_phrase = [i for sl in self.phrase for i in sl]

                await self.renderer.update(self.phrase, self.guesses, self.matches, 
                    is_random=is_random, is_solo=is_solo, is_custom=is_custom, g_type=self.game_type)


    # when a phrase is offered, validate that
    # it only contains letters/numbers
    async def check_if_match(self, guess_phrase: str) -> int:
        status: bool = 0
        l_guess: List[str] = guess_phrase.split()
        flat_guess = [i for sl in l_guess for i in sl]

        if len(flat_guess) > 1:
            self.guesses = l_guess
            self.matches = [l for l in list(flat_guess) if l in self.flat_phrase]
        else:
            guess = flat_guess[0]
            if guess in self.guesses or guess in self.matches:
                await self.renderer.show_already_guessed_prompt(guess)
                status = 2
            else:
                count: int = self.flat_phrase.count(guess)
                if count > 0:
                    if not guess in self.matches:
                        self.matches = self.matches + ([guess]*count)
                    status = 1
                else:
                    self.guesses.append(guess)

        self.is_win = len(self.matches) == len(self.flat_phrase)
        self.is_loss = not self.is_win and ((len(flat_guess) > 1) or (len(self.guesses) == len(self.renderer.hangman_template)-2))

        if self.is_win:
            status = 1

        return status


    # after a win, restart the game after 
    # 10 seconds of waiting
    async def restart_game(self, win: bool) -> None:
        await self.renderer.complete_game(win)
        await asyncio.sleep(10)
        await self.start(self.renderer.hangman_channel)


    def get_random_word_or_name(self) -> str:
        word: str = ""

        c_word: int = roll_int(0, 100)
        if c_word < 70:
            self.game_type = "Random Word"
            word = self.random.random_word()
        else:
            g: str = ""
            c_gender: int = roll_int(0, 100)
            if c_gender > 50:
                g = "f"
                self.game_type = "Random Name (female)"
            else:
                g = "m"
                self.game_type = "Random Name (male)"

            word = self.nicks.random_nick(letter=None, gender=g)

        return word.lower()
