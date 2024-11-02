#!/usr/bin/python3
import discord
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio, aiohttp
import datetime
import logging, traceback
import WebhookUrl as WHU
PYF_CLOWN_URL = "https://pixelya.fun/void"

async def getStatus():
    url = PYF_CLOWN_URL
    async with aiohttp.ClientSession() as session:
        attempts = 0
        while True:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return data
            except:
                if attempts > 3:
                    logging.warning(f"Could not get {url} in three tries, cancelling")
                    raise
                attempts += 1
                logging.warning(f"Failed to load {url}, trying again in 5s")
                await asyncio.sleep(5)
                pass

class clownVoid(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.webhook_urls = WHU.ClownVoidWebhook
        self.isVoidAlive = False
        logging.basicConfig(filename = "clownVoid.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")


    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        return logging.info("Clown Void Cog loaded")
    

    async def on_message(self, message : discord.Message):
        if "when void" in message.lowercase :
            #Request API for void status
            void_status : str #Requete
            message.answer(void_status, mention=False)

    group = app_commands.Group(name = "clown_void", description = "Gives yourself the @clownVoid-ping role (or removes it)")
    @group.command(name ="role", description="Gives or removes the @clownVoid-ping role.")
    async def give_remove_role(self, interaction : discord.Interaction):
        if interaction.guild_id != 1160702908552204288 :
            return await interaction.response.send_message("This command is only available in the official pixelya discord", ephemeral=True)
        else :
            try :
                if interaction.user.get_role(1293447212147408967):
                    await interaction.user.remove_roles(interaction.guild.get_role(1293447212147408967))
                    return await interaction.response.send_message("You have removed the @clownVoid-ping role ! ", ephemeral=True)
                await interaction.user.add_roles(interaction.guild.get_role(1293447212147408967))
                return await interaction.response.send_message("You have now the @clownVoid-ping role ! ", ephemeral=True)
            except Exception :
                logging.warning(traceback.print_exc())
                return await interaction.response.send_message("An error occured, I'm sorry", ephemeral=True)

    # * Make something similar to the pixelya status api
    async def check_void_status(self):
        self.isVoidAlive = True
        while self.isVoidAlive :
            try :
                status = await getStatus()
                print("Status =", status, "\n___________________________ \n")
                # logging.info(status)
                voidInfo = status['voidInfo']
                voidRemaining = status["voidRemaining"]

                if voidInfo.endswith("celebration.") : # ? celebration time left
                    datetime_left = datetime.datetime.strptime(status["voidInfo"], '%Mmin %Ssec. to the end of the celebration.')
                    celTimLeft = datetime_left.second+ datetime_left.minute*60
                    print("Celebration time left : ", celTimLeft, "\n___________________ \n")

                    if celTimLeft >= 2100 :
                        await self.post_discord_embed(
                            title="GG ! Void is Won!",
                            description=f"Celebration time left : {datetime_left.minute} minutes, {datetime_left.second} seconds.",
                            color=discord.Color.from_rgb(135,216,50))
                        await asyncio.sleep(900) # 15 minutes
                        print("Sleeping for 15 minutes (+warning message)")
                    elif celTimLeft > 900 :
                        await self.post_discord_embed(
                            title="Celebration time !",
                            description=f"Time left : {datetime_left.minute} minutes, {datetime_left.second} seconds",
                            color=discord.Color.from_rgb(135,216,50))
                        await asyncio.sleep(900)
                        print("Sleeping for 15 minutes")

                    elif 30<celTimLeft<900 :
                        await self.post_discord_embed(
                            title="Celebration time !",
                            description=f"Time left : {datetime_left.minute} minutes, {datetime_left.second} seconds",
                            color=discord.Color.from_rgb(135,216,50))
                        await asyncio.sleep(celTimLeft)
                        print(f"waiting for {celTimLeft} seconds (until end of celebration)")

                elif voidInfo.endswith("punishment.") : # ? punishment time left
                    datetime_left = datetime.datetime.strptime(status["voidInfo"], '%Mmin %Ssec. to the end of the void punishment.')
                    punTimLeft = datetime_left.second+ datetime_left.minute*60
                    print("Punishment time left : ", punTimLeft, "\n___________________ \n")
                    await self.post_discord_embed(
                            title="You lost again the void... Punishment time",
                            description=f"Time left : {datetime_left.minute} minutes, {datetime_left.second} seconds",
                            color=discord.Color.from_rgb(00,00,00))
                    await asyncio.sleep(punTimLeft)
                    print(f"waiting for {punTimLeft} seconds (until end of punishment)")

                elif voidRemaining["time"] != "N/A" : # ? it's fighting time
                    location = voidRemaining["coords"]
                    time_left = datetime.datetime.strptime(voidRemaining["time"], "%Mmin %Ssec.")
                    percentage = voidRemaining["percen"]
                    print("TLM*60+TLS", time_left.minute*60+time_left.second)
                    if time_left.minute*60+time_left.second >31:
                        await self.post_discord_embed(
                            title = "Void Fight is occuring right now",
                            description = f"At {location}, \n {time_left.minute} minutes, {time_left.second} seconds left, \n{percentage} progress !",
                            color = discord.Color.from_rgb(255,140,0))
                        await asyncio.sleep(30)
                        print("Sleeping for 30 seconds")

                    elif 0<time_left.minute*60+time_left.second<31:
                        await asyncio.sleep(time_left.second)
                        print(f"Sleeping for {time_left.second}")


                elif voidInfo == "N/A" : # ? Lengh of waiting for next void message ?
                    # * stripe the status into the useful information
                    # * Find the datetime at which the next void will be
                    nextVoidUTC = datetime.datetime.strptime(status["nextvoidUTC"], "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=datetime.timezone.utc)
                    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc)
                    if nextVoidUTC < datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc) :
                        print(nextVoidUTC, datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc))
                        nextVoidUTC = datetime.timedelta(hours=2).seconds
                    else :
                        nextVoidUTC = nextVoidUTC - now
                        nextVoidUTC = nextVoidUTC.seconds
                    print("Next void is in : ", nextVoidUTC, "\n___________________\n")
                    if nextVoidUTC >  6600 - 10 :
                        # ! Only since a few seconds ! (lengh of void ?)
                        await self.post_discord_embed(
                            title="Celebration time is over",
                            description="Get back to work",
                            color = discord.Color.from_rgb(44,52,92))
                        await asyncio.sleep(1800)
                        print("sleeping for 30 minutes")

                    elif 1800<nextVoidUTC<6600-10 :
                        await self.post_discord_embed(
                            title = "Clown Void Status",
                            description=f"Next void is in {round(nextVoidUTC/60)} minutes, {nextVoidUTC//60} seconds.",
                            color = discord.Color.from_rgb(255,215,0))
                        await asyncio.sleep(1800)
                        print("sleeping for 30 minutes")

                    elif 60<nextVoidUTC<1800 :
                        await self.post_discord_embed(
                            title = "Clown Void Status",
                            description=f"Next void is in {round(nextVoidUTC/60)} minutes, {nextVoidUTC//60} seconds",
                            color = discord.Color.from_rgb(255,215,0))
                        await asyncio.sleep(nextVoidUTC - 60)
                        print(f"\n Sleeping for {nextVoidUTC -60} seconds \n ") # ? problème ici

                    elif 11<nextVoidUTC < 60:
                        await self.post_discord_embed(
                            title = "Clown Void Status",
                            description=f"Next void is in {nextVoidUTC} seconds",
                            color = discord.Color.from_rgb(255,215,0))
                        await asyncio.sleep(10)
                        print("sleeping for 10 seconds before Warning")

                    elif 0<nextVoidUTC < 11:
                        await self.post_discord_embed(
                            title = "**CLOWN VOID WARNING**",
                            description=f"NEXT VOID IS IN {nextVoidUTC} SECONDS, GET READY TO FIGHT !", 
                            color = discord.Color.from_rgb(229,00,00)) # ! Get role ID
                        await asyncio.sleep(nextVoidUTC+2)
                        print(f"Sleeping for {nextVoidUTC +2} seconds : until start of the fight")

            except Exception :
                print(traceback.print_exc())
                await self.post_discord_embed(
                    title="Void Clown has stopped working",
                    description="Don't ask me why, an Exception has been raised \n<@1094995425326542898> come here",
                    color = discord.Color.from_rgb(00,00,00))
                self.isVoidAlive = False
            
        else : # * considering void status as broken -> no void right now
            await self.post_discord_embed(
                    title="Void Clown has stopped working",
                    description="Don't ask me why...  \n<@1094995425326542898> come here",
                    color = discord.Color.from_rgb(00,00,00))
            self.isVoidAlive = False

    @commands.is_owner()
    @group.command(name = "restart_void", description="Restarts the void status webhook after the void clown has broke down. Please don't misuse it")
    async def restart_void(self, interaction : discord.Interaction, force : bool = True):
        logging.info(f"{interaction.user} has used /restart void")
        if not interaction.user.guild_permissions.administrator :
            return await interaction.response.send_message("You do not have the required permissions to use this command.")
        elif self.isVoidAlive :
            return await interaction.response.send_message("The void status is already working, you don't need to restart it")
        else :
            status = await getStatus()
            try :
                nextVoidUTC = status['nextvoidUTC']
                print(nextVoidUTC)
            except Exception :
                print(traceback.print_exc())
                return await interaction.response.send("Either the page https://pixelya.fin/void is not working, either there is something wrong with the bot. Please contact @daeltam if you see that the page is working.")
            else : 
                try :
                    self.isVoidAlive = False
                    await interaction.response.send_message("The Bot is back up and running !")
                    await self.check_void_status() # ! Maybe not useful if i put self.void as true

                except Exception :
                    print(traceback.print_exc())
                

    async def post_discord_embed(self, title: str, description: str, color: int) -> None:
        current_time = datetime.datetime.now()
        embed = discord.Embed(
            title= title,
            description = description,
            url = "https://pixelya.fun",
            color= color,
            timestamp=current_time    
        )
        try :
            for webhook_url in self.webhook_urls :
                async with aiohttp.ClientSession() as session :
                    Webhook = discord.Webhook.from_url(webhook_url, client= self.bot, session=session)
                    if title == "**CLOWN VOID WARNING**" :
                        await Webhook.send(f"<@&{self.webhook_urls[webhook_url]}>", embed=embed)
                    else :
                        await Webhook.send(embed=embed)
        except Exception:
            print(traceback.print_exc())

    # * hybrid command with "when" prefix or /voidstatus
    @commands.hybrid_command(name = "void", description="Sends the current void status") # guild = discord.Object(id = 5165464)
    async def when_void(self, ctx : commands.Context) -> None :
        logging.info(f"{ctx.author} used 'when void' or /void")
        void_status = await getStatus()
        Info = void_status["nextVoidIn"]
        if void_status['voidInfo'].endswith("celebration."):
            embed = discord.Embed(
                title = "Void Clown status",
                description = "Celebration time ! " + void_status['voidInfo'],
                url  = "https://pixelya.fun",
                color = discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        elif void_status['voidInfo'].endswith("punishment."):
            embed = discord.Embed(
                title = "Void Clown status",
                description = "Punishment time" + void_status['voidInfo'],
                url  = "https://pixelya.fun",
                color = discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        elif void_status["voidRemaining"]["time"] != "N/A":
            embed = discord.Embed(
                title = "Void Clown status",
                description = "Fighting time !" + void_status["voidRemaining"]["time"] + "time left. \n Coordinates :"+ void_status["voidRemaining"]["coords"] + void_status["voidRemaining"]["percen"] + "progress.",
                url  = "https://pixelya.fun",
                color = discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        elif void_status["nextVoidIn"].endswith("ago."):
            embed = discord.Embed(
                title = "Void Clown status",
                description = void_status["nextVoidIn"],
                url  = "https://pixelya.fun",
                color = discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        else :
            embed = discord.Embed(
                title = "Void Clown status",
                description = "Next void is in " + Info,
                url  = "https://pixelya.fun",
                color = discord.Color.random(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        return await ctx.send(embed = embed)

async def setup(bot):
    await bot.add_cog(clownVoid(bot))