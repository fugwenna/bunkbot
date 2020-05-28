import asyncio
from typing import List
from discord import Message, TextChannel
from discord.ext.commands import Context

from .custom_game import CustomGame
from .game_service import GameService
from ..core.bunk_user import BunkUser


class CustomGameCog:
    def __init__(self, game_service: GameService):
        self.game_service: GameService = game_service
        self.games: List[CustomGame] = []


    async def start_new_game(self, ctx: Context, name: str, all_users: bool) -> None:
        await ctx.message.delete()
        user: BunkUser = self.game_service.users.get_by_id(ctx.message.author.id)
        channel: TextChannel = await self.game_service.create_game_channel(name, user, all_users)

        if channel is not None:
            game: CustomGame = self.create_new_game(channel, user)
            await self.start_game(game)


    def create_new_game(self, channel: TextChannel, user: BunkUser) -> CustomGame:
        return CustomGame(channel, user)


    async def start_game(self, game: CustomGame) -> None:
        self.games.append(game)
        await game.start()


    # update the message of a given game - check if the
    # context of the message is a hangman channel 
    async def get_answer(self, message: Message) -> None:
        if not message.author.bot:
            game = next((g for g in self.games if g.channel.id == message.channel.id), None)
            if game is not None:
                user: BunkUser = self.game_service.users.get_by_id(message.author.id)
                await message.delete()
                await game.update(message, user)
                if game.is_cancelled:
                    self.games.remove(game)
                elif game.is_complete:
                    self.games.remove(game)
                    await asyncio.sleep(15)
                    await game.channel.delete()
                    