"""
Base para importar todos los modelos.
Facilita la importación centralizada.
"""

from app.db.session import Base

# Importar todos los modelos para que estén registrados
from app.models.tipo_empleado import TipoEmpleado
from app.models.empleado import Empleado
from app.models.periodo_nomina import PeriodoNomina
from app.models.nomina import Nomina
from app.models.detalle_bono import DetalleBono
from app.models.detalle_beneficio import DetalleBeneficio
from app.models.detalle_deduccion import DetalleDeduccion
from app.models.auditoria_nomina import AuditoriaNomina

__all__ = [
    "Base",
    "TipoEmpleado",
    "Empleado",
    "PeriodoNomina",
    "Nomina",
    "DetalleBono",
    "DetalleBeneficio",
    "DetalleDeduccion",
    "AuditoriaNomina"
]