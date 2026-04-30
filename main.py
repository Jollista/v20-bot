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
                output = commands.r(args, prefix, auth.id)
                print(output)
                print(type(output) == str)

                if type(output) != str:
                    title = output[0]
                    desc = output[1]

                else:
                    print("r output is str")
                    desc = "Would you like to spend willpower for +1 success?"

                    str_args = ""
                    for arg in args:
                        str_args += arg + " "

                    yes_button = commands.ConfirmationButton(label="Yes", id=1)
                    yes_button.message = message
                    yes_button.action = "wp"
                    yes_button.arg = str_args
                    no_button = commands.ConfirmationButton(label="No", id=0)
                    no_button.message = message
                    no_button.action = "wp"
                    no_button.arg = str_args
                    view.add_item(yes_button)
                    view.add_item(no_button)

            # willpower command
            case 'wp':
                user = query(auth.id, "user data")

                if not user: # no entry for user exists in user data
                    # add them to database
                    try:
                        insert({"_id":auth.id, "wp":True}, "user data")
                        desc = "Opted **into** willpower prompts!"
                    except:
                        desc = "Couldn't add user to database."

                else: # user exists
                    try:
                        remove(auth.id, "user data")
                        desc = "Opted **out** of willpower prompts!"
                    except:
                        desc = "Couldn't remove user from database."

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
                        yes_button = commands.ConfirmationButton(label="Yes")
                        yes_button.message = message
                        yes_button.action = "prefix"
                        yes_button.arg = new_pre
                        no_button = commands.ConfirmationButton(label="No")
                        no_button.message = message
                        no_button.action = "prefix"
                        no_button.arg = ""
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