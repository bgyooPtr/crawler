import os
import requests

from dotenv import load_dotenv

load_dotenv()


class LineNotify:
    """Line notify class"""

    def __init__(self) -> None:
        """Initialize line notify"""
        token = os.getenv("TOKEN")
        if not token:
            raise Exception("token is not defined")

        self.line_notify_url = "https://notify-api.line.me/api/notify"
        self.header = {"Authorization": "Bearer " + token}

    def send_msg(self, msg: str) -> None:
        """Send message to line notify"""
        data = {"message": msg}
        requests.post(self.line_notify_url, headers=self.header, data=data)
