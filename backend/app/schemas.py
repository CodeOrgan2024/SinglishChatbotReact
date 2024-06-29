from pydantic import BaseModel
from typing import List

class MessageBase(BaseModel):
    content: str
    
class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id:int
    owner_id: int
    
    class Config:
        orm_mode = True
        
class UserBase(BaseModel):
    username : str
    
class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: int
    messages : List[Message]= []
    
    class Config:
        orm_mode = True