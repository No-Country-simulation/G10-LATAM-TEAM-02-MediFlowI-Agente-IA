"""
MediFlow — API de Gestión de Usuarios y Roles (RF-03, RF-04, RF-05).

Permite a los administradores registrar, consultar, modificar, activar
o desactivar usuarios y asignar los roles:
- ADMINISTRADOR
- OPERADOR
- AUDITOR
- SUPERVISOR
"""

import re

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.security import hash_password, verify_access_token
from app.repositories.user_repository import (
    create_user,
    get_user_by_document,
    get_user_by_id,
    list_all_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Gestión de Usuarios"])

VALID_ROLES = {"ADMINISTRADOR", "OPERADOR", "AUDITOR", "SUPERVISOR"}
VALID_ESTADOS = {"ACTIVO", "INACTIVO"}


def validar_password_segura(password: str) -> str:
    """Aplica la política mínima para credenciales de usuarios clínicos."""
    if len(password) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe incluir una mayúscula.")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe incluir una minúscula.")
    if not re.search(r"\d", password):
        raise ValueError("La contraseña debe incluir un número.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("La contraseña debe incluir un símbolo.")
    return password


class UserCreateRequest(BaseModel):
    documento_identidad: str = Field(
        ...,
        description="Número de documento de identidad de 8 cifras",
        json_schema_extra={"example": "88776655"},
    )
    password: str = Field(
        ...,
        min_length=12,
        description="Mínimo 12 caracteres con mayúscula, minúscula, número y símbolo",
        json_schema_extra={"example": "ClaveSegura#2026"},
    )
    nombres: str = Field(..., json_schema_extra={"example": "María"})
    apellidos: str = Field(..., json_schema_extra={"example": "Gómez"})
    correo: str | None = Field(None, json_schema_extra={"example": "maria.gomez@clinica.com"})
    telefono: str | None = Field(None, json_schema_extra={"example": "987654321"})
    rol: str = Field("OPERADOR", json_schema_extra={"example": "OPERADOR"})
    estado: str = Field("ACTIVO", json_schema_extra={"example": "ACTIVO"})

    @field_validator("documento_identidad")
    @classmethod
    def validate_doc(cls, v: str) -> str:
        v_clean = v.strip()
        if not re.match(r"^\d{8}$", v_clean):
            raise ValueError(
                "El documento de identidad debe contener exactamente 8 cifras numéricas."
            )
        return v_clean

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validar_password_segura(v)

    @field_validator("rol")
    @classmethod
    def validate_rol(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in VALID_ROLES:
            raise ValueError(f"Rol inválido. Opciones permitidas: {', '.join(VALID_ROLES)}")
        return v_upper

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in VALID_ESTADOS:
            raise ValueError(f"Estado inválido. Opciones permitidas: {', '.join(VALID_ESTADOS)}")
        return v_upper


class UserUpdateRequest(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    correo: str | None = None
    telefono: str | None = None
    rol: str | None = None
    estado: str | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        return validar_password_segura(v) if v is not None else None

    @field_validator("rol")
    @classmethod
    def validate_rol(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v_upper = v.upper().strip()
        if v_upper not in VALID_ROLES:
            raise ValueError(f"Rol inválido. Opciones permitidas: {', '.join(VALID_ROLES)}")
        return v_upper

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v_upper = v.upper().strip()
        if v_upper not in VALID_ESTADOS:
            raise ValueError(f"Estado inválido. Opciones permitidas: {', '.join(VALID_ESTADOS)}")
        return v_upper


class UserResponse(BaseModel):
    id: str
    documento_identidad: str
    nombres: str
    apellidos: str
    correo: str | None = None
    telefono: str | None = None
    rol: str
    estado: str
    created_at: str | None = None


async def require_admin(authorization: str | None = Header(None)) -> dict:
    """Verifica que la petición provenga de una sesión activa con rol ADMINISTRADOR."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida."
        )
    token = authorization.replace("Bearer ", "").strip()
    try:
        user = await verify_access_token(token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de autenticación no está disponible temporalmente.",
        ) from exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada."
        )
    if user.get("rol") != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido. Requiere rol ADMINISTRADOR.",
        )
    return user


@router.get("", response_model=list[UserResponse], summary="RF-03 — Consultar Usuarios Registrados")
async def list_users(admin: dict = Depends(require_admin)):
    """Retorna la lista completa de usuarios del sistema (solo Administrador)."""
    users = await list_all_users()
    res = []
    for u in users:
        u_dict = dict(u)
        u_dict["id"] = str(u_dict["id"])
        if u_dict.get("created_at"):
            u_dict["created_at"] = str(u_dict["created_at"])
        res.append(UserResponse(**u_dict))
    return res


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="RF-03 — Registrar Usuario",
)
async def create_new_user(req: UserCreateRequest, admin: dict = Depends(require_admin)):
    """Permite al Administrador registrar un nuevo trabajador con su DNI de 8 cifras y rol."""
    existing = await get_user_by_document(req.documento_identidad)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el documento {req.documento_identidad}.",
        )

    pwd_hash, salt = hash_password(req.password)

    new_u = await create_user(
        documento_identidad=req.documento_identidad,
        password_hash=pwd_hash,
        salt=salt,
        nombres=req.nombres,
        apellidos=req.apellidos,
        correo=req.correo,
        telefono=req.telefono,
        rol=req.rol,
        estado=req.estado,
    )

    if not new_u:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo registrar el usuario en la base de datos.",
        )

    new_u_dict = dict(new_u)
    new_u_dict["id"] = str(new_u_dict["id"])
    if new_u_dict.get("created_at"):
        new_u_dict["created_at"] = str(new_u_dict["created_at"])

    return UserResponse(**new_u_dict)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="RF-03 & RF-04 — Modificar/Activar/Desactivar Usuario",
)
async def update_user_details(
    user_id: str, req: UserUpdateRequest, admin: dict = Depends(require_admin)
):
    """Permite modificar datos, asignar roles y cambiar estado (ACTIVO/INACTIVO)."""
    target = await get_user_by_id(user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_4404_NOT_FOUND
            if hasattr(status, "HTTP_4404_NOT_FOUND")
            else 404,
            detail="Usuario no encontrado.",
        )

    pwd_hash, salt = None, None
    if req.password:
        pwd_hash, salt = hash_password(req.password)

    updated = await update_user(
        user_id=user_id,
        nombres=req.nombres,
        apellidos=req.apellidos,
        correo=req.correo,
        telefono=req.telefono,
        rol=req.rol,
        estado=req.estado,
        password_hash=pwd_hash,
        salt=salt,
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Error actualizando el usuario.")

    u_dict = dict(updated)
    u_dict["id"] = str(u_dict["id"])
    return UserResponse(**u_dict)
