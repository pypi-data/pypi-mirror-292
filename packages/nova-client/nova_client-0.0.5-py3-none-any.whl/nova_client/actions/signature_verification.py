import base64
import json
import os
import re
import traceback
import aiohttp

from datetime import datetime, timezone
from typing import Annotated, Any

from authlib.jose import JsonWebKey, JsonWebSignature
from authlib.jose.errors import DecodeError, BadSignatureError
from fastapi import HTTPException, Header
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request


class WebhookSignatureVerificationFailed(HTTPException):
    def __init__(self, extra_message: str | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook signature verification failed." + (f" {extra_message}" if extra_message else ""),
        )


def b64_encode_jws(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).replace(b"=", b"")


def b64_decode_jws(data: bytes) -> bytes:
    return base64.urlsafe_b64decode(data + b"=" * (4 - len(data) % 4))


_nova_jwks: dict[str, dict] = {}


async def get_nova_jwks(organization_id: str) -> dict:
    if organization_id in _nova_jwks:
        return _nova_jwks[organization_id]

    nova_base_url = os.getenv("NOVA__BASE_URL")

    if nova_base_url is None:
        raise ValueError("NOVA__BASE_URL not set.")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{nova_base_url}organizations/{organization_id}/.well-known/jwks.json",
        ) as response:
            response.raise_for_status()
            jwks = await response.json()
    _nova_jwks[organization_id] = jwks
    return jwks


class SignatureVerificationResult(BaseModel):
    headers: dict[str, Any]


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing the schema and trailing slashes and converting it to lowercase.
    """
    url_no_schema = re.sub(r"https?://", "", url)
    url_no_schema = url_no_schema.strip()
    url_no_schema = url_no_schema.rstrip("/")
    return url_no_schema.lower()


async def validate_signature_or_raise(
    url: str,
    method: str,
    signature_headers: bytes,
    signature: bytes,
    body: bytes,
) -> SignatureVerificationResult:
    jws_header = json.loads(b64_decode_jws(signature_headers))

    organization = jws_header.get("org", None)
    if organization is None:
        raise WebhookSignatureVerificationFailed("No organization in signature header.")
    try:
        jwks = await get_nova_jwks(organization)
    except aiohttp.ClientError as e:
        raise WebhookSignatureVerificationFailed("Could not fetch JWKs.") from e

    signed_url = jws_header.get("url", None)
    if signed_url is None:
        raise WebhookSignatureVerificationFailed("No signed URL in signature header.")

    signed_url_no_schema = normalize_url(signed_url)
    url_no_schema = normalize_url(url)

    if signed_url_no_schema != url_no_schema:
        raise WebhookSignatureVerificationFailed(
            f"Signed URL ({signed_url_no_schema}) does not match request URL ({url_no_schema})."
        )

    signed_method = jws_header.get("method", None)
    if signed_method is None:
        raise WebhookSignatureVerificationFailed("No signed URL in signature header.")
    if signed_method != method:
        raise WebhookSignatureVerificationFailed(
            f"Signed method {signed_method} does not match expected method {method}."
        )

    iat = jws_header.get("iat", None)
    if iat is None:
        raise WebhookSignatureVerificationFailed("No issue date in signature header.")
    iat_date = datetime.fromtimestamp(iat, tz=timezone.utc)
    if (datetime.now(tz=timezone.utc) - iat_date).total_seconds() > 300:
        raise WebhookSignatureVerificationFailed("Signature has been issued more than five minutes ago.")

    payload_data = b64_encode_jws(body)
    jws_data = {"protected": signature_headers, "payload": payload_data, "signature": signature}

    kid = jws_header["kid"]
    jwk = next((jwk for jwk in jwks["keys"] if jwk["kid"] == kid), None)

    if jwk is None:
        raise WebhookSignatureVerificationFailed(f"No matching JWK found for kid {kid}.")

    pub_key = JsonWebKey.import_key(jwk)
    jws = JsonWebSignature()

    try:
        jws.deserialize_json(obj=jws_data, key=pub_key)
    except DecodeError as e:
        raise WebhookSignatureVerificationFailed("Could not decode Json Web Signature.") from e
    except BadSignatureError as e:
        raise WebhookSignatureVerificationFailed("Invalid Signature.") from e
    except BaseException as e:
        traceback.print_exc()
        raise WebhookSignatureVerificationFailed() from e

    return SignatureVerificationResult(headers=jws_header)


async def assert_valid_webhook_body_signature(
    request: Request,
    signature_headers: Annotated[bytes, Header(alias="X-Webhook-Signature-Headers")],
    signature: Annotated[bytes, Header(alias="X-Webhook-Signature")],
) -> SignatureVerificationResult:
    return await validate_signature_or_raise(
        url=str(request.url),
        method=request.method.lower(),
        signature_headers=signature_headers,
        signature=signature,
        body=await request.body(),
    )


async def assert_valid_webhook_signature_no_body(
    request: Request,
    signature_headers: Annotated[bytes, Header(alias="X-Webhook-Signature-Headers")],
    signature: Annotated[bytes, Header(alias="X-Webhook-Signature")],
) -> SignatureVerificationResult:
    return await validate_signature_or_raise(
        url=str(request.url),
        method=request.method.lower(),
        signature_headers=signature_headers,
        signature=signature,
        body=b"{}",
    )
