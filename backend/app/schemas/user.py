from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

class UserCreate(BaseModel):
    documento_identidad: str = Field(..., min_length=8, max_length=8, description="DNI de 8 dígitos")
    nombres: str = Field(..., max_length=250)
    apellidos: str = Field(..., max_length=250)
    telefono: str | None = Field(None, max_length=50)
    correo: EmailStr | None = Field(None)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una letra mayúscula.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("La contraseña debe tener al menos un carácter especial.")
        return v
class UserResponse(BaseModel):
    id: UUID | str
    documento_identidad: str
    nombres: str
    apellidos: str
    correo: EmailStr | None = None
    telefono: str | None = None
    rol: str
    estado: str

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, v) -> str:
        return str(v) if v is not None else ""

    class Config:
        from_attributes = True
