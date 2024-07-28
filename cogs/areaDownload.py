#!/usr/bin/python3
from discord import app_commands
import discord
from discord.ext import commands
import PIL.Image
import sys, os, io, math
import asyncio
import aiohttp
import nest_asyncio, datetime
nest_asyncio.apply()

# USER_AGENT = "pyf areaDownload 1.0 " + ' '.join(sys.argv[1:])
# PYF_URL = "https://pixelya.fun"
# GLOBAL TO BE DEFINED

USER_AGENT = "pyf areaDownload 1.0 0 -1_-1 1_1"
PYF_URL = "https://pixelya.fun"

class Color(object):
    def __init__(self, index, rgb):
        self.rgb = rgb
        self.index = index

class EnumColorPixelya:

    ENUM = []

    def getColors(canvas):
        colors = canvas['colors']
        for i, color in enumerate(colors):
            EnumColorPixelya.ENUM.append(Color(i, tuple(color)))
    
    @staticmethod
    def index(i):
        for color in EnumColorPixelya.ENUM:
            if i == color.index:
                return color
        return EnumColorPixelya.ENUM[0]

class Matrix:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.width = None
        self.height = None
        self.matrix = {}

    def add_coords(self, x, y, w, h):
        if self.start_x is None or self.start_x > x:
            self.start_x = x
        if self.start_y is None or self.start_y > y:
            self.start_y = y
        end_x_a = x + w
        end_y_a = y + h
        if self.width is None or self.height is None:
            self.width = w
            self.height = h
        else:
            end_x_b = self.start_x + self.width
            end_y_b = self.start_y + self.height
            self.width = max(end_x_b, end_x_a) - self.start_x
            self.height = max(end_y_b, end_y_a) - self.start_y

    async def create_image(self, filename = None):
        img = PIL.Image.new('RGBA', (self.width, self.height), (255, 0, 0, 0))
        pxls = img.load()
        for x in range(self.width):
            for y in range(self.height):
                try: 
                    color = self.matrix[x + self.start_x][y + self.start_y].rgb
                    pxls[x, y] = color
                except (IndexError, KeyError, AttributeError):
                    pass
        # Trying to make this work differently
        # if filename is not None: 
        #   if filename == 'b':
        #     b = io.BytesIO()
        #     img.save(b, "PNG")
        #     b.seek(0)
        #     return b
        #   else:
        #     img.save(filename)
        # else:
        #     img.show()
        # img.close()
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            img.seek(0)
            return img 

    def set_pixel(self, x, y, color):
        if x >= self.start_x and x < (self.start_x + self.width) and y >= self.start_y and y < (self.start_y + self.height):
            if x not in self.matrix:
                self.matrix[x] = {}
            self.matrix[x][y] = color

async def fetchMe():
    url = f"{PYF_URL}/api/me"
    headers = {
      'User-Agent': USER_AGENT
    }
    async with aiohttp.ClientSession() as session:
        attempts = 0
        while True:
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    return data
            except:
                if attempts > 3:
                    print(f"Could not get {url} in three tries, cancelling")
                    raise
                attempts += 1
                print(f"Failed to load {url}, trying again in 5s")
                await asyncio.sleep(5)
                pass

async def fetch(session, canvas_id, canvasoffset, ix, iy, target_matrix):
    url = f"{PYF_URL}/chunks/{canvas_id}/{ix}/{iy}.bmp"
    headers = {
      'User-Agent': USER_AGENT
    }
    attempts = 0
    while True:
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.read()
                offset = int(-canvasoffset * canvasoffset / 2)
                off_x = ix * 256 + offset
                off_y = iy * 256 + offset
                if len(data) == 0:
                    clr = EnumColorPixelya.index(0)
                    for i in range(256*256):
                        tx = off_x + i % 256 
                        ty = off_y + i // 256
                        target_matrix.set_pixel(tx, ty, clr)
                else:
                    i = 0
                    for b in data:
                        tx = off_x + i % 256
                        ty = off_y + i // 256
                        bcl = b & 0x7F
                        target_matrix.set_pixel(tx, ty, EnumColorPixelya.index(bcl))
                        i += 1

                print(f"Downloaded a new chunk from {url}")
                break
        except:
            if attempts > 3:
                print(f"Could not get {url} in three tries, cancelling")
                raise
            attempts += 1
            print(f"Failed to load {url}, trying again in 3s")
            await asyncio.sleep(3)
            pass

async def get_area(canvas_id, canvas, x, y, w, h):
    target_matrix = Matrix()
    target_matrix.add_coords(x, y, w, h)
    canvasoffset = math.pow(canvas['size'], 0.5)
    offset = int(-canvasoffset * canvasoffset / 2)
    xc = (x - offset) // 256
    wc = (x + w - offset) // 256
    yc = (y - offset) // 256
    hc = (y + h - offset) // 256
    print(f"Loading from {xc} / {yc} to {wc + 1} / {hc + 1}")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for iy in range(yc, hc + 1):
            for ix in range(xc, wc + 1):
                tasks.append(fetch(session, canvas_id, canvasoffset, ix, iy, target_matrix))
        await asyncio.gather(*tasks)
        return target_matrix

