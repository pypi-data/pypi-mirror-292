#!/usr/bin/env python3

import sys


class SomUtil:
    history_limit = 5

    def __init__(self):
        pass

    @staticmethod
    def print(msg_without_nl_cr):
        sys.stdout.write("{0}\n\r".format(msg_without_nl_cr))
        sys.stdout.flush()

    @staticmethod
    def rq(string):
        if string == "":
            return string
        return string.replace("'", "''")

    @staticmethod
    def get_ltr():
        return "\u202A"

    @staticmethod
    def get_rtl():
        return "\u202B"

    @staticmethod
    def get_arabic_tatweel():
        return "\u0640"
