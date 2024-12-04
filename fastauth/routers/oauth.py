from typing import Optional, List
from fastapi import APIRouter, Query, Request, Depends
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token
from jwt import DecodeError
from pydantic import BaseModel
from fastauth import exceptions
from fastauth.exceptions import InvalidToken
from fastauth.fastauth import FastAuth
from fastauth.models import UOAP, ID, OAP, PP, RP
from fastauth.schemas import OAuthCreate
from fastauth.utils.jwt_helper import SecretType, encode_jwt, decode_jwt


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


def generate_state_token(
    data: dict[str, str],
    secret: SecretType,
    audience: List[str],
    lifetime_seconds: int = 3600,
) -> str:
    data["aud"] = audience[0]
    return encode_jwt(data, secret, lifetime_seconds)


def get_oauth_router(
    self: FastAuth[UOAP, ID, RP, PP, OAP],
    oauth_client: BaseOAuth2,
    redirect_url: Optional[str] = None,
    default_role: Optional[str] = None,
):
    prefix = self.config.OAUTH_ROUTER_DEFAULT_PREFIX + f"/{oauth_client.name.lower()}"
    router = APIRouter(prefix=prefix)
    callback_route_name = f"oauth:{oauth_client.name}.callback"

    if redirect_url is not None:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            redirect_url=redirect_url,
        )
    else:
        oauth2_authorize_callback = OAuth2AuthorizeCallback(
            oauth_client,
            route_name=callback_route_name,
        )

    @router.get(
        "/authorize",
        name=f"oauth:{oauth_client.name}.authorize",
    )
    async def authorize(request: Request, scopes: List[str] = Query(None)):
        if redirect_url is not None:
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))

        state_data: dict[str, str] = {}
        state_data["aud"] = self.config.JWT_STATE_TOKEN_AUDIENCE
        state = encode_jwt(
            state_data,
            self.config.JWT_SECRET,
            self.config.JWT_STATE_TOKEN_LIFETIME,
            self.config.JWT_ALGORITHM,
        )
        authorization_url = await oauth_client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )

        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get("/callback", name=callback_route_name)
    async def callback(
        access_token_state: tuple[OAuth2Token, str] = Depends(
            oauth2_authorize_callback
        ),
        manager=self.AUTH_MANAGER,
        strategy=self.STRATEGY,
    ):
        token, state = access_token_state
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )
        if account_email is None:
            raise exceptions.OAuthUnavailableEmail()

        try:
            decode_jwt(
                state,
                self.config.JWT_SECRET,
                self.config.JWT_STATE_TOKEN_AUDIENCE,
                [self.config.JWT_ALGORITHM],
            )
        except DecodeError:
            raise InvalidToken("state")

        oauth_schema = OAuthCreate(
            oauth_name=oauth_client.name,
            access_token=token["access_token"],
            account_id=account_id,
            account_email=account_email,
            expires_at=token.get("expires_at"),
            refresh_token=token.get("refresh_token"),
        )

        user = await manager.oauth_callback(
            oauth_schema,
            associate_by_email=self.config.OAUTH_ASSOCIATE_WITH_EMAIL,
            is_verified_by_default=self.config.OAUTH_IS_VERIFIED_DEFAULT,
            default_role=default_role,
        )
        if not user.is_active:
            raise exceptions.OAuthUserNotActive()

        access_token = await strategy.write_token(user)
        refresh_token = None
        if self.config.ENABLE_REFRESH_TOKEN:
            refresh_token = await strategy.write_token(user, "refresh")
        return await self.TRANSPORT.get_login_response(access_token, refresh_token)

    return router
