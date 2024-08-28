# This file is placed in the Public Domain.
# pylint: disable=C0413,W0212,E0401


"main"


import os
import readline
import sys
import termios


sys.path.insert(0, os.getcwd())


from .config  import Config
from .console import Console
from .errors  import errors
from .persist import Persist, skel
from .main    import cmnd, enable, init, scan
from .parse   import parse
from .utils   import forever, modnames


from . import modules


if os.path.exists("mods"):
    import mods as MODS
else:
    MODS = None


Cfg         = Config()
Cfg.name    = Config.__module__.split(".")[-2]
Cfg.mod     = "cmd,mod,thr,err"
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr


def wrap(func):
    "reset terminal."
    old3 = None
    try:
        old3 = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")
    finally:
        if old3:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old3)
    errors()


def main():
    "main"
    parse(Cfg, " ".join(sys.argv[1:]))
    Cfg.dis = Cfg.sets.dis
    if "a" in Cfg.opts:
        Cfg.mod += ",".join(modnames(modules, MODS))
    readline.redisplay()
    enable(print)
    skel()
    scan(Cfg.mod, modules, MODS)
    csl = Console(print, input)
    if "i" in Cfg.opts:
        init(Cfg.mod, modules, MODS)
    csl.start()
    cmnd(Cfg.otxt, print)
    forever()


def wrapped():
    "wrap main function."
    wrap(main)


if __name__ == "__main__":
    wrapped()
