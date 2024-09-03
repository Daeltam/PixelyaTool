import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import logging
import datetime
import traceback
import WebhookUrl as WHU

class Monitor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.url_to_check = "https://pixelya.fun"
        self.webhook_url = WHU.urls
        self.was_down = None 
        logging.basicConfig(filename = "monitor.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        print("Monitor Cog loaded")
        await self.send_initial_status()
        await self.check_website.start()

    async def send_initial_status(self) -> None:
        is_up, status = await self.check_website_status()
        if is_up:
            description = "The website https://pixelya.fun is currently up."
            color = 3066993  
        else:
            description = f"The website is currently down. Error code: {status}"
            color = 15158332  
        
        await self.send_discord_embed(
            title="Website Status on Startup",
            description=description,
            color=color,
            startup = True
        )

    async def send_discord_embed(self, title: str, description: str, color: int, startup :bool = False ) -> None:
        current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        embed = {
            "title": title,
            "description": description,
            "url" : "https://pixelya.fun",
            "color": color,
            "footer": {
                "text": f"Checked at {current_time}"
            }
        }
        data = {
            "embeds": [embed]
        }
        session = aiohttp.ClientSession()
        if not startup :
            for url in self.webhook_url:
                response = await session.post(url, json=data)
            if response.status == 204:
                logging.debug("Embed sent successfully.")
            else:
                logging.warning(f"Failed to send embed: {response.status}")
            await session.close()
        elif startup:
            response = await session.post(self.webhook_url[0], json=data)
            if response.status == 204:
                logging.debug("Embed sent successfully.")
            else:
                logging.warning(f"Failed to send embed: {response.status}")
            await session.close()
        

    async def check_website_status(self) -> tuple[bool, int]:
        try:
            session = aiohttp.ClientSession()
            response = await session.get(self.url_to_check)
            status_code = response.status
            await session.close()
            return (status_code == 200), status_code
        except aiohttp.web.HTTPException as e:
            logging.warning(f"Request failed: {e}")
            return False, 0 

    @tasks.loop(seconds=60)
    async def check_website(self) -> None:
        is_up, status = await self.check_website_status()

        if is_up and self.was_down:
            await self.send_discord_embed(
                title="Website Up",
                description="The website https://pixelya.fun is back up.",
                color=3066993  
            )
            self.was_down = False
        elif not is_up and not self.was_down:
            await self.send_discord_embed(
                title="Website Down",
                description=f"The website returned error code: {status}",
                color=15158332  
            )
            self.was_down = True

    group = app_commands.Group(name="webhook", description="Requesting Webhook commands")
    @group.command(name = "info", description = "Explains /webhook request")  
    async def webhook_info(self, interaction : discord.Interaction):
        embed = discord.Embed(
            title="Request a Pixelya Status Webhook addition",
            description="Here is an explaination on how to use this command without making the bot sending an error message :",
            url="https://www.pixelya.fun",
            color=discord.Color.from_rgb(35, 39, 42),
            timestamp= datetime.datetime.now()
        )
        embed.add_field(name = "What is a webhook ?", value = "A Webhook is a link that creates a connexion between a discord channel and my bot. You don't need to have the bot in your server to create a webhook, just to share the link and the bot will be able to send messages in the channel. See this tutorial on how to create a discord Webhook, then share me the `Webhook url` with /webhook request", inline = False)
        embed.add_field(name = "Video Tutorial :", value = "https://www.youtube.com/watch?v=fKksxz2Gdnc")
        embed.add_field(name = "What is the use of this webhook ?", value = "This webhook enables the bot to send to the channel pixelya status warning as you can find in the pixelys status discord, warning players about the state of the website right now. This doesn't add the bot to your discord.")
        return await interaction.response.send_message(embed=embed)

    @group.command(name = "request", description = "Makes a request for adding the pixelys Status warning to your own server")
    async def webhook_request(self, interaction : discord.Interaction, url : str):
        logging.info(f"{interaction.user} is sending {url}")
        try:
            me  = self.bot.get_user(1094995425326542898)
            await me.send(f"Webhook Url request by {interaction.user} : `{url}`")
        except Exception as e:
            appInfo = await self.bot.application_info()
            print(appInfo.owner.name)
            print(traceback.print_exc())
            logging.error(f"Error when sending DM with /webhook request, {e}")
            return await interaction.response.send_message("Something went wrong, the message has not been sent.", ephemeral = True)
        return await interaction.response.send_message("Your url has been sent !", ephemeral = True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Monitor(bot))