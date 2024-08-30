import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import logging
import urllib.parse
logging.basicConfig(filename = "rankingCommands.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")


class RankingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        logging.info("RankingCommands Cog loaded")

    Rgroup = app_commands.Group(name="ranking", description="ranking")

    @Rgroup.command(name="daily", description="Display the top 15 daily rankings by pixels.")
    async def daily(self, interaction: discord.Interaction):
        """Fetch and display the top 10 daily rankings in a table format."""
        logging.info(f"{interaction.user} launched /ranking daily")
        await interaction.response.defer() # .send_message("<a:loading:1267469203103940673> Loading the ranking")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()

                    ranking_data = data.get("dailyRanking", [])

                    if not ranking_data:
                        await interaction.followup.send("No daily rankings found.", ephemeral=True)
                        return

                    top_15 = ranking_data[:14]

                    embed = discord.Embed(
                        title="Top 15 Daily Rankings by Pixels",
                        color=discord.Color.blue()
                    )

                    for entry in top_15:
                        name = entry['name'] # [str for str in entry['name'] if str not in emoji.UNICODE_EMOJI].join(" ")
                        if len(name) > 20:
                            name = name[:17] + "..."  

                        total_pixels = str(entry['t']).replace(',', '')
                        daily_total = str(entry['dt']).replace(',', '')
                        urlname = urllib.parse.quote(name)
                        if entry['facInfo'] is None :
                            fac_tag =" "
                        else :
                            fac_tag = entry['facInfo'][0]
                        embed.add_field(name=f"**{entry['dr']}**",
                                        value=("""**Name:** [%s %s](https://pixelya.fun/profile?name=%s) \n **ID:** %s\n **Total:** %s\n **Daily:** %s\n"""%(fac_tag, name, urlname, entry['id'], total_pixels, daily_total)),
                                        inline=True
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch rankings.", ephemeral=True)

    @Rgroup.command(name="total", description="Display the top 10 total rankings by pixels.")
    async def total(self, interaction: discord.Interaction):
        """Fetch and display the top 10 total rankings in a table format."""
        logging.info(f"{interaction.user} launched /ranking total")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()

                    ranking_data = data.get("ranking", [])

                    if not ranking_data:
                        await interaction.followup.send("No total rankings found.", ephemeral=True)
                        return

                    top_10 = ranking_data[:10]

                    embed = discord.Embed(
                        title="Top 10 Total Rankings by Pixels",
                        color=discord.Color.green()
                    )

                    for entry in top_10:
                        name = entry['name'] # [str for str in entry['name'] if str not in emoji.UNICODE_EMOJI].join(" ")
                        if len(name) > 20:
                            name = name[:17] + "..."  

                        if entry['facInfo'] is None :
                            fac_tag =" "
                        else :
                            fac_tag = entry['facInfo'][0]
                        total_pixels = str(entry['t']).replace(',', '')
                        daily_total = str(entry['dt']).replace(',', '')
                        urlname = urllib.parse.quote(name)
                        embed.add_field(
                            name=f"**{entry['r']}**",
                            value=("""**Name:** [%s %s](https://pixelya.fun/profile?name=%s) \n **ID:** %s\n **Total:** %s\n **Daily:** %s\n"""%(fac_tag, name, urlname, entry['id'], total_pixels, daily_total)),
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch rankings.", ephemeral=True)

    @Rgroup.command(name="country_daily", description="Display the top 10 daily country rankings by pixels.")
    async def country(self, interaction: discord.Interaction):
        """Fetch and display the top 10 daily country rankings in a table format."""
        logging.info(f"{interaction.user} launched /ranking country")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()

                    ranking_data = data.get("dailyCorRanking", [])

                    if not ranking_data:
                        await interaction.followup.send("No daily country rankings found.", ephemeral=True)
                        return

                    top_10 = ranking_data[:10]

                    embed = discord.Embed(
                        title="Top 10 Daily Country Rankings by Pixels",
                        color=discord.Color.purple()
                    )

                    for entry in top_10:
                        country_code = entry['cc'].upper()
                        flag = "".join([chr(127397 + ord(c)) for c in country_code])
                        pixels = str(entry['px']).replace(',', '')

                        embed.add_field(
                            name=f"{flag} {country_code}",
                            value=f"**Pixels:** {pixels}",
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch country rankings.", ephemeral=True)

    @Rgroup.command(name="country_total", description="Display the top 10 country rankings by pixels.")
    async def country(self, interaction: discord.Interaction):
        """Fetch and display the top 10 daily country rankings in a table format."""
        logging.info(f"{interaction.user} launched /ranking country_total")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()

                    ranking_data = data.get("totalCountrieRanking", [])

                    if not ranking_data:
                        await interaction.followup.send("No country rankings found.", ephemeral=True)
                        return

                    top_10 = ranking_data[:10]

                    embed = discord.Embed(
                        title="Top 10 Country Rankings by Pixels",
                        color=discord.Color.purple()
                    )

                    for entry in top_10:
                        country_code = entry['cc'].upper()
                        flag = "".join([chr(127397 + ord(c)) for c in country_code])
                        pixels = str(entry['px']).replace(',', '')

                        embed.add_field(
                            name=f"{flag} {country_code}",
                            value=f"**Pixels:** {pixels}",
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch country rankings.", ephemeral=True)
    
    
    @Rgroup.command(name="best_daily", description="Display the ranking of who placed the most in one day")
    async def best_daily(self, interaction : discord.Interaction):
        """Fetch and display the top 15 best daily stats in a table format."""
        logging.info(f"{interaction.user} launched /ranking best_daily")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()
                    ranking_data = data.get("bestDailyPlaced", [])[:15]
                    embed = discord.Embed(
                        title="Top 15 best daily Rankings by Pixels",
                        color=discord.Color.blue()
                    )
                    rank = 1
                    for entry in ranking_data:
                        name = entry['name']
                        if len(name) > 20:
                            name = name[:17] + "..."  

                        if entry['facInfo'] is None :
                            fac_tag =" "
                        else :
                            fac_tag = entry['facInfo'][0]
                        best = str(entry['px']).replace(',', '')

                        urlname = urllib.parse.quote(name)
                        embed.add_field(
                            name=f"**{rank}**",
                            value=("""**Name:** [%s %s](https://pixelya.fun/profile?name=%s) \n **ID:** %s\n **Best score:** %s\n"""%(fac_tag, name, urlname, entry['id'], best)),
                            inline=True
                        )
                        rank += 1

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch rankings.", ephemeral=True)

    
    Sgroup = app_commands.Group(name="stats", description="Statistics")
    @Sgroup.command(name="daily", description="Shows the total daily pixels placed")
    async def daily(self, interaction: discord.Interaction):
        "fetch and display the daily total pixels using an embed"
        logging.info(f"Daily stats by {interaction.user}")
        await interaction.response.defer()
        print("step 1")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    daily_data = data.get("totalDailyPixelsPlaced", [])[0]
                    print("step 2")
                    if not daily_data:
                        return await interaction.followup.send("No daily rankings found.", ephemeral=True)
                    embed = discord.Embed(
                        title = "Today's stats",
                        color = discord.Color.blue()
                    )
                    dailyTotal = f"{int(daily_data['dailyTotal']):_}".replace("_"," ")
                    lastHoury = f"{int(daily_data['lastHoury']):_}".replace("_"," ")
                    lastMin = f"{int(daily_data['lastMin']):_}".replace("_"," ")
                    embed.add_field(name="Today's total : ", value = f"{dailyTotal} pixels.", inline = False)
                    embed.add_field(name="Last hour : ", value= f"{lastHoury} pixels placed.")
                    embed.add_field(name="Last minute :", value = f"{lastMin} pixels placed.")

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch rankings.", ephemeral=True)

    
    @total.error
    @daily.error
    @country.error
    async def command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.followup.send("You don't have the necessary permissions to use this command.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RankingCommands(bot))