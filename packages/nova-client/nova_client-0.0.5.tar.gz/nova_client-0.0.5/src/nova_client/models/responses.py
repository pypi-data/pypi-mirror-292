from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

from nova_client.models.requests import RequestContentPartText


class AssetRef(BaseModel):
    asset_id: str
    content_type: str


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ResponseContentPartImage(BaseModel):
    type: Literal["image"]
    data: AssetRef


class ResponseContentPartText(BaseModel):
    type: Literal["text"]
    text: str


class ResponseContentPartFunctionCall(BaseModel):
    type: Literal["function"]
    tool_call_id: str
    function: FunctionCall


class PartialMessageEvent(BaseModel):
    type: Literal["partial_message"]
    message_id: str
    content: str
    end: bool


class LogFunctionEvent(BaseModel):
    type: Literal["log_function"]
    message_id: str
    tool_call_id: str
    name: str


class FunctionEvent(BaseModel):
    type: Literal["function"]
    message_id: str
    tool_call_id: str
    name: str
    arguments: dict[str, Any]


class LogFunctionExecutionEvent(BaseModel):
    type: Literal["log_function_execution"]
    tool_call_id: str
    name: str
    arguments: dict[str, str]
    result: list[RequestContentPartText]


class ExceptionEvent(BaseModel):
    type: Literal["exception"]
    key: str
    message: str


class UsageEvent(BaseModel):
    type: Literal["usage"]
    prompt_tokens: int
    completion_tokens: int


ReceivedEvent = (
    PartialMessageEvent | LogFunctionEvent | FunctionEvent | LogFunctionExecutionEvent | ExceptionEvent | UsageEvent
)


class UserMessage(BaseModel):
    message_id: str
    role: Literal["user"]
    content: list[ResponseContentPartText | ResponseContentPartImage]


class SystemMessage(BaseModel):
    message_id: str
    role: Literal["system"]
    content: list[ResponseContentPartText]


class AssistantMessage(BaseModel):
    message_id: str
    role: Literal["assistant"]
    content: list[ResponseContentPartText | ResponseContentPartFunctionCall]


class ToolMessage(BaseModel):
    message_id: str
    role: Literal["tool"]
    tool_call_id: str
    content: list[ResponseContentPartText | ResponseContentPartFunctionCall]


Message = UserMessage | SystemMessage | AssistantMessage | ToolMessage


class ChatSession(BaseModel):
    session_id: str
    organization_id: str
    meta: dict[str, str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[Message] = []


class ChatSessionResponse(BaseModel):
    token: str
    session: ChatSession
