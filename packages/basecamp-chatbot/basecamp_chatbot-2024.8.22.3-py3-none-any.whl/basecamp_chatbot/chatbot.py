import logging

from basecamp_chatbot.rest_adapter import RestAdapter
from pathlib import Path


class Chatbot:
    def __init__(
        self,
        bot_url: str,
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        self._rest_adapter = RestAdapter(bot_url, ssl_verify, logger)

    def post_string(self, message: str):
        self._rest_adapter.post({"content": message})

    def post_file(self, filepath: Path):
        with open(filepath, "r") as file:
            message = file.read()
            self.post_string(message)
