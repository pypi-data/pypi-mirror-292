# This file is placed in the Public Domain.
# pylint: disable=C0413,R0903,R0912,W0105,W0201,W0611,W0718


"runtime"


import inspect
import os
import sys
import termios
import time


sys.path.insert(0, os.getcwd())


from objx.default import Default
from objx.object  import Object, keys
from objx.persist import Persist
from objx.utility import skip, spl


from objx import mods


Cfg         = Default()
Cfg.name    = Object.__module__.rsplit(".", maxsplit=1)[-2]
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr


class Event(Default):

    "Result"

    def __init__(self):
        Default.__init__(self)
        self.result  = []
        self.txt     = ""

    def reply(self, txt):
        "add text to the result"
        self.result.append(txt)


class Commands:

    "Commands"

    cmds = Object()

    @staticmethod
    def add(func):
        "add command."
        setattr(Commands.cmds, func.__name__, func)

    @staticmethod
    def scan(mod) -> None:
        "scan module for commands."
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)


class Console:

    def loop(self):
        while True:
            evt = self.poll()
            command(evt)

    def poll(self):
        "poll console and create event."
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


def command(evt):
    "check for and run a command."
    parse(evt)
    func = getattr(Commands.cmds, evt.cmd, None)
    if func:
        func(evt)
        for text in evt.result:
            print(text)


def parse(obj, txt=None):
    "parse a string for a command."
    args = []
    _nr = -1
    obj.otxt = txt or obj.otxt or obj.txt
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            if not obj.gets:
                obj.gets = Default()
            if key in obj.gets:
                val = getattr(obj.gets, key)
                value = val + "," + value
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            if not obj.sets:
                obj.sets = Default()
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


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
            Persist.scan(module)
    return mds


def wrap(func):
    "reset console."
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


def wrapped():
    wrap(main)

def cmd(event):
    "list commands."
    event.reply(",".join(sorted(keys(Commands.cmds))))


def main():
    Commands.add(cmd)
    txt = " ".join(sys.argv[1:])
    parse(Cfg, txt)
    if Cfg.sets and Cfg.sets.wdr:
        Persist.workdir = Cfg.wdr = Cfg.sets.wdr
    Cfg.mod = ",".join(dir(mods))
    scan(Cfg.mod, mods)
    if "c" in Cfg.opts:
        console = Console()
        console.loop()
        return
    result = Event()
    result.txt = txt
    command(result)


if __name__ == "__main__":
    wrapped()

