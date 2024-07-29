import asyncio
import os
import discord
import Token
from enum import Enum
from discord.ext import commands
discord.utils.setup_logging()

class Bot(commands.Bot):
    async def setup_hook(self):
        print(f"Logged in as: {self.user}")
        # Load extensions here
        await load()
bot = Bot(command_prefix="pyd ", intents= discord.Intents.all(), activity=discord.Activity(type=discord.ActivityType.listening, name="to your commands"))

async def load():
    for filename in os.listdir(r"D:\Perso\Programmation\Discord_Bot\PyfDownloadTool\cogs"):
        if filename.endswith(".py") :
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def reloading(ctx : commands.Context, *, module : str):
    """Reloads a module"""
    print(f"trying to reload {module}")
    if (module + ".py" not in os.listdir(r"D:\Perso\Programmation\Discord_Bot\PyfDownloadTool\cogs")) and module != " all " :
        await ctx.send(f"This module doesn't exist, here is the list of modules : {os.listdir(r"D:\Perso\Programmation\Discord_Bot\PyfDownloadTool\cogs")}")
    try:
        if module == "all" :
            for file in os.listdir(r"D:\Perso\Programmation\Discord_Bot\PyfDownloadTool\cogs") :
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