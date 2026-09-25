from fastapi import Depends, FastAPI

from app.dependencies.require_admin import require_admin
from fastapi.staticfiles import StaticFiles

from app.routers import auth, categories, produits
from app.services.photo_service import UPLOAD_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Maison Guillard API")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(produits.router)
app.include_router(produits.photos_router)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Exercises require_admin end-to-end; also useful during S5+ manual testing.
@app.get("/api/health/protected-check")
def protected_health_check(admin: dict = Depends(require_admin)):
    return {"status": "ok", "admin": admin["email"]}