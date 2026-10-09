from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    documento_identidad = Column(String(8), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    nombres = Column(String(250), nullable=False)
    apellidos = Column(String(250), nullable=False)
    correo = Column(String(250), nullable=True)
    telefono = Column(String(50), nullable=True)
    rol = Column(String, nullable=False, server_default='OPERADOR')
    estado = Column(String, nullable=False, server_default='ACTIVO')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, server_default=text("NOW()"), nullable=False)
