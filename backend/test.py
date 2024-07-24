from uuid import uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)


usr = User()

print(usr.model_json_schema())