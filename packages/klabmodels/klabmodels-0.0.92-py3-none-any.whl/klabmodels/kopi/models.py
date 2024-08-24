from typing import Dict, List, Optional
from redis_om import JsonModel, EmbeddedJsonModel, Field
from pydantic import BaseModel, Extra, ValidationError
from enum import Enum





# This will later be part of Kopi
class User(JsonModel):
    username: str  
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

