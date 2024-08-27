# This file is placed in the Public Domain.


"list of commands"


from objz import Commands


def cmd(event):
    "list commands."
    event.reply(",".join(sorted(Commands.cmds.keys())))
