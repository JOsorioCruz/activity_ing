"""
Configuración central de la aplicación para ejecución LOCAL.
Optimizado para desarrollo en máquina local sin Docker.
"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    # ==========================================
    # INFORMACIÓN DE LA APLICACIÓN
    # ==========================================
    APP_NAME: str = "Sistema de Nómina - Local"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de gestión de nómina"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # ==========================================
    # BASE DE DATOS (SOLO MySQL)
    # ==========================================
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "administrador"
    DATABASE_NAME: str = "sistema_nomina"
    DATABASE_ECHO: bool = True

    # Pool de conexiones
    DATABASE_POOL_SIZE: int = 2
    DATABASE_MAX_OVERFLOW: int = 3
    DATABASE_POOL_RECYCLE: int = 3600

    # Construcción automática de URL MySQL
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL  # Alias para session.py

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT.lower() in ["local", "development"]

    # ==========================================
    # SERVIDOR
    # ==========================================
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1

    # ==========================================
    # SEGURIDAD
    # ==========================================
    SECRET_KEY: str = "local-development-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================================
    # CORS
    # ==========================================
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()