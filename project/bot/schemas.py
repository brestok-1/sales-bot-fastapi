from pydantic import BaseModel


class UserFilterQuerySchema(BaseModel):
    history: list
    settings: dict