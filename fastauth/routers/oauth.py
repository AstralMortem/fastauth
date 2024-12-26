from fastapi import APIRouter, Depends, HTTPException, Query, Request
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token
from jwt import DecodeError

from fastauth import FastAuth, FastAuthConfig
from fastauth.schema.base import BaseSchema
from fastauth.utils.jwt_helper import TokenHelperProtocol


class OAuth2AuthorizeResponse(BaseSchema):
    authorization_url: str


def generate_state_token(
    data: dict[str, str], config: FastAuthConfig, encoder: TokenHelperProtocol
) -> str:
    data["aud"] = config.JWT_DEFAULT_STATE_AUDIENCE
    return encoder.encode_token(data, "state", config.JWT_STATE_TOKEN_MAX_AGE)


def get_oauth_router(
    security: FastAuth,
    client: BaseOAuth2,
    redirect_url: str | None = None,
    default_role: str | bool | None = None,
):
    router = APIRouter(
        prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX + f"/{client.name.lower()}"
    )
    callback_route_name = f"oauth:{client.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            client,
            redirect_url=redirect_url,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            client,
            route_name=callback_route_name,
        )

    @router.get("/authorize", response_model=OAuth2AuthorizeResponse)
    async def authorize(
        request: Request, scopes: list[str] = Query(None), manager=security.AUTH_MANAGER
    ):
        if redirect_url is not None:  # pragma: no cover
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        state_data: dict[str, str] = {}
        state = generate_state_token(state_data, security.config, manager.token_encoder)
        authorization_url = await client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get("/callback", name=callback_route_name)
    async def callback(
        request: Request,
        access_token_state: tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
        manager=security.AUTH_MANAGER,
        strategy=security.TOKEN_STRATEGY,
    ):
        token, state = access_token_state
        account_id, account_email = await client.get_id_email(token["access_token"])

        if account_email is None:
            raise HTTPException(
                status_code=400,
                detail="OAuth don`t provide email",
            )

        try:
            manager.token_encoder.decode_token(
                state, security.config.JWT_DEFAULT_STATE_AUDIENCE
            )
        except DecodeError as e:
            raise HTTPException(status_code=400, detail="Can`t decode token") from e

        if isinstance(default_role, str):
            role = await manager.get_role_by_codename(default_role)
        elif isinstance(default_role, bool):
            if default_role:
                role = await manager.get_role_by_codename(
                    security.config.USER_DEFAULT_ROLE
                )
            else:
                role = None
        else:
            role = None

        user = await manager.oauth_callback(
            client.name,
            token["access_token"],
            account_id,
            account_email,
            token.get("expires_at"),
            token.get("refresh_token"),
            request,
            default_role=role,
        )

        response = await manager.oauth_login(user, strategy, security)
        return response

    return router
