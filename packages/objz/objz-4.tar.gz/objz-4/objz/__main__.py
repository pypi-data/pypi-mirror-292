# This file is placed in the Public Domain.
#
# pylint: disable=R1710,C0413,C0103,E1121


"""OBJZ - objects shell

objz  <cmd> [key=val] [key==val]

OPTIONS

    -c     start console
    -h     show help
    -v     use verbose

COMMANDS
    
    $ objz cmd
    md,dne,err,log,mod,tdo,thr,upt

"""


import sys
import time


from objz import Cfg, Console, Logging, cmnd, debug, parse, scan, wrap
from objz import modules


def main():
    "main"
    parse(Cfg, " ".join(sys.argv[1:]))
    Cfg.mod = ",".join(dir(modules))
    if "h" in Cfg.opts:
        print(__doc__)
        return
    if "v" in Cfg.opts:
        Logging.out = print
        dte = " ".join(time.ctime(time.time()).replace("  ", " ").split()[1:])
        debug(f"{dte} {Cfg.name.upper()} {Cfg.opts.upper()} {Cfg.mod.upper()}".replace("  ", " "))
    scan(Cfg.mod, modules)
    csl = Console()
    if "c" in Cfg.opts:
        csl.loop()
    if Cfg.otxt:
        return cmnd(Cfg.otxt)


if __name__ == "__main__":
    wrap(main)
