import unittest

from dwt.allowed_mention import AllowedMention
from dwt.webhook import WebHook


class TestTypes(unittest.TestCase):
    def test_something(self) -> None:
        webhook: WebHook = {
            "content": "hello world",
            "username": "Ethan Rietz",
            "avatar_url": "www.test.com",
            "tts": True,
            "embeds": [],
            "allowed_mentions": [],
            "components": [],
            "payload_json": "payload",
            "attachments": [],
            # "flags": [],
        }

        self.assertEqual(webhook["content"], "hello world")
        self.assertEqual(webhook["username"], "Ethan Rietz")


if __name__ == "__main__":
    unittest.main()
