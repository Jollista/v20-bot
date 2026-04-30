import os
from dotenv import load_dotenv
import discord
from utils import *
import commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


"""
Set up discord intents and events
"""

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message:discord.Message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    prefix = get_prefix(message.guild.id)
    if message.content.startswith(prefix):
        # split up command and args
        args = str(message.content).split()
        command = args.pop(0)[1:]

        # initialize embed information
        title = ""
        desc = "description"
        auth = message.author
        view = discord.ui.View()

        # find matching command if one exists
        match command:

            # roll command
            case 'r':
                output = commands.r(args, prefix)
                title = output[0]
                desc = output[1]

            # prefix command
            case 'prefix':
                # reject attempts to change prefix from non-server owners
                if message.guild.owner_id != message.author.id:
                    desc = "Must be server owner to change the prefix."

                else: # add confirmation message
                    output = commands.prompt_prefix(args, prefix)
                    desc = output[0]
                    new_pre = output[1]

                    if new_pre != "":
                        c_id = str(message.author.id) + ":prefix:"

                        yes_button = commands.ConfirmationButton(label="Yes", custom_id=c_id+new_pre)
                        no_button = commands.ConfirmationButton(label="No", custom_id=c_id)
                        view.add_item(yes_button)
                        view.add_item(no_button)
            case _:
                title = "No command \"" + command + "\" found"
                desc = "Here's a list of available commands:\n" \
                "\n`" + prefix + "r` - rolls a given number of dice"
                "\n`" + prefix + "prefix` - change this bot's prefix"

        emb = discord.Embed()
        emb.title = title
        emb.description = desc
        emb.set_author(name=auth.display_name, icon_url=auth.avatar)
        emb.color = get_color()

        await message.channel.send(embed=emb, view=view)

load_dotenv()
client.run(os.getenv("TOKEN"))