from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.logging_config import log_info, setup_logging
from core.api.routes import router as core_router
from simulation.api.routes import router as simulation_router


app = FastAPI(title="Quantitative Portfolio API")

setup_logging()
log_info("Quantitative Portfolio API starting up")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Local dev and preview
        "https://mc-frontend-668378177815.europe-west1.run.app",  # GCP Cloud Run frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving
app.mount("/charts", StaticFiles(directory="simulation/charts"), name="charts")


app.include_router(core_router)
app.include_router(simulation_router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "API running"}
