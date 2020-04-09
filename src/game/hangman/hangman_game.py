import asyncio
from typing import List
from discord import Message, TextChannel, PermissionOverwrite, CategoryChannel
from random_words import RandomWords

from .hangman_renderer import HangmanRenderer
from ...core.bunk_exception import BunkException
from ...core.bunk_user import BunkUser


"""
Class that represents the actual game of hangman
"""
class HangmanGame:
    def __init__(self, creator: BunkUser):
        self.creator: BunkUser = creator
        self.renderer: HangmanRenderer = None
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
        self.is_random = False
        self.is_solo = False
        self.is_win = False
        self.is_loss = False
        self.name = None
        self.participants: List[BunkUser] = []


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
                    await self.renderer.update(self.phrase, self.guesses, self.matches, is_added=is_added)

                if self.is_win:
                    await self.restart_game(True)
                elif self.is_loss:
                    await self.restart_game(False)
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
    async def check_if_match(self, guess: str) -> int:
        status: bool = 0

        if guess in self.guesses or guess in self.matches:
            await self.renderer.show_already_guessed_prompt(guess)
            status = 2
        else:
            count: int = self.flat_phrase.count(guess)
            if count > 0:
                self.matches = self.matches + ([guess]*count)
                status = 1
            else:
                self.guesses.append(guess)

            self.is_win = len(self.matches) == len(self.flat_phrase)
            self.is_loss = not self.is_win and len(self.guesses) == len(self.renderer.hangman_template)

        return status


    # after a win, restart the game after 
    # 10 seconds of waiting
    async def restart_game(self, win: bool) -> None:
        await self.renderer.complete_game(win)
        await asyncio.sleep(10)
        await self.start(self.renderer.hangman_channel)
