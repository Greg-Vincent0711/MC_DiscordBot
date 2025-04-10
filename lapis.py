import os
import discord
from discord.ext.commands import CommandNotFound, MissingRequiredArgument, BadArgument
from discord import Color
from utils import *
from docstrings import *
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from embed import *
from discord.ext import commands
from db import *

'''
TODO
s3 operations
Map integration with Dynmap, Chunkbase maybe
'''

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# cooldown params
RATE = 1
PER: float = 5

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="saveLocation", help=saveDocString)
async def saveLocation(ctx, locationName: str, locationCoords: str): 
    coordCheck = isCorrectCoordFormat(locationCoords)
    nameCheck = isCorrectLength(locationName)

    # both of these fns return error messages if not True
    if nameCheck is not True:
        await ctx.send(f"{nameCheck}")
    
    elif coordCheck is not True:
        await ctx.send(f"{coordCheck}")
    else:
        try:
            save_location(ctx.author.id, locationName, locationCoords)
            await ctx.send(embed=makeEmbed(f"New location {locationName} has been saved.", 
                                        Color.blue(), ctx, f"Coordinates: {format_coords(locationCoords)}"))
        except Exception as e:
            await ctx.send(embed=makeErrorEmbed("Error interacting with DB.", {e}))


@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="getLocation", help=getDocString)
async def getLocation(ctx, locationName: str):
    nameCheck = isCorrectLength(locationName)
    if nameCheck is not True:
        await ctx.send(f"{nameCheck}")
    else:
        try:  
            retrieved_coordinates = get_location(ctx.author.id, locationName)
            if retrieved_coordinates:
                await ctx.send(embed=makeEmbed(f"Found coordinates: for location '{locationName}'", 
                                                Color.blue(), ctx, retrieved_coordinates))
            else:
                await ctx.send(embed=makeErrorEmbed(f"No location named {locationName} has been found. Check your spelling."))
        except ClientError as e:
            await ctx.send(embed=makeErrorEmbed(f'Error getting coordinates for your location, try again later.', {e}))

        

@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="deleteLocation", help=deleteDocString)
async def deleteLocation(ctx, locationName: str):
    nameCheck = isCorrectLength(locationName)
    if nameCheck is not True:
        await ctx.send(f"{nameCheck}")
    else:
        try:
            deleted_coords = delete_location(ctx.author.id, locationName)
            if deleted_coords != None:
                await ctx.send(embed=makeEmbed(f"{locationName} has been deleted.",
                                                Color.blue(), ctx, f"Coords were: {deleted_coords}"))
            else:
                await ctx.send(embed=makeErrorEmbed(f"No matching location found for '{locationName}'. Call !list to see all locations you have created."))
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            await ctx.send(makeErrorEmbed(f'Error deleting {locationName}.', error_message))
            

@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="updateLocation", help=updateDocString)
async def updateLocation(ctx, locationName, newCoords):
    nameLengthVar = isCorrectLength(locationName)
    if nameLengthVar is not True:
        await ctx.send(f"{nameLengthVar}")
    else:
        try:
            response = update_location(ctx.author.id, locationName, newCoords)
            if response != None:
                await ctx.send(embed=makeEmbed(f"{locationName} updated successfully. New coordinates: {response}", Color.blue(), ctx))
            else:
                await ctx.send(embed=makeErrorEmbed(f"Error updating {locationName}"))
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            await ctx.send(embed=makeErrorEmbed(f'Error updating {locationName}', error_message))

@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="list", help=listDocString)
async def list_locations_for_player(ctx):
    try:
        player_locations = list_locations(ctx.author.id)
        if len(player_locations) >= 1:
            await ctx.send(embed=makeEmbed(f"All locations created by {ctx.author.display_name}", Color.blue(),
                                           ctx, player_locations))
        else:
            await ctx.send(embed=makeErrorEmbed("You have no locations to list."))
    except ClientError as e:
        await ctx.send(embed=makeErrorEmbed("Try this command again later.", {e}))
        
@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="helpme", help=helpDocString)
async def help_command(ctx):
    help_text = (
        "Commands are always in one of these forms:\n"
        "`!command location_name 'x y z'`\n"
        "`!command location_name`\n"
        "`!command`\n\n"
    )
    for command in bot.commands:
        if not command.hidden:
            help_text += f"**!{command.name}** - {command.help or 'No description provided.'}\n"

    await ctx.send(embed=makeEmbed("Lapis' Commands", Color.blue(), ctx, help_text))

@commands.cooldown(RATE, PER, commands.BucketType.user)
@bot.command(name="addImage", help=addImgDocString)
async def addImage(ctx, location_name):
    # Make sure an attachment exists
    if not ctx.message.attachments:
        await ctx.send("Please attach an image with your command.")
        return

    message = ctx.message  # get the full message object
    author_id = ctx.author.id

    result = await save_image_url(author_id, location_name, message)

    if result:
        await ctx.send(result)
    else:
        await ctx.send("Something went wrong while saving your image.")
    


@bot.command(name="logout", help="Logs the bot out of Discord. Bot owner only.")
@commands.is_owner()
async def logout(ctx):
    await ctx.send("Logging out...")
    await bot.close()
    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(makeErrorEmbed("That command doesn't exist. Send `!helpme` for a list of all commands."))
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(makeErrorEmbed("You're missing a required argument. Check `!helpme` for the proper format."))
    elif isinstance(error, BadArgument):
        await ctx.send(makeErrorEmbed("Invalid argument type. Please check your input."))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=makeErrorEmbed("Wait before sending this command again.", f"Try again in {round(error.retry_after, 1)}s"))
    else:
        await ctx.send(embed=makeErrorEmbed("An error occured", error))
        
bot.run(TOKEN)
    
