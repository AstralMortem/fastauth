from inspect import Parameter, Signature
from typing import Optional, List, TYPE_CHECKING
from makefun import with_signature
from fastauth.config import FastAuthConfig
from fastapi import Request, Depends, Response

from fastauth import exceptions

from .base import TokenTransport
from .bearer import BearerTransport
from .cookie import CookieTransport
from ..schema import TokenResponse

if TYPE_CHECKING:
    from fastauth.fastauth import FastAuth

TRANSPORT_GETTER = {
    "headers": BearerTransport,
    "cookies": CookieTransport,
}


def _get_token_from_request(
    config: FastAuthConfig,
    request: Optional[Request] = None,
    refresh: bool = False,
    locations: Optional[List[str]] = None,
):
    if locations is None:
        locations = config.TOKEN_LOCATIONS

    parameters: List[Parameter] = []
    for location in locations:
        transport = TRANSPORT_GETTER[location]
        parameters.append(
            Parameter(
                name=location,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(transport(config).schema(request, refresh)),
            )
        )

    @with_signature(Signature(parameters))
    async def _token_locations(*args, **kwargs):
        errors: List[exceptions.MissingToken] = []
        for location_name, token in kwargs.items():
            if token is not None:
                return token
            errors.append(
                exceptions.MissingToken(
                    msg=f"Missing token in {location_name}: Not authenticated"
                )
            )
        if errors:
            raise exceptions.MissingToken(msg=[err.detail for err in errors])
        raise exceptions.MissingToken(f"No token found in request from {locations}")

    return _token_locations


async def get_login_response(
    security: "FastAuth", tokens: TokenResponse, response: Optional[Response] = None
):
    for location in security.config.TOKEN_LOCATIONS:
        transport_callable = TRANSPORT_GETTER[location]
        transport: TokenTransport = transport_callable(security.config)
        response = await transport.login_response(
            security,
            tokens,
            response,
        )
    return response


async def get_logout_response(
    security: "FastAuth", response: Optional[Response] = None
):
    for location in security.config.TOKEN_LOCATIONS:
        transport_callable = TRANSPORT_GETTER[location]
        transport: TokenTransport = transport_callable(security.config)
        response = await transport.logout_response(
            security,
            response,
        )
    return response
