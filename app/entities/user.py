from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
