# OAuth2

To configure OAuth client, we need install oauth support.
```txt
pip install 'fastapi-fastauth[oauth]'
```

After that we need create [OAuth model](/configuration/models/#oauthaccount-model) and [OAuthRepository](/configuration/repositories/#abstractoauthrepository).
Then create BaseAuthManager and init FastAuth.

## OAuth Client

OAuth2 router required BaseOAuth client, we need choose provider and init it client. For example, let's choose `github`
provider and create client

```python
from httpx_oauth.clients.github import GitHubOAuth2

github_client = GitHubOAuth2("CLIENT_ID", "CLIENT_SECRET_KEY")
```

After that we can pass it to router

--8<-- "docs/routers.md:95:106"
