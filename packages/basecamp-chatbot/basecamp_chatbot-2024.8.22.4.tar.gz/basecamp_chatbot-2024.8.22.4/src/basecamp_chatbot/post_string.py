#!/usr/bin/env python

"""
Post a string to the specified Basecamp chatbot

Usage:
  bc_post_from_str <bot_url> <message>
"""

from docopt import docopt
from basecamp_chatbot.chatbot import Chatbot


def _post_string(bot_url, message):
    bot = Chatbot(bot_url)
    bot.post_string(message)


def _main():
    args = docopt(__doc__)
    _post_string(args["<bot_url>"], args["<message>"])


if __name__ == "__main__":
    _main()
