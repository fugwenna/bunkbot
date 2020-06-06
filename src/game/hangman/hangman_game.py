import asyncio
from typing import List
from discord import Message, TextChannel, PermissionOverwrite, CategoryChannel
from random import randint
from random_words import RandomWords, RandomNicknames

from .hangman_constants import HANGMAN_TEMPLATE
from .hangman_renderer import HangmanRenderer
from ..custom_game import CustomGame
from ...core.bunk_exception import BunkException
from ...core.bunk_user import BunkUser


"""
Class that represents the actual game of hangman
"""
class HangmanGame(CustomGame):
    def __init__(self, creator: BunkUser, channel: TextChannel):
        super().__init__(channel, creator)
        self.random: RandomWords = RandomWords()
        self.nicks: RandomNicknames = RandomNicknames()
        self.renderer: HangmanRenderer = HangmanRenderer(channel)
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
    async def start(self) -> None:
        self.name = await self.renderer.create_game(self.creator)


    # update the state of the game based on the
    # content of the user input
    async def update(self, message: Message, user: BunkUser) -> None:
        if not await self.is_cancel(message, self.creator):
            l_content: str = message.content.lower()
            if self.is_active:
                status: int = await self.check_if_match(l_content)
                is_added: bool = status == 1

                if status != 2:
                    await self.renderer.update(self.phrase, self.guesses, self.matches, is_added=is_added, user=user)

                if self.is_win or self.is_loss:
                    self.is_complete = True
                    await self.renderer.complete_game(self.is_win)
            else:
                self.is_active = True
                is_random = l_content == "random"
                is_solo = l_content == "solo"
                is_custom = not is_random and not is_solo

                if is_random or is_solo:
                    l_content = self.get_random_word_or_name()
                elif is_custom:
                    self.game_type = "Custom word/phrase by {0}".format(user.name)

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
        self.is_loss = not self.is_win and ((len(flat_guess) > 1) or (len(self.guesses) == len(HANGMAN_TEMPLATE)-2))

        if self.is_win:
            status = 1

        return status


    def get_random_word_or_name(self) -> str:
        word: str = ""

        c_word: int = randint(0, 100)
        if c_word < 70:
            self.game_type = "Random Word"
            word = self.random.random_word()
        else:
            g: str = ""
            c_gender: int = randint(0, 100)
            if c_gender > 50:
                g = "f"
                self.game_type = "Random Name (female)"
            else:
                g = "m"
                self.game_type = "Random Name (male)"

            word = self.nicks.random_nick(letter=None, gender=g)

        return word.lower()
