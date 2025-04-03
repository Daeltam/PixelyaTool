import discord
from discord.ext import commands
from discord import app_commands
import datetime
import logging
import re
from PIL import Image
import io
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
    # @app_commands.guilds(1160702908552204288)
    async def add_faction(self, interaction : discord.Interaction, member : discord.Member, role_tag : str):
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

    @app_commands.command(name = "about", description = "about the bot")
    async def about_me(self, interaction : discord.Interaction):
        logging.info(f"about me command by {interaction.user}")
        await interaction.response.defer()
        aboutInfos = discord.Embed(
            title="Informations about @Pixelya.fun",
            description="About me",
            url="https://pixelya.fun",
            color = discord.Color.from_str("#21d8c9"),
            timestamp=datetime.datetime.now(datetime.UTC),
        )
        aboutInfos.add_field(name = "Stats :", value=f"I'm in {len(self.bot.guilds)} servers for now !")
        aboutInfos.add_field(name="Terms of service", value = "[Click here !](https://daeltam.github.io/PixelyaTool/terms-of-service.html)", inline=False)
        aboutInfos.add_field(name="Privacy Policy", value = "[Click here !](https://daeltam.github.io/PixelyaTool/Privacy-Policy.html)", inline = True)
        aboutInfos.add_field(
            name="Add the bot to your discord! ",
            value = "Here is the link : [Add Me](https://discord.com/oauth2/authorize?client_id=1253684567525691483) ! Make sure to DM me in case of any bug, it still has flaws",
            inline=False)
        aboutInfos.set_author(name="@Daetlam", url="https://github.com/Daeltam/PixelyaTool",
                            icon_url="https://media.discordapp.net/attachments/1178076180637818910/1178077857633800192/logopixelya2.png?ex=66d57ec0&is=66d42d40&hm=bcff3bcbb864f0e0a2471f829f7b7fd0fd0562c9b71e6ca11e740fbbfd33fba3&=&format=webp&quality=lossless&width=320&height=320")
        aboutInfos.set_image(url="https://pixelya.fun/PixelyaLOGO.png")
        return await interaction.followup.send(embed=aboutInfos)
    
    colorGroup = app_commands.Group(name="color", description="Colors related commands")

    #@colorGroup.command(name = "picker", description = "Try a color")
    # @colorGroup.checks.cooldown(1, 15, key = lambda i: (i.user.id))
    #@colorGroup.guilds(1160702908552204288)
    async def about_me(self, interaction : discord.Interaction, hexCode : str):
        return #! TEMPORARY
        logging.info(f"about me command by {interaction.user}")
        # Validate hex code
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexCode):
            return await interaction.response.send_message("Invalid hex code. Please provide a valid hex code in the format #RRGGBB or #RGB.", ephemeral=True)

        # Create an image with the specified color
        image = Image.new("RGB", (100, 100), hexCode)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Create a discord file and send it
        file = discord.File(fp=buffer, filename="color.png")
        embed = discord.Embed(title="Color Picker", description=f"Here is the color {hexCode}", color=int(hexCode[1:], 16))
        embed.set_image(url="attachment://color.png")

        await interaction.response.send_message(embed=embed, file=file)

    @colorGroup.command(name = "suggesting", description = "This command Suggests a new color to the game owner, there is a 1month cooldown")
    # @colorGroup.checks.cooldown(1, 2592000, key = lambda i: (i.user.id))  # 1 month cooldown in seconds
    # @colorGroup.guilds(1160702908552204288)
    async def suggesting(self, interaction : discord.Interaction, hexCode : str):
        return # ! TEMPORARY
        logging.info(f"suggesting command by {interaction.user}")
        # Validate hex code
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexCode):
            return await interaction.response.send_message("Invalid hex code. Please provide a valid hex code in the format #RRGGBB or #RGB.", ephemeral=True)

        # Create an image with the specified color
        image = Image.new("RGB", (100, 100), hexCode)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Create a discord file
        file = discord.File(fp=buffer, filename="suggested_color.png")

        # Send the suggestion to the specified thread
        thread_id = 1352233525650391051  # Placeholder for the thread ID
        user_id = 480530535760789511  # Placeholder for the user ID to ping
        thread = interaction.guild.get_thread(thread_id)
        if thread is None:
            return await interaction.response.send_message("The suggestion thread does not exist.", ephemeral=True)

        embed = discord.Embed(title="New Color Suggestion", description=f"Suggested by {interaction.user.mention}", color=int(hexCode[1:], 16))
        embed.add_field(name="Hex Code", value=hexCode)
        embed.set_image(url="attachment://suggested_color.png")

        await thread.send(content=f"<@{user_id}>", embed=embed, file=file)
        return await interaction.response.send_message("Your color suggestion has been sent!", embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(self.guild.me).send_messages:
                await channel.send(f'Hey there! Thanks for adding me here ! Don\'t forget to do /about or /help to have more rules and informations about my commands. Have a good time playing Pixelya !')
                break

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, app_commands.CommandInvokeError):
            await ctx.send("This command can only be used in the specified guild.", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Please try again after {error.retry_after:.2f} seconds.", ephemeral=True)
        else:
            await ctx.send("An error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
