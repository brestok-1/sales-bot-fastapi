from pydantic import BaseModel


class UserFilterQuerySchema(BaseModel):
    history: list
