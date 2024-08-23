# Franklin's FastAPI Extension

#### author: Franklin Neves Filho

## Install

```
pip install franklin-fastapi-extension
```

## Usage

The extension uses file names to route the endpoints.

create a routes module with the following structure:

```
src/
  app/
    routes/
      __init__.py
      user.py
  main.py
```

### src/app/routes/__init__.py
```python
from . import user
```

### src/app/routes/user.py
```python
# import the extension with the route decorators
from franklin_fastapi_extension import GET, POST

# endpoint: user/get-user
@GET('/get-user')
def get_user():
    return {'message': 'get user'}
```

### src/main.py
```python
from franklin_fastapi_extension import FastAPI, register_routes
from . import routes

app = FastAPI()

register_routes(app, routes)
```