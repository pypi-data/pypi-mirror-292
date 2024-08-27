# This file is placed in the Public Domain.
# pylint: disable=W0718


"main"


import sys
import termios


from .console import Console
from .cmds    import Commands, command
from .event   import Event
from .utils   import spl, skip


def cmnd(txt):
    "do a command using the provided output function."
    if not txt:
        return None
    cli = Console()
    evn = Event()
    evn.txt = txt
    command(cli, evn)
    evn.wait()
    return evn


def scan(modstr, *pkgs, disable=""):
    "scan modules for commands and classes"
    mds = []
    for modname in spl(modstr):
        if skip(modname, disable):
            continue
        for pkg in pkgs:
            module = getattr(pkg, modname, None)
            if not module:
                continue
            Commands.scan(module)
    return mds


def wrap(func):
    "restore console."
    old2 = None
    try:
        old2 = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")
    finally:
        if old2:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old2)


def __dir__():
    return (
        'cmnd',
        'init',
        'scan',
        'wrap'
    )
