from fastapi import FastAPI

app = FastAPI(title="Maison Guillard API")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}