def validateCoorRange(ulcoor: str, brcoor: str, canvasSize: int):
    if not ulcoor or not brcoor:
        return "Not all coordinates defined"
    splitCoords = ulcoor.strip().split('_')
    if not len(splitCoords) == 2:
        return "Invalid Coordinate Format for top-left corner"
    
    x, y = map(lambda z: int(math.floor(float(z))), splitCoords)

    splitCoords = brcoor.strip().split('_')
    if not len(splitCoords) == 2:
        return "Invalid Coordinate Format for top-left corner"
    u, v = map(lambda z: int(math.floor(float(z))), splitCoords)
    
    error = None

    if (math.isnan(x)):
        error = "x of top-left corner is not a valid number"
    elif (math.isnan(y)):
        error = "y of top-left corner is not a valid number"
    elif (math.isnan(u)):
        error = "x of bottom-right corner is not a valid number"
    elif (math.isnan(v)):
        error = "y of bottom-right corner is not a valid number"
    elif (u < x or v < y):
        error = "Corner coordinates are aligned wrong"

    if not error is None:
        return error
    
    canvasMaxXY = canvasSize / 2
    canvasMinXY = -canvasMaxXY
    
    if (x < canvasMinXY or y < canvasMinXY or x >= canvasMaxXY or y >= canvasMaxXY):
        return "Coordinates of top-left corner are outside of canvas"
    if (u < canvasMinXY or v < canvasMinXY or u >= canvasMaxXY or v >= canvasMaxXY):
        return "Coordinates of bottom-right corner are outside of canvas"
    
    return (x, y, u, v)

async def main():
    """to be rewritten"""
    # apime = await fetchMe()
    # former warning message, to be added as a description :
    Description = """
    if len(sys.argv) != 5:
        print("Download an area of pixelya")
        print("Usage: areaDownload.py canvasID startX_startY endX_endY filename.png")
        print("(use R key on pixelya to copy coordinates)")
        print("canvasID: ", end='')
        for canvas_id, canvas in apime['canvases'].items():
            if 'v' in canvas and canvas['v']:
                continue
            print(f"{canvas_id} = {canvas['title']}", end=', ')
        print()
        return"""

    # canvas_id = sys.argv[1]

    # if canvas_id not in apime['canvases']:
    #     print("Invalid canvas selected")
    #     return

    # canvas = apime['canvases'][canvas_id]

    # parseCoords = validateCoorRange(sys.argv[2], sys.argv[3], canvas['size'])

    # if (type(parseCoords) is str):
    #     print(parseCoords)
    #     sys.exit()
    # else:
    #     x, y, w, h = parseCoords
    #     w = w - x + 1
    #     h = h - y + 1

    # EnumColorPixelya.getColors(canvas)
    # filename = sys.argv[4] (Useless)

    # matrix = await get_area(canvas_id, canvas, x, y, w, h)
    # print("Saving image ...")
    # matrix.create_image('./output/'+filename)
    # print("Done! you can find your image on the output folder.")

if __name__ == "__main__":
    asyncio.run(main())

# Slash Command
class areaDownload(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def CogLoaded(self) -> None:
        return print("areaDownload Cog loaded")
    
    group = app_commands.Group(name="area", description="Area Download related commands")

    @group.command(name = "infos", description = r"Information on how to use `/area download`")
    async def info_area_download(self, interaction : discord.Interaction):
        print(f"information comment send by {interaction.user}")
        apime = await fetchMe()
        # will send an embed explaining how download area works
        informations = discord.Embed(
            title="Download an area of pixelya",
            description="Here is an explaination on how to use this command without making the bot sending an error message :",
            url="https://www.pixelya.fun",
            color=discord.Color.from_rgb(173, 233, 230),
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        canvases = apime['canvases'].items()
        informations.add_field(name="Canvas", value=f"Here are the available canvases : {"; ".join([canvas[1]['title'] for canvas in canvases])}, with for respective IDs : {[canvas[0] for canvas in canvases]}", inline=False)

        informations.add_field(name="Coordinates", value = "Use `R` key in the canvas to pick coordinates. You need the Upper left corner (startx_starty) and the bottom right corner (endx_endy)", inline = False)

        informations.add_field(name = "Result", value = "The bot will send you the result. If it doesn't work and you have made no mistakes, please make a but report in the dedicated thread of this channel", inline = False)

        informations.set_author(name=self.bot.user.display_name, url = "https://github.com/Daeltam/PyfDownloadTool", icon_url=self.bot.user.avatar)

        informations.set_footer(text = "Informations about /area Download")

        return await interaction.response.send_message(embed=informations)

    @group.command(name = "download", description = "Sends the pixelya map between two coordinates in a file.")
    @app_commands.describe(maps = "Map from which you want to download the image")
    @app_commands.choices(maps=[
        app_commands.Choice(name="MiniWorld", value=1),
        app_commands.Choice(name="Graffiti", value=2),
        app_commands.Choice(name="MainWorld", value=4),
        ])
    async def download_area(self, interaction : discord.Interaction, maps : app_commands.Choice[int], startx_starty : str, endx_endy : str):
        global USER_AGENT
        USER_AGENT = "pyf areaDownload 1.0 " + maps.value + " " + startx_starty + " " + endx_endy
        print("downloadArea called")
        apime = await fetchMe()
        canvas_id = maps.value

        if canvas_id not in apime['canvases']:
            return await interaction.response.send_message("❌ Invalid canvas selected")
        canvas = apime['canvases'][canvas_id]

        parseCoords = validateCoorRange(startx_starty, endx_endy, canvas['size'])
        if (type(parseCoords) is str):
            return await interaction.response.send_message(parseCoords)
        else:
            x, y, w, h = parseCoords
            w = w - x + 1
            h = h - y + 1

        EnumColorPixelya.getColors(canvas)

        matrix = await get_area(canvas_id, canvas, x, y, w, h)
        # ENVOYER PROGRESS BY EDITING MESSAGE
        matrix.create_image()  # './output/'+filename) (filename should be optional if i read well)

        image = matrix.create_image # send PIL image
        # A completer avec main()
        return await interaction.response.send_message(f"👌 Your image is ready :", file = discord.File(fp=image, filename = "result.png"))

async def setup(bot):
    await bot.add_cog(areaDownload(bot))