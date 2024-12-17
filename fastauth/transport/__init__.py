from inspect import Parameter, Signature
from typing import Optional, List
from makefun import with_signature
from fastauth.config import FastAuthConfig
from fastapi import Request, Depends

from fastauth import exceptions
from .bearer import BearerTransport
from .cookie import CookieTransport

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
        print(kwargs)
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
