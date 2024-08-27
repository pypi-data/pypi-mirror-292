from nova_client.chat_session_client import SessionManagementClient


class NOVAClient:
    def __init__(self, api_key: str, base_url: str | None = None):
        self.__api_key = api_key
        self.__base_url = base_url or "https://api-core.nova-ai.de/"

    async def ping(self):
        pass

    @property
    def client_sessions(self):
        return SessionManagementClient(self.__api_key, self.__base_url)
