import discord
from discord.ext import commands
from discord import app_commands
import datetime
import logging
from typing import Literal, Optional

class AdminCommands(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        logging.basicConfig(filename = "adminCommands.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")


    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        return logging.info("Admin Commands Cog loaded")
        
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
        """Syncronize commands : https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html : link to the function"""
        logging.info(f"Sync command called : !sync{spec} by {ctx.author}")
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
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild'} :/{' ; ' .join([sync.name for sync in synced])} command"
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
        """Changes slowmode, give time in seconds and channel (optional) with the #"""
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

        logging.info("%s has modified %s's slowmode to %s seconds"%(ctx.author, channel.name, seconds))

        if seconds==0:
            await channel.edit(slowmode_delay=0)
            return await ctx.send(f':white_check_mark: Slowmode disabled')

        await channel.edit(slowmode_delay=seconds)

        return await ctx.send(f':white_check_mark: Set slowmode to {seconds} seconds')
    
    @app_commands.describe(role_tag = "The tag between [] that you have in the faction name, case insensitive. (Exemple : void)")
    @app_commands.command(name = "add_to_my_faction", description="Adds a discord member do your discord faction")
    async def add_faction(self, interaction : discord.Interaction, member : discord.Member, role_tag : str):
        if interaction.guild_id != 1160702908552204288 :
            return await interaction.response.send_message("This command is restricted to the Pixelya Official Server, you can join it here : https://discord.gg/8vcWt7XGKt")
        roles = interaction.user.roles
        factionLeader = discord.utils.get(interaction.guild.roles, id = 1259269181065662625)
        if factionLeader not in roles:
            return await interaction.response.send_message("You need to be the Faction Leader to give the role to someone") 
        try :
            facrole = [ role for role in roles if role.name.lower().startswith(f"[{role_tag.lower()}]")][0]
        except IndexError:
            return await interaction.response.send_message("<a:error40:1267490066125819907> The tag you have given does not correspond to any faction you're in, please try again")
        await member.add_roles(facrole)
        return await interaction.response.send_message(f"{member.mention}, you have recieved the role {facrole.name} by your faction leader {interaction.user} !")


    @app_commands.command(name = "help", description = "Help command")
    async def helping(self, interaction : discord.Interaction):
        logging.info(f"help command by {interaction.user}")
        await interaction.response.defer()
        helpInfos = discord.Embed(
            title="Informations about @Pixelya.fun",
            description="How to use the Pixelya.fun discord bot, list of all commands and bonus infos",
            url="https://pixelya.fun",
            color = discord.Color.from_str("#21d8c9"),
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        helpInfos.add_field(name="Area Download", value = "Download an area of pixelya, use `/area infos` for detailed how-to-use.", inline=False)
        helpInfos.add_field(name="History Download", value = "Download the history of picelya, use `/history infos` for detailed how-to-use.", inline = False)
        helpInfos.add_field(name="Webhook request", value = "Add Pixelya Status to your discord, doesn't need the bot for this. Check `/webhook infos` for detailed how-to-use.", inline=False)
        helpInfos.add_field(name="Ranking commands", value = "With `/ranking total; daily and best_daily`, you will be able to access pixelya ranking stats from the discord !", inline = False)
        helpInfos.add_field(name="Ranking Country commands", value = "With `/ranking country; daily and total` you will be able to access pixelya country stats from the discord !", inline = False)
        helpInfos.add_field(name="Ranking factions commands", value = "With `/ranking faction total and top`, you will be able to access pixelya faction stats from the discord !", inline = False)
        helpInfos.add_field(name="Add the bot to your discord! ", value = "Here is the link : [Add Me](https://discord.com/oauth2/authorize?client_id=1253684567525691483) ! Make sure to DM me in case of any bug, it still has flaws")
        helpInfos.set_author(name="@Daetlam", url="https://github.com/Daeltam/PixelyaTool",
                            icon_url="https://media.discordapp.net/attachments/1178076180637818910/1178077857633800192/logopixelya2.png?ex=66d57ec0&is=66d42d40&hm=bcff3bcbb864f0e0a2471f829f7b7fd0fd0562c9b71e6ca11e740fbbfd33fba3&=&format=webp&quality=lossless&width=320&height=320")
        return await interaction.followup.send(embed=helpInfos)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))