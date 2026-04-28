import os
import discord
from utils import *
import commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

prefix = '$'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith(prefix):
        # split up command and args
        args = str(message.content).split()
        command = args.pop(0)[1:]

        # initialize embed information
        title = ""
        desc = "description"
        auth = message.author

        # find matching command if one exists
        match command:
            case 'r':
                output = commands.r(args)
                title = output[0]
                desc = output[1]
            case _:
                title = "No command \"" + command + "\" found"
                desc = "Here's a list of available commands:\n" \
                "\n`$r` - rolls a given number of dice"

        emb = discord.Embed()
        emb.title = title
        emb.description = desc
        emb.set_author(name=auth.display_name, icon_url=auth.avatar)
        emb.color = get_color()
        await message.channel.send(embed=emb)

client.run(os.getenv("TOKEN"))