# Sistema de Nómina (Proyecto - Fines Académicos)

Este repositorio contiene un sistema de nómina desarrollado en Python con FastAPI. El propósito del proyecto es académico: servir como ejemplo didáctico de diseño de API REST, cálculo de nómina y organización de un proyecto web con buenas prácticas.

## Buenas prácticas, metodología y control de versiones

El desarrollo del proyecto se realizó siguiendo estándares profesionales, tanto en la estructura del código como en el proceso de versión y documentación:

✔ Principios de diseño
- Aplicar principios SOLID para construir componentes mantenibles y escalables.
- Escribir código limpio y legible: nombres descriptivos, funciones pequeñas, evitar duplicación y comentarios innecesarios.
- Realizar refactorización continua para mejorar la estructura sin modificar el comportamiento externo.

✔ Documentación y comentarios
- Documentar funciones y módulos mediante docstrings claros.
- Usar comentarios únicamente para explicar intención, no código evidente.

✔ Metodología de desarrollo
- Se recomienda trabajar bajo un enfoque ágil (Scrum o Kanban).
- Mantener una Definición de Hecho y tableros de tareas visibles.

✔ Control de versiones (Git / GitHub)
- El proyecto debe estar versionado en GitHub y reflejar el control del CIPA.
- Flujo recomendado:
  - Rama main: versión estable.
  - Rama develop: integración.
  - Ramas de trabajo: feature/*, fix/*, hotfix/*.
  - Commits claros preferiblemente estilo Conventional Commits.

Recomendado: Implementar CI con GitHub Actions para ejecutar pruebas y linters automáticamente.

---

## Metodología de Desarrollo Aplicada

Este proyecto se desarrolló siguiendo **Scrum** como framework ágil:

### Sprint Planning
- **Duración de sprints**: 1 semana
- **Definición de historias de usuario**: Cada funcionalidad se definió como historia de usuario con criterios de aceptación claros
- **Estimación**: Planning Poker para estimar complejidad de tareas
- **Product Backlog**: Priorización de funcionalidades según valor de negocio

### Daily Standup
- **Reuniones diarias del equipo**: Sincronización de 15 minutos
- **Tres preguntas clave**:
  - ¿Qué hice ayer?
  - ¿Qué haré hoy?
  - ¿Tengo algún impedimento?
- **Revisión de avances y bloqueos**: Identificación temprana de problemas

### Sprint Review & Retrospective
- **Demostración de funcionalidades**: Presentación del incremento al Product Owner
- **Identificación de mejoras**: Retrospectiva para mejorar el proceso
- **Definición de Done**: Verificación de que las historias cumplen criterios de aceptación

### Herramientas utilizadas:
- **GitHub Projects**: Tablero Kanban para gestión visual de tareas
- **GitHub Issues**: Historias de usuario, bugs y tareas técnicas
- **Git Flow**: Control de versiones con ramas feature, develop y main
- **Pull Requests**: Revisión de código antes de merge

### Roles del equipo (CIPA):
- **Product Owner**: Definición de requisitos y prioridades
- **Scrum Master**: Facilitación del proceso y eliminación de impedimentos
- **Development Team**: Desarrollo, testing y documentación

---

## Desarrollo Guiado por Pruebas (TDD)

El proyecto siguió la metodología **TDD (Test-Driven Development)** para componentes críticos del sistema, garantizando la calidad del código desde el diseño.

### Ciclo Red-Green-Refactor

El desarrollo siguió el ciclo TDD:

1. **🔴 RED - Escribir prueba que falla**
   - Se escribe primero la prueba que define el comportamiento esperado
   - La prueba falla porque la funcionalidad aún no existe

2. **🟢 GREEN - Escribir código mínimo para pasar la prueba**
   - Se implementa el código más simple que hace pasar la prueba
   - No se sobre-optimiza en esta etapa

3. **🔵 REFACTOR - Mejorar el código manteniendo las pruebas en verde**
   - Se refactoriza el código para mejorar diseño y legibilidad
   - Las pruebas garantizan que no se rompe funcionalidad

### Ejemplo: Calculadora de Nómina

```python
# ==========================================
# PASO 1: RED - Escribir la prueba primero
# ==========================================
def test_calcular_salario_asalariado():
    """
    Prueba: Un empleado asalariado debe recibir su salario base
    como salario bruto.
    """
    # Arrange
    empleado = crear_empleado_asalariado(salario_base=5000000)
    
    # Act
    salario_bruto = CalculadoraNomina.calcular_salario_bruto(empleado)
    
    # Assert
    assert salario_bruto == Decimal("5000000.00")

# ==========================================
# PASO 2: GREEN - Implementar código mínimo
# ==========================================
class CalculadoraNomina:
    @staticmethod
    def calcular_salario_bruto(empleado):
        """Calcula el salario bruto de un empleado."""
        return Decimal(str(empleado.salario_base))

# ==========================================
# PASO 3: REFACTOR - Mejorar el diseño
# ==========================================
class CalculadoraNomina:
    @staticmethod
    def calcular_salario_bruto(
        empleado: Empleado,
        horas_trabajadas: Decimal = Decimal("0"),
        horas_extras: Decimal = Decimal("0"),
        ventas_realizadas: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Calcula el salario bruto según el tipo de empleado.
        
        Soporta:
        - Empleados asalariados
        - Empleados por horas (con horas extras)
        - Empleados por comisión (con ventas)
        - Empleados temporales
        """
        tipo_nombre = empleado.tipo_empleado.nombre_tipo
        
        if tipo_nombre == TipoEmpleadoEnum.ASALARIADO.value:
            return self._calcular_asalariado(empleado)
        elif tipo_nombre == TipoEmpleadoEnum.POR_HORAS.value:
            return self._calcular_por_horas(empleado, horas_trabajadas, horas_extras)
        # ... más casos
```

### Componentes desarrollados con TDD:

#### 1. Calculadora de Nómina (app/services/calculadora_nomina.py)
- ✅ `test_calcular_salario_asalariado()` → Salario fijo mensual
- ✅ `test_calcular_salario_por_horas()` → Horas normales + extras
- ✅ `test_calcular_salario_por_comision()` → Salario base + comisión
- ✅ `test_calcular_bonos_antiguedad()` → 10% después de 5 años
- ✅ `test_calcular_deducciones()` → Seguridad social 4% + ARL 0.522%
- ✅ `test_salario_neto_no_negativo()` → Validación de salario neto >= 0

#### 2. Servicios de Negocio (app/services/nomina_service.py)
- ✅ `test_crear_nomina_exitosa()` → Creación completa de nómina
- ✅ `test_no_duplicar_nomina()` → Evitar nóminas duplicadas
- ✅ `test_recalcular_nomina()` → Actualización de valores
- ✅ `test_periodo_cerrado()` → No modificar períodos cerrados

#### 3. Validaciones de Negocio
- ✅ `test_horas_no_negativas()` → Validar horas >= 0
- ✅ `test_ventas_no_negativas()` → Validar ventas >= 0
- ✅ `test_empleado_activo()` → Solo empleados activos

### Ventajas observadas del TDD:

- ✅ **Mejor diseño**: Las pruebas primero fuerzan a pensar en la interfaz
- ✅ **Menos bugs**: Los errores se detectan inmediatamente
- ✅ **Refactorización segura**: Las pruebas garantizan que nada se rompe
- ✅ **Documentación viva**: Las pruebas documentan el comportamiento esperado
- ✅ **Cobertura alta**: Casi 100% de cobertura en lógica crítica

### Desarrollo Guiado por Comportamiento (BDD)

Además de TDD, se aplicó **BDD (Behavior-Driven Development)** para definir casos de uso:

```gherkin
Feature: Calcular nómina de empleado asalariado

  Scenario: Empleado asalariado con más de 5 años de antigüedad
    Given un empleado asalariado con salario de $5.000.000
    And el empleado tiene 6 años de antigüedad
    When se calcula la nómina para el período actual
    Then el salario bruto debe ser $5.000.000
    And debe recibir un bono de antigüedad de $500.000 (10%)
    And debe recibir bono de alimentación de $1.000.000
    And debe tener deducciones de seguridad social de $200.000 (4%)
    And debe tener deducciones de ARL de $26.100 (0.522%)
    And el salario neto debe ser $6.273.900
```

---

## Reglas de Negocio Implementadas

El sistema implementa las siguientes reglas de negocio para el cálculo de nómina según el tipo de empleado:

### Tipos de Empleados

#### 1. Empleado Asalariado
**Características:**
- Salario fijo mensual definido en el contrato
- Elegible para bonos y beneficios

**Cálculo de salario:**
```
Salario Bruto = Salario Base
```

**Bonos aplicables:**
- **Bono de antigüedad**: 10% del salario base si lleva más de 5 años en la empresa
  - Ejemplo: Salario $5.000.000 + 6 años → Bono $500.000

**Beneficios:**
- **Bono de alimentación**: $1.000.000/mes (cubierto por la empresa)

**Deducciones:**
- Seguridad Social y Pensión: 4% del salario bruto
- ARL (Riesgos Laborales): 0.522% del salario bruto

**Ejemplo de cálculo:**
```
Empleado: Carlos Rodríguez
Salario Base: $5.000.000
Años antigüedad: 6 años

Salario Bruto:        $5.000.000
+ Bono antigüedad:      $500.000 (10%)
+ Bono alimentación:  $1.000.000
- Seg. Social (4%):    -$200.000
- ARL (0.522%):         -$26.100
= Salario Neto:       $6.273.900
```

---

#### 2. Empleado Por Horas
**Características:**
- Pago por horas trabajadas con tarifa base por hora
- Horas extras pagadas a tarifa especial
- No recibe bonos de antigüedad

**Cálculo de salario:**
```
Salario Bruto = (Horas Normales × Tarifa) + (Horas Extras × Tarifa × 1.5)

Donde:
- Horas Normales: Hasta 40 horas semanales / 160 mensuales
- Horas Extras: Más de 40 horas semanales
- Multiplicador: 1.5x la tarifa normal
```

**Bonos aplicables:**
- ❌ No recibe bonos (ni antigüedad ni ventas)

**Beneficios:**
- **Fondo de ahorro**: Solo si cumple:
  - Tiene más de 1 año de antigüedad
  - Acepta participar en el fondo
  - Aporte: 2% del salario bruto (se descuenta de nómina)

**Deducciones:**
- Seguridad Social y Pensión: 4% del salario bruto
- ARL: 0.522% del salario bruto
- Fondo de ahorro: 2% (si acepta)

**Ejemplo de cálculo:**
```
Empleado: Juan Martínez
Tarifa hora: $25.000
Horas trabajadas: 160 horas (normales)
Horas extras: 10 horas
Antigüedad: 2 años
Acepta fondo: Sí

Salario Bruto:
  160 hrs × $25.000 =        $4.000.000
  10 hrs × $25.000 × 1.5 =     $375.000
  Total Bruto:               $4.375.000

Deducciones:
  - Seg. Social (4%):         -$175.000
  - ARL (0.522%):              -$22.838
  - Fondo ahorro (2%):         -$87.500
= Salario Neto:              $4.089.662
```

---

#### 3. Empleado Por Comisión
**Características:**
- Salario base mensual garantizado
- Comisión sobre ventas realizadas
- Bono adicional por alto desempeño

**Cálculo de salario:**
```
Salario Bruto = Salario Base + (Ventas × % Comisión)
```

**Bonos aplicables:**
- **Bono por ventas altas**: 3% adicional sobre ventas si ventas > $20.000.000
  - Ejemplo: Ventas $25.000.000 → Bono adicional $750.000 (3%)

**Beneficios:**
- **Bono de alimentación**: $1.000.000/mes (cubierto por la empresa)

**Deducciones:**
- Seguridad Social y Pensión: 4% del salario bruto
- ARL: 0.522% del salario bruto

**Ejemplo de cálculo:**
```
Empleado: Luis Ramírez
Salario Base: $2.000.000
Ventas realizadas: $25.000.000
% Comisión: 5%

Salario Bruto:
  Salario Base:              $2.000.000
  Comisión (5%):             $1.250.000
  Total Bruto:               $3.250.000

Bonos:
  + Bono ventas (3%):          $750.000 (ventas > $20M)
  + Bono alimentación:       $1.000.000

Deducciones:
  - Seg. Social (4%):         -$130.000
  - ARL (0.522%):              -$16.965

= Salario Neto:              $4.853.035
```

---

#### 4. Empleado Temporal
**Características:**
- Salario fijo mensual
- Contrato por tiempo definido
- Sin acceso a bonos ni beneficios adicionales

**Cálculo de salario:**
```
Salario Bruto = Salario Base
```

**Bonos aplicables:**
- ❌ No recibe ningún bono

**Beneficios:**
- ❌ No recibe beneficios adicionales

**Deducciones:**
- Seguridad Social y Pensión: 4% del salario bruto
- ARL: 0.522% del salario bruto

**Ejemplo de cálculo:**
```
Empleado: Sandra Vargas
Salario Base: $2.500.000
Contrato: 01/10/2024 - 31/03/2025

Salario Bruto:               $2.500.000

Deducciones:
  - Seg. Social (4%):         -$100.000
  - ARL (0.522%):              -$13.050

= Salario Neto:              $2.386.950
```

---

### Resumen de Reglas por Tipo

| Concepto | Asalariado | Por Horas | Por Comisión | Temporal |
|----------|------------|-----------|--------------|----------|
| **Salario Base** | Fijo mensual | Por hora | Fijo + Comisión | Fijo mensual |
| **Bono Antigüedad** | ✅ 10% (+5 años) | ❌ No | ❌ No | ❌ No |
| **Bono Ventas** | ❌ No | ❌ No | ✅ 3% (>$20M) | ❌ No |
| **Bono Alimentación** | ✅ $1.000.000 | ❌ No | ✅ $1.000.000 | ❌ No |
| **Fondo Ahorro** | ❌ No | ✅ 2% (+1 año) | ❌ No | ❌ No |
| **Horas Extras** | ❌ No | ✅ 1.5x | ❌ No | ❌ No |
| **Seg. Social** | ✅ 4% | ✅ 4% | ✅ 4% | ✅ 4% |
| **ARL** | ✅ 0.522% | ✅ 0.522% | ✅ 0.522% | ✅ 0.522% |

---

### Validaciones Implementadas

El sistema implementa las siguientes validaciones de negocio:

#### Validaciones de Entrada

1. **❌ Salario neto no puede ser negativo**
   ```python
   if salario_neto < 0:
       raise SalarioNegativoException(salario_neto, empleado.id)
   ```

2. **❌ Horas trabajadas no pueden ser negativas**
   ```python
   if horas_trabajadas < 0:
       raise ValidacionNominaException("horas_trabajadas", "No pueden ser negativas")
   ```

3. **❌ Ventas no pueden ser menores a $0**
   ```python
   if ventas_realizadas < 0:
       raise ValidacionNominaException("ventas_realizadas", "No pueden ser negativas")
   ```

#### Validaciones de Proceso

4. **❌ No se puede calcular nómina duplicada**
   - Un empleado solo puede tener una nómina por período
   
5. **❌ No se puede modificar período cerrado**
   - Solo períodos en estado "ABIERTO" pueden ser modificados

6. **❌ No se puede eliminar período con nóminas**
   - Integridad referencial protegida

7. **✅ Empleado debe estar activo**
   - Solo empleados con estado "ACTIVO" pueden recibir nómina

---

### Constantes del Sistema

```python
# Bonos
BONO_ANTIGUEDAD_PORCENTAJE = 10.00%       # 10% del salario
AÑOS_PARA_BONO_ANTIGUEDAD = 5             # Mínimo 5 años

BONO_ALIMENTACION = $1.000.000            # Fijo mensual

BONO_VENTAS_PORCENTAJE = 3.00%            # 3% sobre ventas
COMISION_VENTAS_LIMITE = $20.000.000     # Umbral para bono

# Horas
HORAS_NORMALES_MAXIMAS = 40               # Por semana
MULTIPLICADOR_HORA_EXTRA = 1.5            # 1.5x tarifa normal

# Deducciones
DEDUCCION_SEGURIDAD_SOCIAL = 4.00%        # 4% del salario bruto
DEDUCCION_ARL = 0.522%                    # 0.522% del salario bruto

# Fondo de Ahorro
FONDO_AHORRO_PORCENTAJE = 2.00%           # 2% del salario
AÑOS_PARA_FONDO_AHORRO = 1                # Mínimo 1 año
```

---

## Tecnologías y dependencias

- Python 3.10+ (recomendado)
- FastAPI (framework web)
- Uvicorn (servidor ASGI)
- SQLAlchemy (ORM)
- PyMySQL (driver MySQL)
- Pydantic / pydantic-settings (validación de modelos y configuración)
- Alembic (migraciones)

Las dependencias están listadas en `requirements.txt`.

---

## Estructura principal del proyecto

Carpeta principal relevante:

- `app/` - Código de la aplicación
  - `app/main.py` - Punto de entrada (configura FastAPI, middlewares y routers)
  - `app/api/endpoints/` - Routers por recurso (empleados, tipos_empleado, periodos, nomina)
  - `app/core/config.py` - Configuración central (host, puerto, base de datos, CORS, .env)
  - `app/db/` - Inicialización de sesión y base de datos
  - `app/services/` - Lógica de negocio (cálculo de nómina, servicios de entidades)
  - `app/repositories/` - Acceso a datos
  - `app/models/` - Modelos ORM
  - `app/schemas/` - Esquemas Pydantic (request/response)

Otros archivos:

- `requirements.txt` - dependencias
- `scripts/init_local_db.py` - script auxiliar para inicializar la DB local (si aplica)

---

## Requisitos para ejecutar localmente

1. Tener Python 3.10+ instalado.
2. Tener MySQL (u otro servidor compatible) configurado si desea usar la configuración por defecto.
   - Por defecto la configuración en desarrollo está en `app/core/config.py`: usuario `root`, contraseña `root`, host `127.0.0.1`, puerto `3306`, base de datos `sistema_nomina`.
3. (Opcional) Crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Variables de entorno (opcional):
   - El proyecto carga `.env` (si existe) gracias a `pydantic-settings`. Puedes crear un archivo `.env` en la raíz con variables como:

```
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=root
DATABASE_NAME=sistema_nomina
HOST=127.0.0.1
PORT=8000
RELOAD=True
```

Si no defines `.env`, el proyecto usará los valores por defecto que están en `app/core/config.py`.

---

## Inicializar la base de datos (local)

- Revisa `scripts/init_local_db.py` si quieres crear tablas o datos de ejemplo. Dependiendo de cómo tengas configurado MySQL, puede que necesites crear la base de datos `sistema_nomina` manualmente antes de ejecutar.

---

## Cómo correr la aplicación (desarrollo)

Desde la raíz del proyecto (donde está `app/`) ejecuta:

```bash
uvicorn app.main:app --reload 
```

Parámetros importantes:
- `--reload` reinicia el servidor cuando hay cambios (útil en desarrollo).
- El host y puerto por defecto están configurados en `app/core/config.py` (HOST=127.0.0.1, PORT=8000).

Si prefieres usar Python directamente:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Documentación interactiva (Swagger)

FastAPI ofrece Swagger UI. En este proyecto la URL de la documentación (Swagger) está configurada en `app/main.py` como:

### - Swagger UI: `http://127.0.0.1:8000/docs`
### - ReDoc: `http://127.0.0.1:8000/redoc`

Abre esa URL en tu navegador después de iniciar el servidor para ver y probar los endpoints desde la interfaz.

### Ejemplo (captura de Swagger UI)

A continuación hay una imagen de ejemplo que muestra cómo se ve Swagger UI. `docs/swagger_example.png`
![Ejemplo Swagger UI](docs/img.png)

---

## Endpoints principales

La API expone los siguientes routers y rutas base (prefijos):

- Tipos de empleado (CRUD)
  - Base: `/api/v1/tipos-empleado`
  - `GET /api/v1/tipos-empleado/` - Listar tipos
  - `GET /api/v1/tipos-empleado/{id_tipo_empleado}` - Obtener tipo por ID
  - `POST /api/v1/tipos-empleado/` - Crear tipo
  - `PUT /api/v1/tipos-empleado/{id_tipo_empleado}` - Actualizar tipo
  - `DELETE /api/v1/tipos-empleado/{id_tipo_empleado}` - Eliminar tipo

- Empleados (CRUD y búsquedas)
  - Base: `/api/v1/empleados`
  - `GET /api/v1/empleados/` - Listar empleados (soporta query params: skip, limit, solo_activos)
  - `GET /api/v1/empleados/buscar?q=...` - Buscar empleados por término
  - `GET /api/v1/empleados/{id_empleado}` - Obtener empleado por ID
  - `POST /api/v1/empleados/` - Crear empleado
  - `PUT /api/v1/empleados/{id_empleado}` - Actualizar empleado
  - `DELETE /api/v1/empleados/{id_empleado}` - Eliminar empleado
  - `GET /api/v1/empleados/antiguedad/{anio_minimos}` - Empleados con antigüedad mínima

- Períodos de nómina
  - Base: `/api/v1/periodos`
  - `GET /api/v1/periodos/` - Listar períodos
  - `GET /api/v1/periodos/ultimos?cantidad=N` - Últimos N períodos
  - `GET /api/v1/periodos/abiertos` - Períodos abiertos
  - `GET /api/v1/periodos/{id_periodo}` - Obtener período por ID
  - `GET /api/v1/periodos/buscar/{anio}/{mes}` - Buscar por año/mes
  - `POST /api/v1/periodos/` - Crear período
  - `PUT /api/v1/periodos/{id_periodo}` - Actualizar período
  - `DELETE /api/v1/periodos/{id_periodo}` - Eliminar período

- Nómina (cálculo y gestión)
  - Base: `/api/v1/nomina`
  - `POST /api/v1/nomina/calcular` - Calcular y crear nómina para un empleado (body: `NominaCreate`)
  - `POST /api/v1/nomina/calcular-periodo?id_periodo=...` - Calcular nóminas para todos los empleados de un período
  - `GET /api/v1/nomina/{id_nomina}` - Obtener nómina detallada por ID
  - `GET /api/v1/nomina/empleado/{id_empleado}` - Listar nóminas de un empleado
  - `GET /api/v1/nomina/periodo/{id_periodo}` - Listar nóminas de un período
  - `GET /api/v1/nomina/periodo/{id_periodo}/resumen` - Resumen estadístico del período
  - `PUT /api/v1/nomina/{id_nomina}` - Recalcular nómina (actualizar horas/ventas, etc.)
  - `DELETE /api/v1/nomina/{id_nomina}` - Eliminar nómina

> Nota: Los esquemas de request/response están definidos en `app/schemas/` y aparecen documentados en Swagger con ejemplos y validaciones.

---

## Ejemplos rápidos de uso (cURL)

- Obtener lista de empleados:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/empleados/" -H "accept: application/json"
```

- Calcular una nómina (ejemplo simplificado):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nomina/calcular" \
  -H "Content-Type: application/json" \
  -d '{"id_empleado": 1, "id_periodo": 1}'
```

Usa Swagger UI para ver los modelos completos y parámetros esperados.

---

## Consideraciones y notas finales

- Propósito académico: Este proyecto se desarrolló con fines de aprendizaje y demostración. No está pensado para producción sin auditoría, pruebas adicionales y endurecimiento de seguridad.
- Seguridad: Las credenciales por defecto son para desarrollo local solamente. No usar estas credenciales en entornos públicos.
- Migraciones: Si agregas o cambias modelos, actualiza/ejecuta las migraciones con Alembic.

---