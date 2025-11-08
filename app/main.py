"""
Aplicación principal de FastAPI.
Punto de entrada del sistema de nómina.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.db.session import init_db
from app.utils.exceptions import NominaException

# Importar routers
from app.api.endpoints import tipos_empleado, empleados, periodos, nomina


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida de la aplicación.
    Se ejecuta al inicio y al final.
    """
    # Startup
    print("\n" + "🚀 " + "="*58)
    print("🔧 Inicializando base de datos...")
    init_db()
    print("✓ Base de datos lista")
    print("="*60 + "\n")

    yield

    # Shutdown
    print("\n" + "🛑 Cerrando aplicación...")


# Crear aplicación FastAPI
# app = FastAPI(
#     title=settings.APP_NAME,
#     description=settings.APP_DESCRIPTION,
#     version=settings.APP_VERSION,
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
#     lifespan=lifespan
# )

# app = FastAPI(
#     title="Sistema de Nomina",
#     version="1.0.0",
#     docs_url="/docs",  # Swagger
#     redoc_url=None,    # Desactivar ReDoc
# )

app = FastAPI(
    title="Sistema de Nomina",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None
)

# ==========================================
# MIDDLEWARE
# ==========================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Agrega tiempo de procesamiento en headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ==========================================
# EXCEPTION HANDLERS
# ==========================================

@app.exception_handler(NominaException)
async def nomina_exception_handler(request: Request, exc: NominaException):
    """Handler para excepciones personalizadas del sistema."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para excepciones generales."""
    if settings.DEBUG:
        # En desarrollo, mostrar el error completo
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # En producción, ocultar detalles
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ha ocurrido un error interno"
            }
        )


# ==========================================
# ENDPOINTS BÁSICOS
# ==========================================

@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Endpoint raíz."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"], include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/info", tags=["Info"], include_in_schema=False)
async def info():
    """Información del sistema."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": "SQLite" if settings.is_sqlite else "MySQL",
        "timezone": settings.TIMEZONE
    }


# ==========================================
# INCLUIR ROUTERS
# ==========================================

app.include_router(
    tipos_empleado.router,
    prefix="/api/v1/tipos-empleado",
    tags=["Tipos de Empleado"]
)

app.include_router(
    empleados.router,
    prefix="/api/v1/empleados",
    tags=["Empleados"]
)

app.include_router(
    periodos.router,
    prefix="/api/v1/periodos",
    tags=["Períodos de Nómina"]
)

app.include_router(
    nomina.router,
    prefix="/api/v1/nomina",
    tags=["Nómina"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )