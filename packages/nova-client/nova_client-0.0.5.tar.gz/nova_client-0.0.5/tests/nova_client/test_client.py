import os
import unittest
from unittest import IsolatedAsyncioTestCase
from nova_client.client import NOVAClient
from dotenv import load_dotenv

from nova_client.models.responses import UsageEvent

load_dotenv()
NOVA_API_KEY = os.getenv("NOVA_API_KEY")
if NOVA_API_KEY is None:
    raise ValueError("NOVA_API_KEY must be defined in the .env file")
BOT_ID = os.getenv("BOT_ID")
if BOT_ID is None:
    raise ValueError("BOT_ID must be defined in the .env file")


class TestCreateSession(IsolatedAsyncioTestCase):
    async def test_create_session(self):
        client = NOVAClient(api_key=NOVA_API_KEY)
        session = await client.client_sessions.create_session(bot_id=BOT_ID)
        token = session.session_token
        self.assertIsNotNone(token)


class TestSendMessage(IsolatedAsyncioTestCase):
    async def test_send_message(self):
        client = NOVAClient(api_key=NOVA_API_KEY)
        session = await client.client_sessions.create_session(bot_id=BOT_ID)

        stream = session.send_message("Hello World!")

        parts = []
        async for part in stream:
            parts.append(part)
        self.assertIsInstance(parts[-1], UsageEvent)


if __name__ == "__main__":
    unittest.main()
