from utils import *
import time

# Helper function for $r command
# parses through args
def parse_args(args:list):
    dots = 1
    diff = 6
    explode = False
    wp = False
    ignore_ones = False
    message = ""

    print("args:", args)

    if len(args) == 0 or args[0] == "help":
        return 0

    # get dots to roll
    try:
        dots = int(args[0])
        args.pop(0)
    except:
        return -1

    # parse args
    assign_diff = False
    for i in range(len(args)):
        arg = args[i]
        print("arg:", arg)
        if assign_diff:
            diff = int(arg)
            assign_diff = False
        elif arg == "-diff":
            assign_diff = True
        elif arg == "e":
            explode = True
        elif arg == "wp":
            wp = True
        elif arg == "i":
            ignore_ones = True
        else:
            # can't parse arg
            j = i
            while j < len(args):
                message += args[j] + " "
                j += 1
            return (dots, diff, explode, wp, ignore_ones, message)
    
    return (dots, diff, explode, wp, ignore_ones, message)

# Helper function for $r command
# Simulates all dice rolling logic
def get_rolls(dots:int, explode:bool):
    rolls = []
    tens = 0
    
    i = 0
    while i < dots:
        r = roll(10)
        rolls.append(r)
        if r == 10:
            tens += 1
        i += 1

    while explode and i < dots + tens:
        r = roll(10)
        rolls.append(r)
        if r == 10:
            tens += 1
        i += 1
    
    return (rolls, tens)

# Helper function for $r command
# counts successes and formats dice output
def count_successes(dots:int, diff:int, explode:bool, wp:bool, ignore_ones:bool, rolls:list):
    succ = 1 if wp else 0
    
    desc = str(dots) + "d10 ("
    print()
    for i in range(len(rolls)):
        if i != 0:
            desc += ", "

        c = rolls[i]
        if rolls[i] >= diff:
            succ += 1

        if rolls[i] == 1:
            c = "**" + str(rolls[i]) + "**"
            if not ignore_ones:
                succ -= 1
        elif rolls[i] == 10:
            if not explode:
                c = "**" + str(rolls[i]) + "**"
            if explode:
                c = "**" + str(rolls[i]) + "!**"
        elif rolls[i] < diff:
            c = "~~" + str(rolls[i]) + "~~"

        desc += str(c)
    desc += ")"

    return (succ, desc)

### $r command ###
# Rolls dice and formats output nicely.
def r(args:list, prefix):
    title = ""
    desc = "description"
    
    # parse args
    parsed_args = parse_args(args)

    # Output couldn't parse error
    if parsed_args == -1: # error
        title = "Couldn't parse arguments."
        desc = "Something went wrong with the following command:\n"
        raw_args = ""
        for arg in args:
            raw_args += arg
        desc += "`$r " + raw_args + "`"
        return (title, desc)
    elif parsed_args == 0: # help
        title = ""
        desc = "**" + prefix + "r [number of dice] [args]**\n" \
        "Rolls a given number of dice at a default difficulty of 6.\n" \
        "\nExample: `" + prefix + "r 10`\n" \
        "\n**Advanced Options**\n" \
        "`-diff X` - sets the difficulty for the roll to X.\n" \
        "`e` - automatically explode all 10s.\n" \
        "`wp` - spend willpower, add one success automatically.\n" \
        "`i` - ignore 1s.\n" \
        "Additionally, any quoted string will be appended to the title.\n" \
        "\nExample: `" + prefix + "r 10 -diff 8 e wp i 'hello world'`"
        return (title, desc)

    dots = parsed_args[0]
    diff = parsed_args[1]
    explode = parsed_args[2]
    wp = parsed_args[3]
    ignore_ones = parsed_args[4]
    message = parsed_args[5]

    # get rolls
    result = get_rolls(dots, explode)
    rolls = result[0]
    tens = result[1]

    # format output
    result = count_successes(dots, diff, explode, wp, ignore_ones, rolls)
    succ = result[0]
    desc = result[1]

    # final touches
    if tens > 0:
        desc += "\n\n-# *" + str(succ + tens) + " if specialization applies*"
    
    wp_msg = ", with willpower" if wp else ""
    ig_msg = ", ignoring 1s" if ignore_ones else ""
    title = str(succ) + " successes" + wp_msg + ig_msg + " (diff " + str(diff) + ")"
    
    if message != "":
        title += ", " + message

    return (title, desc)

# prompt user to change prefix based on args
def prompt_prefix(args:list, prefix):
    """
    Initiate prefix change.

    Returns
    -------
    [0]
        The description to be output
    [1]
        The new prefix, empty string if none
    """

    if len(args) == 0 or args[0] == "help": # output help
        return ("**" + prefix + "prefix [new prefix]**\n"
        "Change the prefix from `" + prefix + "` to any other single character.", "")
    elif len(args[0]) == 1: # update prefix?
        return ("Change prefix from `" + prefix + "` to `" + args[0] + "`?", args[0])
    elif args[0] == prefix: # prefix already set to arg
        return ("Prefix is already `" + prefix + "`", "")

# A button class used for interactions exclusive to 
class ConfirmationButton(discord.ui.Button):
    async def callback(self, interaction):

        print("interaction: ", interaction)
        print("custom id:", interaction.custom_id)

        custom_ids = interaction.custom_id.split(":")
        initiator_id = int(custom_ids[0])
        action = custom_ids[1]
        arg = custom_ids[2]

        # ignore responses not from initiator
        if interaction.user.id != initiator_id:
            await interaction.response.defer()
            return

        match action:
            case "prefix":
                if arg != "":
                    update_prefix(arg, interaction.guild_id)
                pass
            case _:
                pass

        v:discord.ui.View = self.view

        for item in v.children:
            item.disabled = True

        await interaction.response.edit_message(view=v)