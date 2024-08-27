import asyncio
import os
import discord
import Token
from enum import Enum
from discord.ext import commands
import logging
discord.utils.setup_logging()
logging.basicConfig(filename = "main.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")


class Bot(commands.Bot):
    async def setup_hook(self):
        print(f"Logged in as: {self.user}")
        logging.info(f"Logged in as: {self.user}")
        # Load extensions here
        await load()
bot = Bot(command_prefix="pyd ", intents= discord.Intents.all(), activity=discord.Activity(type=discord.ActivityType.listening, name="your commands"))

async def load():
    """Loads the module"""
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") :
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def reloading(ctx : commands.Context, *, module : str):
    """Reloads a module"""
    logging.info(f"trying to reload {module}")
    if (module + ".py" not in os.listdir("cogs")) and module != " all " :
        dirs = os.listdir('cogs')
        await ctx.send(f"This module doesn't exist, here is the list of modules : {dirs}") 
    try:
        if module == "all" :
            for file in os.listdir("cogs") :
                await bot.unload_extension("cogs." +file)
                await bot.load_extension("cogs."+ file)
        else :
            # await bot.reload_extension(module)
            await bot.unload_extension("cogs." +module)
            await bot.load_extension("cogs."+ module)
    except Exception as e:
        await ctx.send('\N{PISTOL}')
        await ctx.send('{}: {}'.format(type(e).__name__, e))
    else:
        await ctx.send(f'\N{OK HAND SIGN} {module}')

@bot.command(name="ping")
async def ping(ctx : commands.Context) -> discord.Message :
    "Sends the bot delay"
    return await ctx.send(f"🏓 Pong ! with {round(bot.latency, 3)*1000} ms !")

if __name__ == "__main__":
    bot.run(Token.Token)