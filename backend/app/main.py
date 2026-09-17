from fastapi import Depends, FastAPI

from app.dependencies.require_admin import require_admin
from app.routers import auth

app = FastAPI(title="Maison Guillard API")

app.include_router(auth.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Exercises require_admin end-to-end; also useful during S5+ manual testing.
@app.get("/api/health/protected-check")
def protected_health_check(admin: dict = Depends(require_admin)):
    return {"status": "ok", "admin": admin["email"]}