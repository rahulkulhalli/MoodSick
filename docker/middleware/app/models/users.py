from pydantic import BaseModel, EmailStr

class UserRegisterData(BaseModel):
    email: EmailStr
    password: str
    age: int