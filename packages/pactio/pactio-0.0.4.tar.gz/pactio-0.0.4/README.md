# pactio
Unbreakable contracts in Django

## Usage

Install with pip:

```
(venv) $ python -m pip install pactio
```

Then add `pactio` to your list of middlewares:

```
# settings.py

MIDDLEWARE = [
    ...
    "pactio.middleware.PactioMiddleware",
]
```

Define the pydantic base model that is required for any particular view and simply include it
as an annotated argument to the view:

```python
# views.py
from pydantic import BaseModel

class UserData(BaseModel):
    username: str
    age: int
    accept_terms: bool


def register(request, user: UserData):
    if not user.accept_terms:
        ...

    save(user.username, user.age)
```
