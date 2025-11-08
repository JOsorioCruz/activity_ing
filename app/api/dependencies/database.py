"""
Dependencias relacionadas con la base de datos.
"""

from typing import Generator
from sqlalchemy.orm import Session

from app.db.session import get_db


# Re-exportar para usar en endpoints
def get_database() -> Generator[Session, None, None]:
    """
    Obtiene una sesión de base de datos.

    Uso en endpoints:
        @router.get("/items/")
        def read_items(db: Session = Depends(get_database)):
            ...
    """
    yield from get_db()