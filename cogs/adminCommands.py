import discord
from discord.ext import commands
import datetime
import asyncio
from typing import Literal, Optional
import nest_asyncio

nest_asyncio.apply()

class AdminCommands(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        return print("Admin Commands Cog loaded")
    
    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx : commands.Context):
        """Shutdowns the bot"""
        # await self.bot.change_presence(activity=discord.Game(name=Status.shutdown))
        await ctx.reply("Sudoku time o7", mention_author = False)
        return exit()
    
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        """https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html : link to the function"""
        print(f"Sync command called : !sync{spec}")
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild'} :/{" ; " .join([sync.name for sync in synced])} command"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    
    @commands.command()
    async def slowmode(self, ctx : commands.Context, seconds: int, channel : discord.TextChannel = None) :
        is_in_private_messages = ctx.guild is None and isinstance(ctx.author, discord.User)
        if is_in_private_messages:
            return await ctx.send('This command cannot be used in private messages')

        has_permission = ctx.author.guild_permissions.manage_channels
        if not has_permission:
            return await ctx.send('You do not have permission to use this command')

        is_time_invalid = seconds < 0 or seconds > 21600
        if is_time_invalid:
            return await ctx.send('Time must be between 0 and 21600 seconds')

        if channel is None:
            channel = ctx.channel

        if seconds==0:
            await channel.edit(slowmode_delay=0)
            return await ctx.send(f':white_check_mark: Slowmode disabled')

        await channel.edit(slowmode_delay=seconds)

        return await ctx.send(f':white_check_mark: Set slowmode to {seconds} seconds')

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))