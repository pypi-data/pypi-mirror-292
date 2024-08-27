# This file is placed in the Public Domain.
# pylint: disable=R0902,R0903


"default values"


class Default:

    "Default"

    def __getattr__(self, key):
        return self.__dict__.get(key, "")


def __dir__():
    return (
        'Default',
    )
