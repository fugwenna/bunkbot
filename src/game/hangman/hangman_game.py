from typing import List
from discord import Message, TextChannel, PermissionOverwrite, CategoryChannel
from random_words import RandomWords

from .hangman_renderer2 import HangmanRenderer2
from ...core.bunk_exception import BunkException
from ...core.bunk_user import BunkUser


"""
Class that represents the actual game of hangman
"""
class HangmanGame:
    def __init__(self, creator: BunkUser):
        self.creator: BunkUser = creator
        self.renderer: HangmanRenderer2 = None
        self.random: RandomWords = RandomWords()
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
        self.is_completed = False
        self.is_random = False
        self.is_solo = False
        self.is_win = False
        self.name = None
        self.participants: List[BunkUser] = []


    # start a new or re-created game
    async def start(self, hangman_channel: CategoryChannel) -> None:
        if self.renderer is None:
            self.renderer = HangmanRenderer2(hangman_channel)
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
                is_added: bool = self.check_if_match(l_content)
                await self.renderer.update(self.phrase, self.guesses, self.matches, is_added=is_added)
            else:
                self.is_active = True
                self.is_random = l_content == "random"
                self.is_solo = l_content == "solo"

                if self.is_random or self.is_solo:
                    l_content = self.random.random_word().lower()

                self.phrase = [list(x) for x in l_content.split()]
                self.flat_phrase = [i for sl in self.phrase for i in sl]

                await self.renderer.update(self.phrase, self.guesses, self.matches, 
                    is_random=self.is_random, is_solo=self.is_solo)


    # when a phrase is offered, validate that
    # it only contains letters/numbers
    def check_if_match(self, guess: str) -> bool:
        added: bool = False

        if guess in self.guesses:
            # todo..
            pass
        else:
            count: int = self.flat_phrase.count(guess)
            if count > 0:
                self.matches = self.matches + ([guess]*count)
                added = True
            else:
                self.guesses.append(guess)

        self.is_win = len(self.matches) == len(self.flat_phrase)
        return added
