from inspect import Parameter, Signature
from typing import TYPE_CHECKING, Any, Callable, Coroutine

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


def get_token_from_request(
    config: FastAuthConfig,
    request: Request | None = None,
    refresh: bool = False,
) -> Callable[..., Coroutine[Any, Any, str]]:
    """
    Get token from request using the token transport locations specified in the FastAuthConfig.TOKEN_LOCATIONS.
    If the token is not found in any of the locations, raise a MissingToken exception.
    Because used FastAPI SecuredBase, in Transport.scheme() method,  we need to return callable to resolve the dependency later.

    :param config: FastAuthConfig
    :param request: FastAPI Request
    :param refresh: flag to set refresh token type
    :return: Callable with coroutine to pass to FastAPI Depends
    """

    parameters: list[Parameter] = []
    for location in config.TOKEN_LOCATIONS:
        transport = TRANSPORT_GETTER[location]
        parameters.append(
            Parameter(
                name=location,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(transport(config).schema(request, refresh)),
            )
        )

    @with_signature(Signature(parameters))
    async def _token_locations(**kwargs) -> str:
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
        msg = f"No token found in request from {config.TOKEN_LOCATIONS}"
        raise exceptions.MissingToken(msg)

    return _token_locations


async def get_login_response(
    security: "FastAuth", tokens: TokenResponse, response: Response | None = None
):
    """
    Get login response from the token locations specified in the FastAuthConfig.TOKEN_LOCATIONS.
    :param security: FastAuth instance
    :param tokens: TokenResponse instance with access and/or refresh tokens
    :param response: Optional FastAPI Response to modify to
    :return: FastAPI Response with multiple token locations(eg. headers, cookies) set
    """
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
    """
    Get logout response from the token locations specified in the FastAuthConfig.TOKEN_LOCATIONS.
    :param security: FastAuth instance
    :param response: Optional FastAPI Response to modify to
    :return: FastAPI Response with unset action for multiple token locations
    """
    for location in security.config.TOKEN_LOCATIONS:
        transport_callable = TRANSPORT_GETTER[location]
        transport: TokenTransport = transport_callable(security.config)
        response = await transport.logout_response(
            security,
            response,
        )
    return response
