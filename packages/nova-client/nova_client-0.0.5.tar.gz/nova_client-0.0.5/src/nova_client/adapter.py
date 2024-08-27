from abc import ABC
from typing import Any, AsyncIterator

import aiohttp
from pydantic import TypeAdapter


class NOVAClientException(Exception):
    def __init__(self, code: str, description: str, status: int):
        self.__code = code
        self.__description = description
        self.__status = status
        super().__init__(f"NOVA API Error: {code} - {description}")

    @property
    def code(self) -> str:
        return self.__code

    @property
    def description(self) -> str:
        return self.__description

    @property
    def status(self) -> int:
        return self.__status


class AsyncHTTPClient(ABC):
    def _headers(self) -> dict[str, str]:
        return {}

    def _base_url(self) -> str:
        return "https://api-core.nova-ai.de/"

    def _client(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            base_url=self._base_url(),
            headers=self._headers(),
        )

    async def _raise_for_status(self, response: aiohttp.ClientResponse):
        if 200 <= response.status <= 299:
            return

        body = await response.json()

        raise NOVAClientException(
            code=body.get("detail", {}).get("code", "unknown") if isinstance(body.get("detail"), dict) else "unknown",
            description=(
                body.get("detail", {}).get("message", "unknown") if isinstance(body.get("detail"), dict) else "unknown"
            ),
            status=response.status,
        )

    async def _get(self, url: str, response_model: type[Any] | None = None) -> Any:
        async with self._client() as client:
            async with client.get(url) as resp:
                await self._raise_for_status(resp)
                result = await resp.json()

        if response_model is not None:
            adapter = TypeAdapter(response_model)
            return adapter.validate_python(result)

        return result

    async def _post(self, url: str, data: dict[str, Any], response_model: type[Any] | None = None) -> Any:
        async with self._client() as client:
            async with client.post(
                url,
                json=data,
            ) as resp:
                await self._raise_for_status(resp)
                result = await resp.json()

        if response_model is not None:
            adapter = TypeAdapter(response_model)
            return adapter.validate_python(result)

        return result

    async def _put(self, url: str, data: dict[str, Any], response_model: type[Any] | None = None) -> Any:
        async with self._client() as client:
            async with client.put(
                url,
                json=data,
            ) as resp:
                await self._raise_for_status(resp)
                result = await resp.json()

        if response_model is not None:
            adapter = TypeAdapter(response_model)
            return adapter.validate_python(result)

        return result

    async def _delete(self, url: str, response_model: type[Any] | None = None) -> Any:
        async with self._client() as client:
            async with client.delete(url) as resp:
                await self._raise_for_status(resp)
                result = await resp.json()

        if response_model is not None:
            adapter = TypeAdapter(response_model)
            return adapter.validate_python(result)

        return result

    async def _patch(self, url: str, data: dict[str, Any], response_model: type[Any] | None = None) -> Any:
        async with self._client() as client:
            async with client.patch(
                url,
                json=data,
            ) as resp:
                await self._raise_for_status(resp)
                result = await resp.json()

        if response_model is not None:
            adapter = TypeAdapter(response_model)
            return adapter.validate_python(result)

        return result

    async def _parse_sse_response(self, response: aiohttp.ClientResponse) -> AsyncIterator[dict]:
        event: dict = {}

        async for line in response.content:
            # Decode bytes to string
            line = line.decode().strip()
            if line == "":
                # End of an event
                if event:
                    yield event
                    event = {}
            elif line.startswith(":"):
                # This line is a comment, ignore it
                continue
            else:
                # Process the line; it should contain a key-value pair
                key, _, value = line.partition(":")
                key, value = key.strip(), value.strip()
                if key in event:
                    # Append to existing key data
                    event[key] += f"\n{value}"
                else:
                    # Create new key in the event dictionary
                    event[key] = value

            # Yield the last event if the stream doesn't end with a new line
        if event:
            yield event
