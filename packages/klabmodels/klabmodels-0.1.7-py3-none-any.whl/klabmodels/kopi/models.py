from typing import Dict, List, Optional
from redis_om import JsonModel, EmbeddedJsonModel, Field
from pydantic import BaseModel, Extra, ValidationError
from enum import Enum




class User(JsonModel):
    username: str = Field(index=True)
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    #companies: List[str] | None = None  # companies the user has access to
    scopes: List[str] = []
    hashed_password: str = None    

