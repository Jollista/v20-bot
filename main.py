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

        title = ""
        desc = "description"

        match command:
            case 'r':
                output = commands.r(args)
                title = output[0]
                desc = output[1]
            case _:
                title = "No command \"" + command + "\" found"

        emb = discord.Embed()
        emb.title = title
        emb.description = desc
        await message.channel.send(embed=emb)

client.run(os.getenv("TOKEN"))