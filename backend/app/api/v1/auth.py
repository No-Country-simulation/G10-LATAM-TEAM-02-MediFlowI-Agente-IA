"""
MediFlow — API de Autenticación (RF-01, RF-02).

Endpoints para inicio de sesión con documento de identidad de 8 cifras,
cierre de sesión y verificación de usuario activo en sesión.
"""

import re

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.security import (
    create_access_token,
    invalidate_access_token,
    require_current_user,
    verify_password,
)
from app.repositories.user_repository import get_user_by_document

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    documento_identidad: str = Field(
        ...,
        description="Número de documento de identidad de 8 cifras (DNI)",
        json_schema_extra={"example": "12345678"},
    )
    password: str = Field(
        ..., description="Contraseña del usuario", json_schema_extra={"example": "admin"}
    )

    @field_validator("documento_identidad")
    @classmethod
    def validate_documento_identidad(cls, v: str) -> str:
        v_clean = v.strip()
        if not re.match(r"^\d{8}$", v_clean):
            raise ValueError("El documento de identidad debe ser un número exacto de 8 cifras.")
        return v_clean


class UserResponse(BaseModel):
    id: str
    documento_identidad: str
    nombres: str
    apellidos: str
    correo: str | None = None
    telefono: str | None = None
    rol: str
    estado: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse
    mensaje: str = "Inicio de sesión exitoso"


@router.post("/login", response_model=LoginResponse, summary="RF-01 — Inicio de Sesión")
async def login(req: LoginRequest):
    """
    Permite a un trabajador de la clínica iniciar sesión ingresando:
    - documento_identidad (8 cifras)
    - contraseña

    Valida que el usuario exista, esté activo y la contraseña sea correcta.
    """
    user = await get_user_by_document(req.documento_identidad)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. El usuario no existe.",
        )

    if user["estado"] != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. El usuario se encuentra deshabilitado/inactivo.",
        )

    if not verify_password(req.password, user["password_hash"], user["salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas. Contraseña incorrecta.",
        )

    user_payload = {
        "id": str(user["id"]),
        "documento_identidad": user["documento_identidad"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "correo": user["correo"],
        "telefono": user["telefono"],
        "rol": user["rol"],
        "estado": user["estado"],
    }

    try:
        token = await create_access_token(user_payload)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible iniciar la sesión porque PostgreSQL no está disponible.",
        ) from exc

    return LoginResponse(
        access_token=token,
        token_type="Bearer",
        user=UserResponse(**user_payload),
        mensaje=f"Bienvenido/a {user['nombres']} {user['apellidos']} ({user['rol']})",
    )


@router.post("/logout", summary="RF-02 — Cierre de Sesión")
async def logout(authorization: str | None = Header(None)):
    """
    Invalida el token/sesión activa del usuario y desautoriza accesos posteriores.
    """
    if not authorization:
        return {"mensaje": "Sesión ya cerrada o token no provisto"}

    token = authorization.replace("Bearer ", "").strip()
    try:
        await invalidate_access_token(token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible cerrar la sesión porque PostgreSQL no está disponible.",
        ) from exc
    return {"mensaje": "Cierre de sesión exitoso. Token invalidado."}


@router.get("/me", response_model=UserResponse, summary="Consultar usuario autenticado")
async def get_current_user(current_user: dict = Depends(require_current_user)):
    """Retorna los datos del usuario de la sesión activa."""
    return UserResponse(**current_user)
