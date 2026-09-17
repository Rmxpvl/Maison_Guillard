from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    motDePasse: str


class TokenResponse(BaseModel):
    token: str