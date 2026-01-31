"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends

from sgp_plus.core.config import settings
from sgp_plus.core.rbac import require_permissions
from sgp_plus.features.auth.router import router as auth_router

app = FastAPI(
    title="SGP+ API",
    description="Sistema de Gestão de Processos Plus - API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)


@app.get("/admin/ping")
async def admin_ping(_=Depends(require_permissions("rbac.manage"))):
    """Rota protegida por RBAC (rbac.manage). Prova server-side."""
    return {"ok": True}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}
