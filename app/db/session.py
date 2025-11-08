"""
Configuración de la sesión de base de datos.
Optimizado para ejecución local con MySQL.
"""

import pymysql
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


def create_database_if_not_exists():
    """
    Crea la base de datos si no existe (solo aplica para MySQL).
    """
    try:
        connection = pymysql.connect(
            host=settings.DATABASE_HOST,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {settings.DATABASE_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        connection.close()
        print(f"[INFO] ✅ Base de datos verificada/creada: {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"[ERROR] ❌ No se pudo crear/verificar la base de datos: {e}")


def get_engine():
    """
    Crea el engine SQLAlchemy para MySQL.
    """
    create_database_if_not_exists()

    engine = create_engine(
        settings.database_url_sync,
        pool_pre_ping=True,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.DATABASE_ECHO
    )

    return engine


# Crear engine principal
engine = get_engine()

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesiones para usar en FastAPI con Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa las tablas en la base de datos si no existen.
    """
    print("\n[INFO] Inicializando base de datos...")

    from app.db.base import Base  # Importa modelos

    Base.metadata.create_all(bind=engine)

    print(f"[SUCCESS] 🗄️ Tablas sincronizadas en: {settings.DATABASE_NAME}\n")


def drop_all_tables() -> None:
    """
    Elimina TODAS las tablas (solo en modo local).
    """
    if not settings.is_local:
        raise Exception("drop_all_tables solo está permitido en entorno local")

    print("\n[WARNING] Eliminando todas las tablas...")
    from app.db.base import Base
    Base.metadata.drop_all(bind=engine)
    print("[SUCCESS] ✅ Todas las tablas eliminadas\n")


def reset_database() -> None:
    """
    Reinicia la base de datos (borra todo y lo recrea).
    Solo para desarrollo local.
    """
    if not settings.is_local:
        raise Exception("reset_database solo está permitido en entorno local")

    drop_all_tables()
    init_db()
    print("[SUCCESS] 🔄 Base de datos reiniciada\n")