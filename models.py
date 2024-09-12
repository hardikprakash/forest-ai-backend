from pydantic import BaseModel

class UserBase(BaseModel):
    username:str

class User(UserBase):
    password: str

class Token(BaseModel):
    token: str
    token_type: str

