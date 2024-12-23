# Token strategy

To make lib more customizable, we separate token encoding and decoding to another class. FastAuth support 1 TokenStrategy
out the box:

* [JWTStrategy](/api/strategy/#jwt-strategy) - JWTHelper token strategy which use PyJWT library to encode and decode tokens

If you want to customize and add your own strategy just inherit abstract [TokenStrategy](/api/strategy/#fastauth.strategy.base.TokenStrategy)
class from `fastauth.strategy.base` package, and override `write_token` and `read_token` methods:

```python
import json
from fastauth.strategy.base import TokenStrategy
from fastauth.schema import TokenPayload
import base64

class CustomStrategy(TokenStrategy):
    async def write_token(self, payload: TokenPayload, **kwargs) -> str:
        return base64.b64encode(payload.model_dump_json().encode("ascii")) #convert payload to base64

    async def read_token(self, token: str, **kwargs) -> TokenPayload:
        data = base64.b64encode(token).decode("ascii") # convert base64 to json dict
        return TokenPayload.model_validate(json.loads(data)) # convert to py dict and validate to TokenPayload

```
