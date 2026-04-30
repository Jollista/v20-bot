from utils import *

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
        other_args = args[1:]
    except:
        return -1

    # parse args
    assign_diff = False
    for i in range(len(other_args)):
        arg = other_args[i]
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
            j = i+1
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
def r(args:list, prefix, id, ignore_wp_prompt=False):
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

    # if didn't arg wp and opted into wp prompts
    if not ignore_wp_prompt and not wp and query(id, "user data"):
        print("not ignoring wp prompt, didn't declare wp, and id found in user data")
        return "prompt"

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
    message:discord.Message = None
    action:str = None
    arg = None

    async def callback(self, interaction):

        print("interaction: ", interaction)
        initiator_id = self.message.author.id

        emb = discord.Embed()
        auth = self.message.author
        emb.set_author(name=auth.display_name, icon_url=auth.avatar)
        emb.color = get_color()

        # ignore responses not from initiator
        if interaction.user.id != initiator_id:
            await interaction.response.defer()
            return

        match self.action:
            case "prefix":
                print("prefix self.arg: `" + self.arg + "`")
                if self.arg != "":
                    update_prefix(self.arg, interaction.guild_id)
                    emb.description = "Prefix was changed to `" + self.arg + "`."
                else:
                    print("prefix not changed")
                    emb.description = "Prefix was not changed."
            case "wp":
                # get list of arguments for roll command input
                arg = self.arg.split(" ")
                
                # determine response based on confirmation buttons
                if self.id == 1:
                    arg.insert(1, "wp")
                    print("Yes!", arg)
                
                # output message
                output = r(arg, get_prefix(self.message.guild.id), -1, True)
                emb.title = output[0]
                emb.description = output[1]
            case _:
                pass

        # remove buttons and edit message
        v:discord.ui.View = self.view
        for item in v.children:
            v.remove_item(item)

        await interaction.response.edit_message(embed=emb, view=v)