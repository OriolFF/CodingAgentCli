from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re

class User(BaseModel):
    email: EmailStr

    @validator('email')
    def correct_domain(cls, v):
        if '.com' not in v:
            raise ValueError("Email must have a .com domain")
        return v