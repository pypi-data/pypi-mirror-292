# This file is placed in the Public Domain.
# pylint: disable=R0903,W0201


"runtime"


import os
import time


from .default import Default


STARTTIME   = time.time()


Cfg         = Default()
Cfg.name    = __file__.rsplit(".", maxsplit=1)[-2]
Cfg.mod     = "cmd,mod,skl,srv,thr"
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")
