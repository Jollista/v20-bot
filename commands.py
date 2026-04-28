def r(args:list):
    title = ""
    desc = "description"

    # get dots to roll
    try:
        dots = int(args.pop(0))
    except:
        title = "Dots"

    # parse args
    for arg in args:
        pass

    return (title, desc)