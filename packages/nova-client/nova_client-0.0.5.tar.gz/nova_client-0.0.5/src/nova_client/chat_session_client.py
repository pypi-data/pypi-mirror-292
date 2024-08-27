import json
from typing import Literal, AsyncIterator

from pydantic import TypeAdapter

from nova_client.adapter import AsyncHTTPClient
from nova_client.models.requests import (
    SessionUser,
    CreateSessionRequest,
    CompletionSourceEvent,
    RequestContentPart,
)
from nova_client.models.responses import ReceivedEvent, ChatSession, ChatSessionResponse


class ChatSessionClient(AsyncHTTPClient):
    def __init__(self, base_url: str, session_id: str, session_token: str):
        self.__base_url = base_url
        self.__session_id = session_id
        self.__session_token = session_token

    def _base_url(self) -> str:
        return self.__base_url

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.session_token}",
        }

    @property
    def session_id(self) -> str:
        return self.__session_id

    @property
    def session_token(self) -> str:
        return self.__session_token

    async def get_session(self) -> ChatSession:
        return await self._get("/client_session", response_model=ChatSession)

    async def get_asset(self, asset_id: str) -> bytes:
        async with self._client() as client:
            async with client.get(f"/client_session/assets/{asset_id}") as resp:
                await self._raise_for_status(resp)
                return await resp.read()

    def send_message(self, content: str | list[RequestContentPart]) -> AsyncIterator[ReceivedEvent]:
        return self.__stream_completion_from_event(
            {
                "type": "message",
                "content": content,
            }
        )

    def send_function_result(
        self, tool_call_id: str, result: str | list[RequestContentPart]
    ) -> AsyncIterator[ReceivedEvent]:
        return self.__stream_completion_from_event(
            {
                "type": "function_result",
                "tool_call_id": tool_call_id,
                "result": result,
            }
        )

    def send_multiple_function_results(
        self, results: dict[str, str | list[RequestContentPart]]
    ) -> AsyncIterator[ReceivedEvent]:
        return self.__stream_completion_from_event(
            {
                "type": "multiple_function_results",
                "results": results,
            }
        )

    async def __stream_completion_from_event(self, event: CompletionSourceEvent):
        def parse_event(e: dict[str, str]) -> ReceivedEvent:
            event_type = e.pop("event")
            event_data = json.loads(e.pop("data"))
            adapter = TypeAdapter(ReceivedEvent)
            return adapter.validate_python({"type": event_type, **event_data})

        async with self._client() as client:
            async with client.post(
                "/client_session/infer_completion",
                json=event,
                headers={"Accept": "text/event-stream"},
            ) as resp:
                await self._raise_for_status(resp)

                async for rec_ev in self._parse_sse_response(resp):
                    yield parse_event(rec_ev)


class SessionManagementClient(AsyncHTTPClient):
    def __init__(self, api_key: str, base_url: str):
        self.__api_key = api_key
        self.__base_url = base_url

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.__api_key}",
        }

    def _base_url(self) -> str:
        return self.__base_url

    async def create_session(
        self,
        bot_id: str,
        enabled_device_actions: list[str] | None = None,
        user: SessionUser | None = None,
        editable: Literal["none", "user_messages", "all_messages"] = "none",
        meta: dict[str, str] | None = None,
    ):
        if user is None:
            user = {"organization_user_id": "anonymous"}

        if meta is None:
            meta = {}

        if enabled_device_actions is None:
            enabled_device_actions = []

        request: CreateSessionRequest = {
            "bot_id": bot_id,
            "enabled_device_actions": enabled_device_actions,
            "user": user,
            "editable": editable,
            "meta": meta,
        }

        session_resp: ChatSessionResponse = await self._post(
            "/m2m/client_sessions", request, response_model=ChatSessionResponse
        )

        return ChatSessionClient(
            base_url=self.__base_url,
            session_id=session_resp.session.session_id,
            session_token=session_resp.token,
        )

    async def get_session(self, session_id: str):
        response: ChatSessionResponse = await self._post(
            f"/m2m/client_sessions/{session_id}/renew", {}, response_model=ChatSessionResponse
        )

        return ChatSessionClient(
            base_url=self.__base_url,
            session_id=response.session.session_id,
            session_token=response.token,
        )

    async def delete_session(self, session_id: str):
        await self._delete(f"/m2m/client_sessions/{session_id}")
