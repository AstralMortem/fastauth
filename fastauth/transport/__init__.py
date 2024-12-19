from inspect import Parameter, Signature
from typing import TYPE_CHECKING

from fastapi import Depends, Request, Response
from makefun import with_signature

from fastauth import exceptions
from fastauth.config import FastAuthConfig
from fastauth.schema import TokenResponse
from fastauth.transport.bearer import BearerTransport
from fastauth.transport.cookie import CookieTransport

if TYPE_CHECKING:
    from fastauth.fastauth import FastAuth
    from fastauth.transport.base import TokenTransport

TRANSPORT_GETTER = {
    "headers": BearerTransport,
    "cookies": CookieTransport,
}


def _get_token_from_request(
    config: FastAuthConfig,
    request: Request | None = None,
    refresh: bool = False,
    locations: list[str] | None = None,
):
    if locations is None:
        locations = config.TOKEN_LOCATIONS

    parameters: list[Parameter] = []
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
        errors: list[exceptions.MissingToken] = []
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
        msg = f"No token found in request from {locations}"
        raise exceptions.MissingToken(msg)

    return _token_locations


async def get_login_response(
    security: "FastAuth", tokens: TokenResponse, response: Response | None = None
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


async def get_logout_response(security: "FastAuth", response: Response | None = None):
    for location in security.config.TOKEN_LOCATIONS:
        transport_callable = TRANSPORT_GETTER[location]
        transport: TokenTransport = transport_callable(security.config)
        response = await transport.logout_response(
            security,
            response,
        )
    return response
