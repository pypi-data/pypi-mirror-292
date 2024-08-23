import logging
from typing import Dict

import requests
import requests.packages

from basecamp_chatbot.exceptions import BasecampApiException
from basecamp_chatbot.models import Result


class RestAdapter:
    def __init__(
        self,
        bot_url: str,
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        """
        :param bot_url: URL to POST updates to. See README.md for more details
        :param ssl_verify: Normally set to True, but if having SSL/TLS cert validation issues, can turn off with False
        :param logger: (optional) If your app has a logger, pass it in here
        """
        self.url = bot_url
        self._ssl_verify = ssl_verify
        self._logger = logger or logging.getLogger(__name__)
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()

    def post(self, data: Dict) -> Result:
        log_line_pre = f"url={self.url}"
        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(
                method="POST",
                url=self.url,
                verify=self._ssl_verify,
                json=data,
            )
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise BasecampApiException("Request failed") from e
        # Deserialize JSON output to Python object, or return failed Result on exception

        is_success = response.status_code == 201
        log_line = f"{log_line_pre}, success={is_success}, status_code={response.status_code}, message={response.reason}"

        if is_success:
            self._logger.debug(msg=log_line)
            return Result(response.status_code, message=response.reason)
        self._logger.error(msg=log_line)
        raise BasecampApiException(f"{response.status_code}: {response.reason}")
