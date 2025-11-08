"""
Servicio de Nómina.
Maneja la lógica de negocio relacionada con nóminas.

Principios SOLID aplicados:
- Single Responsibility: Solo maneja operaciones de nómina
- Dependency Injection: Recibe repositories como dependencias
"""

from typing import List, Optional, Dict
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.empleado import Empleado
from app.models.periodo_nomina import PeriodoNomina
from app.models.nomina import Nomina
from app.models.detalle_bono import DetalleBono
from app.models.detalle_beneficio import DetalleBeneficio
from app.models.detalle_deduccion import DetalleDeduccion
from app.models.auditoria_nomina import AuditoriaNomina

from app.repositories.empleado_repository import EmpleadoRepository
from app.repositories.periodo_repository import PeriodoNominaRepository
from app.repositories.nomina_repository import NominaRepository

from app.services.calculadora_nomina import CalculadoraNomina

from app.schemas.nomina import NominaCreate, NominaUpdate

from app.utils.exceptions import (
    EmpleadoNoEncontradoException,
    PeriodoNoEncontradoException,
    NominaException,
    PeriodoCerradoException
)
from app.utils.enums import EstadoPeriodoEnum


class NominaService:
    """
    Servicio para gestión de nóminas.

    Coordina repositories y la calculadora para operaciones de nómina.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio con sus dependencias.

        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.empleado_repo = EmpleadoRepository(db)
        self.periodo_repo = PeriodoNominaRepository(db)
        self.nomina_repo = NominaRepository(db)
        self.calculadora = CalculadoraNomina()

    def calcular_y_crear_nomina(
        self,
        nomina_data: NominaCreate,
        usuario: str = "SYSTEM"
    ) -> Nomina:
        """
        Calcula y crea una nueva nómina.

        Args:
            nomina_data: Datos de entrada para la nómina
            usuario: Usuario que realiza el cálculo

        Returns:
            Nómina creada con todos los detalles

        Raises:
            EmpleadoNoEncontradoException: Si el empleado no existe
            PeriodoNoEncontradoException: Si el período no existe
            PeriodoCerradoException: Si el período está cerrado
            NominaException: Si ya existe nómina para ese empleado/período
        """
        # 1. Validar que el empleado exista
        empleado = self.empleado_repo.get_by_id(nomina_data.id_empleado)
        if not empleado:
            raise EmpleadoNoEncontradoException(nomina_data.id_empleado)

        # 2. Validar que el período exista
        periodo = self.periodo_repo.get_by_id(nomina_data.id_periodo)
        if not periodo:
            raise PeriodoNoEncontradoException(nomina_data.id_periodo)

        # 3. Validar que el período esté abierto
        if periodo.esta_cerrado:
            raise PeriodoCerradoException(nomina_data.id_periodo)

        # 4. Validar que no exista ya una nómina para este empleado/período
        nomina_existente = self.nomina_repo.get_by_empleado_periodo(
            nomina_data.id_empleado,
            nomina_data.id_periodo
        )

        if nomina_existente:
            raise NominaException(
                message=f"Ya existe una nómina para este empleado en el período {periodo.periodo_texto}",
                code="NOMINA_DUPLICADA",
                details={
                    "id_empleado": nomina_data.id_empleado,
                    "id_periodo": nomina_data.id_periodo,
                    "id_nomina_existente": nomina_existente.id_nomina
                }
            )

        # 5. Calcular nómina completa
        calculo = self.calculadora.calcular_nomina_completa(
            empleado=empleado,
            horas_trabajadas=Decimal(str(nomina_data.horas_trabajadas or 0)),
            horas_extras=Decimal(str(nomina_data.horas_extras or 0)),
            ventas_realizadas=Decimal(str(nomina_data.ventas_realizadas or 0))
        )

        # 6. Crear registro de nómina
        nomina = Nomina(
            id_empleado=nomina_data.id_empleado,
            id_periodo=nomina_data.id_periodo,
            horas_trabajadas=nomina_data.horas_trabajadas or 0,
            horas_extras=nomina_data.horas_extras or 0,
            ventas_realizadas=nomina_data.ventas_realizadas or 0,
            salario_bruto=calculo["salario_bruto"],
            total_bonos=calculo["total_bonos"],
            total_beneficios=calculo["total_beneficios"],
            total_deducciones=calculo["total_deducciones"],
            salario_neto=calculo["salario_neto"],
            calculado_por=usuario
        )

        self.db.add(nomina)
        self.db.flush()  # Para obtener el ID sin hacer commit

        # 7. Crear detalles de bonos
        for bono_data in calculo["detalles_bonos"].values():
            bono = DetalleBono(
                id_nomina=nomina.id_nomina,
                **bono_data
            )
            self.db.add(bono)

        # 8. Crear detalles de beneficios
        for beneficio_data in calculo["detalles_beneficios"].values():
            beneficio = DetalleBeneficio(
                id_nomina=nomina.id_nomina,
                **beneficio_data
            )
            self.db.add(beneficio)

        # 9. Crear detalles de deducciones
        for deduccion_data in calculo["detalles_deducciones"].values():
            deduccion = DetalleDeduccion(
                id_nomina=nomina.id_nomina,
                **deduccion_data
            )
            self.db.add(deduccion)

        # 10. Crear auditoría
        auditoria = AuditoriaNomina(
            id_nomina=nomina.id_nomina,
            accion="CREAR",
            usuario=usuario,
            descripcion=f"Nómina calculada para {empleado.nombre_completo}",
            valores_nuevos={
                "salario_bruto": float(calculo["salario_bruto"]),
                "salario_neto": float(calculo["salario_neto"]),
                "total_bonos": float(calculo["total_bonos"]),
                "total_beneficios": float(calculo["total_beneficios"]),
                "total_deducciones": float(calculo["total_deducciones"])
            }
        )
        self.db.add(auditoria)

        # 11. Guardar todo
        self.db.commit()
        self.db.refresh(nomina)

        return nomina

    def recalcular_nomina(
        self,
        id_nomina: int,
        nomina_update: NominaUpdate,
        usuario: str = "SYSTEM"
    ) -> Nomina:
        """
        Recalcula una nómina existente con nuevos datos.

        Args:
            id_nomina: ID de la nómina a recalcular
            nomina_update: Nuevos datos de entrada
            usuario: Usuario que realiza el recálculo

        Returns:
            Nómina recalculada

        Raises:
            NominaException: Si la nómina no existe o el período está cerrado
        """
        # 1. Obtener nómina existente
        nomina = self.nomina_repo.get_by_id(id_nomina)
        if not nomina:
            raise NominaException(
                message=f"Nómina con ID {id_nomina} no encontrada",
                code="NOMINA_NOT_FOUND"
            )

        # 2. Validar que el período esté abierto
        if nomina.periodo.esta_cerrado:
            raise PeriodoCerradoException(nomina.id_periodo)

        # 3. Guardar valores anteriores para auditoría
        valores_anteriores = {
            "horas_trabajadas": float(nomina.horas_trabajadas),
            "horas_extras": float(nomina.horas_extras),
            "ventas_realizadas": float(nomina.ventas_realizadas),
            "salario_bruto": float(nomina.salario_bruto),
            "salario_neto": float(nomina.salario_neto)
        }

        # 4. Actualizar datos de entrada
        if nomina_update.horas_trabajadas is not None:
            nomina.horas_trabajadas = nomina_update.horas_trabajadas
        if nomina_update.horas_extras is not None:
            nomina.horas_extras = nomina_update.horas_extras
        if nomina_update.ventas_realizadas is not None:
            nomina.ventas_realizadas = nomina_update.ventas_realizadas

        # 5. Recalcular nómina
        calculo = self.calculadora.calcular_nomina_completa(
            empleado=nomina.empleado,
            horas_trabajadas=Decimal(str(nomina.horas_trabajadas)),
            horas_extras=Decimal(str(nomina.horas_extras)),
            ventas_realizadas=Decimal(str(nomina.ventas_realizadas))
        )

        # 6. Actualizar valores calculados
        nomina.salario_bruto = calculo["salario_bruto"]
        nomina.total_bonos = calculo["total_bonos"]
        nomina.total_beneficios = calculo["total_beneficios"]
        nomina.total_deducciones = calculo["total_deducciones"]
        nomina.salario_neto = calculo["salario_neto"]
        nomina.calculado_por = usuario

        # 7. Eliminar detalles antiguos
        for bono in nomina.bonos:
            self.db.delete(bono)
        for beneficio in nomina.beneficios:
            self.db.delete(beneficio)
        for deduccion in nomina.deducciones:
            self.db.delete(deduccion)

        self.db.flush()

        # 8. Crear nuevos detalles de bonos
        for bono_data in calculo["detalles_bonos"].values():
            bono = DetalleBono(
                id_nomina=nomina.id_nomina,
                **bono_data
            )
            self.db.add(bono)

        # 9. Crear nuevos detalles de beneficios
        for beneficio_data in calculo["detalles_beneficios"].values():
            beneficio = DetalleBeneficio(
                id_nomina=nomina.id_nomina,
                **beneficio_data
            )
            self.db.add(beneficio)

        # 10. Crear nuevos detalles de deducciones
        for deduccion_data in calculo["detalles_deducciones"].values():
            deduccion = DetalleDeduccion(
                id_nomina=nomina.id_nomina,
                **deduccion_data
            )
            self.db.add(deduccion)

        # 11. Crear auditoría
        auditoria = AuditoriaNomina(
            id_nomina=nomina.id_nomina,
            accion="RECALCULAR",
            usuario=usuario,
            descripcion="Nómina recalculada con nuevos datos",
            valores_anteriores=valores_anteriores,
            valores_nuevos={
                "horas_trabajadas": float(nomina.horas_trabajadas),
                "horas_extras": float(nomina.horas_extras),
                "ventas_realizadas": float(nomina.ventas_realizadas),
                "salario_bruto": float(calculo["salario_bruto"]),
                "salario_neto": float(calculo["salario_neto"])
            }
        )
        self.db.add(auditoria)

        # 12. Guardar cambios
        self.db.commit()
        self.db.refresh(nomina)

        return nomina

    def calcular_nominas_periodo(
        self,
        id_periodo: int,
        usuario: str = "SYSTEM"
    ) -> Dict:
        """
        Calcula nóminas para todos los empleados activos de un período.

        Args:
            id_periodo: ID del período
            usuario: Usuario que realiza el cálculo

        Returns:
            Diccionario con resultados del cálculo masivo
        """
        # Validar período
        periodo = self.periodo_repo.get_by_id(id_periodo)
        if not periodo:
            raise PeriodoNoEncontradoException(id_periodo)

        if periodo.esta_cerrado:
            raise PeriodoCerradoException(id_periodo)

        # Obtener empleados activos
        empleados_activos = self.empleado_repo.get_all_activos()

        resultados = {
            "periodo_id": id_periodo,
            "total_empleados": len(empleados_activos),
            "nominas_exitosas": [],
            "nominas_fallidas": [],
            "total_exitosas": 0,
            "total_fallidas": 0
        }

        for empleado in empleados_activos:
            try:
                # Verificar si ya existe nómina
                if self.nomina_repo.exists_nomina(empleado.id_empleado, id_periodo):
                    resultados["nominas_fallidas"].append({
                        "empleado_id": empleado.id_empleado,
                        "empleado_nombre": empleado.nombre_completo,
                        "error": "Ya existe nómina para este período"
                    })
                    resultados["total_fallidas"] += 1
                    continue

                # Crear datos de nómina (valores por defecto)
                nomina_data = NominaCreate(
                    id_empleado=empleado.id_empleado,
                    id_periodo=id_periodo,
                    horas_trabajadas=Decimal("0"),
                    horas_extras=Decimal("0"),
                    ventas_realizadas=Decimal("0")
                )

                # Calcular y crear nómina
                nomina = self.calcular_y_crear_nomina(nomina_data, usuario)

                resultados["nominas_exitosas"].append({
                    "empleado_id": empleado.id_empleado,
                    "empleado_nombre": empleado.nombre_completo,
                    "nomina_id": nomina.id_nomina,
                    "salario_neto": float(nomina.salario_neto)
                })
                resultados["total_exitosas"] += 1

            except Exception as e:
                resultados["nominas_fallidas"].append({
                    "empleado_id": empleado.id_empleado,
                    "empleado_nombre": empleado.nombre_completo,
                    "error": str(e)
                })
                resultados["total_fallidas"] += 1

        return resultados

    def obtener_nomina_detallada(self, id_nomina: int) -> Optional[Nomina]:
        """
        Obtiene una nómina con todos sus detalles cargados.

        Args:
            id_nomina: ID de la nómina

        Returns:
            Nómina con relaciones cargadas o None
        """
        return self.nomina_repo.get_by_id(id_nomina)

    def listar_nominas_empleado(
        self,
        id_empleado: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Nomina]:
        """
        Lista todas las nóminas de un empleado.

        Args:
            id_empleado: ID del empleado
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de nóminas
        """
        return self.nomina_repo.get_by_empleado(id_empleado, skip, limit)

    def listar_nominas_periodo(
        self,
        id_periodo: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Nomina]:
        """
        Lista todas las nóminas de un período.

        Args:
            id_periodo: ID del período
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de nóminas
        """
        return self.nomina_repo.get_by_periodo(id_periodo, skip, limit)

    def eliminar_nomina(self, id_nomina: int, usuario: str = "SYSTEM") -> bool:
        """
        Elimina una nómina.

        Args:
            id_nomina: ID de la nómina
            usuario: Usuario que elimina

        Returns:
            True si se eliminó exitosamente

        Raises:
            PeriodoCerradoException: Si el período está cerrado
        """
        nomina = self.nomina_repo.get_by_id(id_nomina)
        if not nomina:
            return False

        if nomina.periodo.esta_cerrado:
            raise PeriodoCerradoException(nomina.id_periodo)

        # Crear auditoría antes de eliminar
        auditoria = AuditoriaNomina(
            id_nomina=nomina.id_nomina,
            accion="ELIMINAR",
            usuario=usuario,
            descripcion="Nómina eliminada",
            valores_anteriores={
                "salario_bruto": float(nomina.salario_bruto),
                "salario_neto": float(nomina.salario_neto)
            }
        )
        self.db.add(auditoria)
        self.db.commit()

        return self.nomina_repo.delete(id_nomina)

    def obtener_resumen_periodo(self, id_periodo: int) -> Dict:
        """
        Obtiene un resumen estadístico de un período.

        Args:
            id_periodo: ID del período

        Returns:
            Diccionario con estadísticas
        """
        nominas = self.nomina_repo.get_by_periodo(id_periodo)

        if not nominas:
            return {
                "periodo_id": id_periodo,
                "total_nominas": 0,
                "total_salario_bruto": 0,
                "total_salario_neto": 0,
                "total_bonos": 0,
                "total_beneficios": 0,
                "total_deducciones": 0
            }

        return {
            "periodo_id": id_periodo,
            "total_nominas": len(nominas),
            "total_salario_bruto": sum(float(n.salario_bruto) for n in nominas),
            "total_salario_neto": sum(float(n.salario_neto) for n in nominas),
            "total_bonos": sum(float(n.total_bonos) for n in nominas),
            "total_beneficios": sum(float(n.total_beneficios) for n in nominas),
            "total_deducciones": sum(float(n.total_deducciones) for n in nominas),
            "promedio_salario_neto": sum(float(n.salario_neto) for n in nominas) / len(nominas)
        }