# Auth Manager

After creating Repositories, you need to create AuthManager, just inherit [BaseAuthManager](/api/manager) class from `fastauth.manager` package.
You need to override `parse_id` method to convert User primary key from string to type you set in your model. 
Also you can override event which called every time after some event.
For example:

```python
from fastauth.manager import BaseAuthManager
import uuid
    
class AuthManager(BaseAuthManager):
    def parse_id(self, pk: str):
        return uuid.UUID(pk) # let`s pretend User pk is UUID type
```
