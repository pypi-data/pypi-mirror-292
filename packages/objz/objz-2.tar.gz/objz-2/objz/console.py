# This file is placed in the Public Domain.


"console"


import time


from objr import Reactor


from objz.event import Event
from objz.cmds  import command


class Console(Reactor):

    "Console"

    def __init__(self, prompt="> "):
        Reactor.__init__(self)
        self.prompt = prompt
        self.register("command", command)

    def announce(self, txt):
        "echo text"

    def callback(self, evt):
        "wait for callback."
        Reactor.callback(self, evt)
        evt.wait()

    def forever(self):
        "run forever."
        while True:
            time.sleep(1.0)

    def poll(self):
        "poll console and create event."
        evt = Event()
        evt.txt = input(self.prompt)
        evt.type = "command"
        return evt

    def raw(self, txt):
        "echo text."
        print(txt)

    def show(self, evt):
        "show results."
        for text in evt.result:
            self.raw(text)


def __dir__():
    return (
        'Console',
    )
