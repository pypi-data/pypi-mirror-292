from typing import TypedDict, Required, Literal


class OrganizationClientSessionUser(TypedDict):
    organization_user_id: Required[str]
    meta: dict[str, str]


class ClientSessionUser(TypedDict):
    user_id: Required[str]
    meta: dict[str, str]


SessionUser = OrganizationClientSessionUser | ClientSessionUser


class CreateSessionRequest(TypedDict):
    user: Required[SessionUser]
    bot_id: Required[str]
    enabled_device_actions: list[str] | None
    editable: Literal["none", "user_messages", "all_messages"] | None
    meta: dict[str, str] | None


class RequestContentPartText(TypedDict):
    type: Required[Literal["text"]]
    text: Required[str]


class RequestContentPartImage(TypedDict):
    type: Required[Literal["image"]]
    content_type: Required[str]
    content: Required[bytes]


RequestContentPart = RequestContentPartText | RequestContentPartImage


class MessageEvent(TypedDict):
    type: Required[Literal["message"]]
    content: Required[str | list[RequestContentPart]]


class FunctionResultEvent(TypedDict):
    type: Required[Literal["function_result"]]
    tool_call_id: Required[str]
    result: Required[str | list[RequestContentPartText]]


class MultipleFunctionResultsEvent(TypedDict):
    type: Required[Literal["multiple_function_results"]]
    results: Required[dict[str, str | list[RequestContentPartText]]]


CompletionSourceEvent = MessageEvent | FunctionResultEvent | MultipleFunctionResultsEvent


class UpdateMessageRequest(TypedDict):
    content: Required[list[RequestContentPart] | str]
