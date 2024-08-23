#!/usr/bin/env python

"""
Post the contents of a file to the specified Basecamp chatbot

Usage:
  bc_post_from_file <bot_url> <content_file>
"""

from pathlib import Path

from docopt import docopt
from basecamp_chatbot.chatbot import Chatbot


def _post_file(bot_url, content_file):
    bot = Chatbot(bot_url)
    bot.post_file(Path(content_file))


def _main():
    args = docopt(__doc__)
    _post_file(args["<bot_url>"], args["<content_file>"])


if __name__ == "__main__":
    _main()
