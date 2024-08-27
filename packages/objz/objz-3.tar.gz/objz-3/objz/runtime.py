# This file is placed in the Public Domain.
# pylint: disable=R0903,W0201

"runtime"


import getpass
import os
import time


from objx import Default


STARTTIME   = time.time()


class Config(Default):

    "configuration"


Cfg         = Config()
Cfg.name    = Config.__module__.rsplit(".", maxsplit=1)[-2]
Cfg.user    = getpass.getuser()
Cfg.mod     = "cmd,skl,req,srv"
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")
