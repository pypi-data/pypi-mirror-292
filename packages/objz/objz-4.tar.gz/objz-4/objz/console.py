# This file is placed in the Public Domain.


"console"


import _thread


from .event import Event
from .cmds  import command


class Console:

    "Console"

    def announce(self, txt):
        "echo text"

    def loop(self):
        "proces events until interrupted."
        while True:
            try:
                evt = self.poll()
                command(self, evt)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        "poll console and create event."
        evt      = Event()
        evt.txt  = input("> ")
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
