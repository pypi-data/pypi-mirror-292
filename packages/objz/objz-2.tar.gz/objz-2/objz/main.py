# This file is placed in the Public Domain.
# pylint: disable=W0718


"main"


import sys
import termios


from objr import errors, launch


from objz.console import Console
from objz.cmds    import Commands, command
from objz.event   import Event
from objz.utils   import spl, skip


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


def init(modstr, *pkgs, disable=None):
    "scan modules for commands and classes"
    thrs = []
    for mod in spl(modstr):
        if disable and mod in spl(disable):
            continue
        for pkg in pkgs:
            modi = getattr(pkg, mod, None)
            if not modi:
                continue
            if "init" not in dir(modi):
                continue
            thrs.append(launch(modi.init))
            break
    return thrs


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
    errors()


def __dir__():
    return (
        'cmnd',
        'init',
        'scan',
        'wrap'
    )
