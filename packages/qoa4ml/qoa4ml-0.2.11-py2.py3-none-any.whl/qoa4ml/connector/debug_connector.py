import json

from devtools import debug

from .base_connector import BaseConnector


class DebugConnector(BaseConnector):
    def __init__(self):
        pass

    def send_report(self, body_message: str):
        debug(json.loads(body_message))
