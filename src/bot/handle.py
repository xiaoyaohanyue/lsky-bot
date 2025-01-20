import logging
import textwrap

logger = logging.getLogger(__name__)


class BotHandle():
    def __init__(self, client):
        self.client = client

    async def get_id(self, username):
        id = await self.client.get_peer_id(username)
        return id