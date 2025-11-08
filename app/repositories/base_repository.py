"""
Repository Base - Patrón Repository.
Proporciona operaciones CRUD genéricas.

Principios SOLID aplicados:
- Single Responsibility: Solo maneja acceso a datos
- Open/Closed: Extensible mediante herencia
- Liskov Substitution: Subclases pueden reemplazar la base
- Dependency Inversion: Depende de abstracciones (SQLAlchemy)
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.db.session import Base

# TypeVar para hacer el repository genérico
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repository genérico con operaciones CRUD básicas.

    Uso:
        class EmpleadoRepository(BaseRepository[Empleado]):
            pass
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Inicializa el repository.

        Args:
            model: Clase del modelo SQLAlchemy
            db: Sesión de base de datos
        """
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.

        Args:
            id: ID del registro

        Returns:
            Modelo encontrado o None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_desc: bool = False
    ) -> List[ModelType]:
        """
        Obtiene todos los registros con paginación.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            order_by: Campo por el cual ordenar
            order_desc: Si ordenar descendente

        Returns:
            Lista de modelos
        """
        query = self.db.query(self.model)

        # Ordenamiento
        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                query = query.order_by(
                    desc(order_column) if order_desc else asc(order_column)
                )

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: ModelType) -> ModelType:
        """
        Crea un nuevo registro.

        Args:
            obj_in: Objeto a crear

        Returns:
            Objeto creado
        """
        self.db.add(obj_in)
        self.db.commit()
        self.db.refresh(obj_in)
        return obj_in

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        Actualiza un registro existente.

        Args:
            db_obj: Objeto de base de datos
            obj_in: Diccionario con campos a actualizar

        Returns:
            Objeto actualizado
        """
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """
        Elimina un registro por ID.

        Args:
            id: ID del registro a eliminar

        Returns:
            True si se eliminó, False si no se encontró
        """
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """
        Cuenta el total de registros.

        Returns:
            Cantidad de registros
        """
        return self.db.query(self.model).count()

    def exists(self, id: int) -> bool:
        """
        Verifica si existe un registro.

        Args:
            id: ID del registro

        Returns:
            True si existe, False si no
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None