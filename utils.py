import random
from discord import Color as color
import discord

def get_prefix():
    return prefix

def update_prefix(new_pre:str, guild_id):
    prefix = new_pre
    print("prefix updated!\n" + "new_pre:", new_pre, "\nguild id:", guild_id)

def roll(number:int, size:int):
    results = []

    for i in range(number):
        results.append(random.randint(1, size))
    
    return results

def roll(size:int):
    return random.randint(1, size)

colors = [
        color.dark_blue(), color.dark_embed(), color.dark_gold(), color.dark_green(), color.dark_grey(), color.dark_magenta(),
        color.dark_orange(), color.dark_purple(), color.dark_red(), color.dark_teal(), color.dark_theme(), color.darker_grey()
    ]
def get_color():
    return colors[random.randint(0, len(colors)-1)]