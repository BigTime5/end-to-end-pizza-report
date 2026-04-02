from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.analysis import router as analysis_router
from app.api.clients import router as clients_router
from app.api.reports import router as reports_router
from app.api.plaid import router as plaid_router

app = FastAPI(
    title="Tax Anomaly Detector",
    description="AI-powered tax anomaly detection for CPAs",
    version="1.0.0",
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(clients_router)
app.include_router(reports_router)
app.include_router(plaid_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
