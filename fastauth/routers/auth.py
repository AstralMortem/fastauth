from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastauth.fastauth import FastAuth


def get_auth_router(self: FastAuth):
    router = APIRouter(prefix=self.config.AUTH_ROUTER_DEFAULT_PREFIX)

    @router.post(self.config.TOKEN_LOGIN_URL)
    async def login(
        manager=self.AUTH_MANAGER,
        strategy=self.STRATEGY,
        credentials: OAuth2PasswordRequestForm = Depends(),
    ):
        user = await manager.user_login(credentials.username, credentials.password)
        access_token = await strategy.write_token(user)
        if self.config.ENABLE_REFRESH_TOKEN:
            refresh_token = await strategy.write_token(user, "refresh")
            return await self.TRANSPORT.get_login_response(access_token, refresh_token)
        return await self.TRANSPORT.get_login_response(access_token)

    @router.post(
        self.config.TOKEN_LOGOUT_URL,
        dependencies=[self.ACCESS_REQUIRED],
    )
    async def logout(
        strategy=self.STRATEGY,
    ):
        try:
            await strategy.destroy_token()
        except NotImplementedError:
            pass

        try:
            return await self.TRANSPORT.get_logout_response()
        except NotImplementedError:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post(self.config.TOKEN_REFRESH_URL)
    async def refresh(
        manager=self.AUTH_MANAGER, token=self.REFRESH_REQUIRED, strategy=self.STRATEGY
    ):
        # todo: implement refresh
        pass

    return router
