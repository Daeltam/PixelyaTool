import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import logging
import urllib.parse
import datetime
from operator import itemgetter
from enum import Enum
logging.basicConfig(filename = "rankingCommands.log", level = logging.INFO, format = "%(asctime)s:%(levelname)s:%(message)s")


class RankingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        logging.info("RankingCommands Cog loaded")

    rankings = app_commands.Group(name="ranking", description="ranking")

    @rankings.command(name="daily", description="Display the top 15 daily rankings by pixels.")
    async def daily(self, interaction: discord.Interaction):
        """Fetch and display the top 10 daily rankings in a table format."""
        logging.info(f"{interaction.user} launched /ranking daily")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()

                    ranking_data = data.get("dailyRanking", [])

                    if not ranking_data:
                        await interaction.followup.send("No daily rankings found.", ephemeral=True)
                        return

                    top_15 = ranking_data[:15]

                    embed = discord.Embed(
                        title="Top 15 Daily Rankings by Pixels",
                        color=discord.Color.blue()
                    )

                    for entry in top_15:
                        name = entry['name']
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

    @rankings.command(name="total", description="Display the top 15 total rankings by pixels.")
    async def total(self, interaction: discord.Interaction):
        """Fetch and display the top 15 total rankings in a table format."""
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

                    top_15 = [ entry for entry in ranking_data[:15] if int(entry['r']) <16]

                    embed = discord.Embed(
                        title="Top 10 Total Rankings by Pixels",
                        color=discord.Color.green()
                    )

                    for entry in top_15:
                        name = entry['name']
                        if len(name) > 20:
                            name = name[:17] + "..."  

                        if entry['facInfo'] is None :
                            fac_tag =" "
                        else :
                            fac_tag = entry['facInfo'][0]
                        total_pixels = str(entry['t']).replace(',', '')
                        daily_total = str(entry['dt']).replace(',', '')
                        urlname = urllib.parse.quote(name)
                        embed.set_field_at(
                            index = int(entry['r']),
                            name=f"**{entry['r']}**",
                            value=("""**Name:** [%s %s](https://pixelya.fun/profile?name=%s) \n **ID:** %s\n **Total:** %s\n **Daily:** %s\n"""%(fac_tag, name, urlname, entry['id'], total_pixels, daily_total)),
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Failed to fetch rankings.", ephemeral=True)

    @rankings.command(name="best_daily", description="Display the ranking of who placed the most in one day")
    async def best_daily(self, interaction : discord.Interaction):
        """Fetch and display the top 15 best daily stats in a table format."""
        logging.info(f"{interaction.user} launched /ranking best_daily")
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()
                    ranking_data = data.get("bestDailyPlaced", [])
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

    country = app_commands.Group(name = "country", description="country rankings", parent = rankings)

    @country.command(name="daily", description="Display the top 10 daily country rankings by pixels.")
    async def country_daily(self, interaction: discord.Interaction):
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

    @country.command(name="total", description="Display the top 10 country rankings by pixels.")
    async def country_total(self, interaction: discord.Interaction):
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
    
    factions = app_commands.Group(name = "factions", description="faction rankings", parent = rankings)
    factionList = {'Pixelya': '1', 'VoidEP': '3', 'Altaiya': '4', 'HayPF': '6', 'North Federation': '7', 'United States of Ameri': '8', 'Russian National Repub': '9' , 'ITALIA': '10', 'ISLAMIC UNION': '12', 'PCVoid': '13', 'Brazil Operation': '14', 'PIXELARG': '15', 'Chile Pixel': '16', 'France': '17', 'PeruPPF': '20', 'Indonesia': '21', 'GreecePYA': '22', "Gravedona's Empire": '23', 'Ukraine Pixelya': '25', 'HungarYA': '26', 'ISRAEL': '27', 'CIN': '28', 'Romania PYA': '29', 'Grenia.IRG': '30', 'Dardania': '31', 'ECUADOR': '37', 'Christianity': '39', 'UkrPixel': '40', 'Scotland Pixel': '41', '{HUN}HungaryCPN': '42', '! EXC': '47', 'Ural Pixel': '48', 'Georgian pixelya': '53', 'Christian Azerbaijan': '54', 'Abbasid State': '55'} # * create the list of all factions 
    async def rps_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]] :
        factionList = {'Pixelya': '1', 'VoidEP': '3', 'Altaiya': '4', 'HayPF': '6', 'North Federation': '7', 'United States of Ameri': '8', 'Russian National Repub': '9' , 'ITALIA': '10', 'ISLAMIC UNION': '12', 'PCVoid': '13', 'Brazil Operation': '14', 'PIXELARG': '15', 'Chile Pixel': '16', 'France': '17', 'PeruPPF': '20', 'Indonesia': '21', 'GreecePYA': '22', "Gravedona's Empire": '23', 'Ukraine Pixelya': '25', 'HungarYA': '26', 'ISRAEL': '27', 'CIN': '28', 'Romania PYA': '29', 'Grenia.IRG': '30', 'Dardania': '31', 'ECUADOR': '37', 'Christianity': '39', 'UkrPixel': '40', 'Scotland Pixel': '41', '{HUN}HungaryCPN': '42', '! EXC': '47', 'Ural Pixel': '48', 'Georgian pixelya': '53', 'Christian Azerbaijan': '54', 'Abbasid State': '55'}
        factionsList = [app_commands.Choice(name=name, value=ID) for name, ID in factionList.items() if current.lower() in name.lower()][:25]
        return factionsList
    factionsEnum = Enum('facs', factionList)
    
    @factions.command(name = "total", description="Display the top 25 factions all-time")
    async def factions_total(self, interaction : discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session :
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200 :
                    data = await response.json()

                    embed = discord.Embed(
                        title="Ranking of top 25 best factions in pixelya",
                        color=discord.Color.blue()
                    )

                    rankingfactions = data.get('rankingFactions', [])
                    factions = dict({ rank : {'id' : fac['id'] , 'name' : fac['name'], 'tag' : fac['tag'], 'total_pixels' : fac['tp'], 'daily_pixels' : fac['dp']} for rank, fac in enumerate(rankingfactions)}.items())
                    for entry in factions :
                        if entry < 24:
                            name = factions[entry]['name']
                            if len(name) > 20:
                                name = name[:17] + "..."  

                            urlfac = urllib.parse.quote(name)
                            embed.add_field(
                                name=f"**{entry +1}**",
                                value=("""**Name:** [%s] [%s](https://pixelya.fun/profile?name=%s) \n **ID:** %s\n **Total pixels:** %s \n **Daily Pixels:** %s \n"""%(factions[entry]['tag'], name, urlfac, factions[entry]['id'], factions[entry]['total_pixels'], factions[entry]['daily_pixels'])),
                                inline=True
                            )
                    return await interaction.followup.send(embed = embed)
                else:
                    return await interaction.followup.send("Failed to fetch rankings.")

    @factions.command(name = "top", description="Display the top 15 members of the faction.")
    @app_commands.autocomplete(faction=rps_autocomplete)
    @app_commands.describe(faction="If the faction you want isn't in the list, please contact @daeltam to add it")
    async def factions_top(self, interaction : discord.Interaction, faction : str):
        await interaction.response.defer()
        url = 'https://pixelya.fun/api/getfactioninfo'
        payload = {'id': int(faction)}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                # Check if the request was successful
                if response.status == 200:
                    result = await response.json()
                    result = result['fac']
                    factionURL = "https://pixelya.fun/faction?name=%s"%(urllib.parse.quote(result['name']))
                    embed = discord.Embed(
                        title="Top 15 members of %s"%(result['name']),
                        description = result['desc'],
                        url=factionURL,
                        color=discord.Color.from_str(result['color'][:5]),
                        timestamp=datetime.datetime.now(datetime.UTC)
                    )
                    all_players = result['membersinfo']+result['modsinfo']+result['ownerinfo']
                    playerInfos = sorted(all_players, key=itemgetter(4), reverse = True)[:15]
                    for rank, playerInfo in enumerate(playerInfos):
                        urlname = urllib.parse.quote(playerInfo[1])
                        embed.add_field(
                            name=f"**{rank +1}**",
                            value=("""**Name:** [%s](https://pixelya.fun/profile?name=%s) :flag_%s: \n **ID:** %s\n **Total:** %s pixels\n **Daily:** %s pixels\n"""%(playerInfo[1], urlname, playerInfo[2], playerInfo[0], playerInfo[4], playerInfo[5])),
                            inline=True
                        )
                    embed.set_author(name=result['name'], url=factionURL,
                        icon_url=result['avatar'])
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"Request failed with status code {response.status}")
   
    stats = app_commands.Group(name="stats", description="Statistics")
    @stats.command(name="daily", description="Shows the total daily pixels placed")
    async def stats_daily(self, interaction: discord.Interaction):
        "fetch and display the daily total pixels using an embed"
        logging.info(f"Daily stats by {interaction.user}")
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pixelya.fun/ranking") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    daily_data = data.get("totalDailyPixelsPlaced", [])[0]
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
    @best_daily.error
    @stats_daily.error
    @country_daily.error
    @country_total.error
    @factions_total.error
    async def command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.followup.send("You don't have the necessary permissions to use this command.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RankingCommands(bot))
