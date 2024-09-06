# A FastAPI starter project template

This project is a starter template for a FastAPI project.

## Tools

- [x] **FastAPI**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- [x] **SQLAlchemy**: SQLAlchemy is the Python SQL toolkit and Object Relational Mapper
- [x] **Alembic**: Alembic is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.
- [x] **Pydantic v2**: Data validation and settings management using Python type annotations.
- [x] **Pytest**: Testing framework for Python code. 100% test coverage has been set up.
- [x] **Poetry**: Poetry is a tool for dependency management and packaging in Python.
- [x] **Ruff**: Ruff is used for the QA of the code.
- [ ] **Docker**: Docker for containerization.
- [ ] **Github Actions**: CI/CD with Github Actions.
- [ ] **Gitlab CI**: CI/CD with Gitlab CI.

## Features

- [x] OAuth2 with Password (and hashing), Bearer with JWT tokens and three basic scopes.
- [x] Account CRUD already implemented (password robustness is checked used `zxcvbn`).
- [x] Helper function useful for creating query parameters that can be used to filter database queries (for example looking for items that has some fields greater than a certain value).
- [x] Support of development, testing and production settings.
- [x] Support of PostgreSQL and SQLite databases (other databases can be added with a plugin).
- [x] Some commands to initialize the database, dump the data, etc.
- [x] Use Sentry to report errors.
- [x] Translation and internationalization (i18n) of API errors and responses (some english and french translations are already implemented).

## Getting started

Begin by installing the dependencies with `poetry install`.
You can run the tests with `poetry run pytest`.

Let's imagine you want to create a new model, for example a `Client` model.

1. You can begin by creating the SQLAlchemy model. In order to do that, let's create a new file `app/models/client.py`:

```python
from sqlalchemy.orm import Mapped

from app.core.types import SecurityScopes
from app.db.base_class import Base, Str256, Str512


class Client(Base):
  last_name: Mapped[Str256]
  first_name: Mapped[Str256]
  subscription_year: Mapped[int]
  email: Mapped[Str256]
```

Notice that:

- The `Base` class is the base class for all the models. It is located in `app/db/base_class.py`. This class is very useful because it apply some default settings to all the models (table name, id, etc).
- Types of the fields are defined using the `sqlalchemy.orm.Mapped` type to represent an attribute on a mapped class. This allow type checkers to works so that ORM-mapped attributes are correctly types.

2. Then, you must add it to the file `app/db/base.py` so that Alembic see the model and generate migration scripts for it.
3. You can now create a Pydantic validation schema for the model. In order to do that, let's create a new file `app/schemas/client.py`:

```python
from datetime import datetime
from pydantic import (
  EmailStr,
  Field,
  computed_field,
)

from app.schemas.base import DefaultModel, ExcludedField

class ClientBase(DefaultModel):
  last_name: str = Field(..., min_length=3, max_length=256)
  first_name: str = Field(..., min_length=3, max_length=256)
  subscription_year: int = Field(
    ..., ge=2000, le=datetime.now().year
  ) # Let's imagine that no one was able to subscribe before 2000
  email: EmailStr = Field(..., max_length=256)

class ClientCreate(ClientBase):
  @computed_field
  @property
  def subscription_year(self) -> int:
    return datetime.now().year

class ClientUpdate(ClientBase):
  ...

class Client(ClientBase):
  """The model linked to the database and used in the API."""
  id: int
```

Notice that:

- All classes inherit from the `ClientBase` class to avoid code duplication.
- The `ClientCreate` class is used to validate the data when creating a new client. It is used in the `POST` requests.
- The `ClientUpdate` class is used to validate the data when updating a client. It is used in the `PUT` requests.
- The `Client` class is used to validate the data when reading a client. It is used in the `GET` requests.

4. You can now create a CRUD service for the model. In order to do that, let's create a new file `app/crud/client.py`:

```python
from app.crud.base import CRUDBase
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
  ...

client = CRUDClient(Client)
```

Notice that the `CRUDClient` class is a generic class that is used to create a CRUD service for the `Client` model. It is located in `app/crud/base.py`. This class is very useful because it apply some default settings to all the CRUD services (create, read, update, delete, etc) and in almost all cases, you don't need to modify it so it makes creating a CRUD service very straightforward.

5. You can now create a controller for the model. In order to do that, let's create a new file `app/api/endpoints/client.py`:

```python
import logging

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.core.translation import Translator
from app.crud.crud_client import client as clients
from app.dependencies import get_current_active_account, get_db
from app.schemas import client as client_schema

router = APIRouter(tags=["client"], prefix="/client")
translator = Translator()

logger = logging.getLogger("app.api.client")


@router.get(
  "/",
  response_model=list[client_schema.Client],
  dependencies=[Security(get_current_active_account)],
)
async def read_clients(db=Depends(get_db)):
  """
  Retrieve a list of all clients.
  """
  return await clients.query(db, limit=None)


@router.post(
  "/",
  response_model=client_schema.Client,
  dependencies=[Security(get_current_active_account)],
)
async def create_client(
  client: client_schema.ClientCreate, db=Depends(get_db)
):
  """
  Create a new client.
  """
  if await clients.query(db, email=client.email, limit=1):
      logger.debug(f"Client {client.email} already exists")
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=translator.ELEMENT_ALREADY_EXISTS,
      )
  return await clients.create(db, obj_in=client)


@router.get(
  "/{client_id}",
  response_model=client_schema.Client,
  dependencies=[Security(get_current_active_account)],
)
async def read_client(client_id: int, db=Depends(get_db)):
  """
  Retrieve a specific client by ID.
  """
  client = await clients.read(db, client_id)
  if client is None:
      logger.debug(f"Client {client_id} not found")
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=translator.ELEMENT_NOT_FOUND
      )
  return client


@router.put(
  "/{client_id}",
  response_model=client_schema.Client,
  dependencies=[Security(get_current_active_account)],
)
async def update_client(
  client_id: int,
  client: client_schema.ClientUpdate,
  db=Depends(get_db),
):
  """
  Update a specific client by ID.
  """
  old_client = await clients.read(db, client_id)
  if old_client is None:
      logger.debug(f"Client {client_id} not found")
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=translator.ELEMENT_NOT_FOUND
      )
  results = await clients.query(db, email=client.email, limit=1)
  if results and results[0].id != client.id:
      logger.debug(f"Client {client.email} already exists")
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=translator.ELEMENT_ALREADY_EXISTS,
      )
  return await clients.update(
      db, db_obj=old_client, obj_in=client
  )


@router.delete(
  "/{client_id}",
  response_model=client_schema.Client,
  dependencies=[Security(get_current_active_account)],
)
async def delete_client(client_id: int, db=Depends(get_db)):
  """
  Delete a specific client by ID.
  """
  if await clients.read(db, client_id) is None:
      logger.debug(f"Client {client_id} not found")
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail=translator.ELEMENT_NOT_FOUND
      )
  return await clients.delete(db, id=client_id)
```

Notice that:

- The `translator` object is used to translate the error messages.
- The `logger` object is used to log the errors or whaterever you want.
- The `Security` object is used to check if the user is authenticated. You can also check if the user has the right to do the action by adding the `scopes` parameter to the `Security` object (`scopes` are defined in `app/core/types.py` among others).

6. Your done! You can now test your API by running `uvicorn app.main:app --reload` and going to `http://127.0.0.1:8080/docs` in your browser.

7. Don't forget to add tests!

## Projects using this template

This model comes from the project [Clochette](https://github.com/Clochette-AbsINThe/clochette), which is a student bar inventory management application.

It is also used in some projects made by [MiNET](https://www.minet.net/).
