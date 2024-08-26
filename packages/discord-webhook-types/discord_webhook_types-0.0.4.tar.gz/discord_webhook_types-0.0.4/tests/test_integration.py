import os
import unittest

import requests

from dwt.webhook import WebHook


class TestSendBasic(unittest.TestCase):
    def test_send_msg(self) -> None:
        webhook: WebHook = {
            "content": "Test Message",
            "username": "Ethan Rietz",
        }

        requests.post(
            f"https://discord.com/api/webhooks/{os.environ.get('DISCORD_WEBHOOK_ID_SLASH_TOKEN')}",
            json=webhook,
        )


if __name__ == "__main__":
    unittest.main()
