import asyncio
import os
import discord
import Token
from enum import Enum
from discord.ext import commands

class Bot(commands.Bot):
    async def setup_hook(self):
        print(f"Logged in as: {self.user}")
        # Load extensions here
        await self.load_extensions()
bot = Bot(command_prefix="!", intents= discord.Intents.all(), status = "Running to help you")

async def load():
    for filename in os.listdir("D:\Perso\Programmation\Discord_Bot\MyTestBot\cogs"):
        if filename.endswith(".py") :
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def reloading(ctx : commands.Context, *, module : str):
    """Reloads a module"""
    print(f"trying to reload {module}")
    if module + ".py" not in os.listdir("D:\Perso\Programmation\Discord_Bot\MyTestBot\cogs"):
        await ctx.send(f"This module doesn't exist, here is the list of modules : {os.listdir("D:\Perso\Programmation\Discord_Bot\MyTestBot\cogs")}")
    try:
        # await bot.reload_extension(module)
        await bot.unload_extension("cogs." +module)
        await bot.load_extension("cogs."+ module)
    except Exception as e:
        await ctx.send('\N{PISTOL}')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send(f'\N{OK HAND SIGN} {module}')

if __name__ == "__main__":
    bot.run(Token.Token)