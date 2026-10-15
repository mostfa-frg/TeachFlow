"""TeachFlow application setup and cross-cutting HTTP handlers."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1.router import router
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("teachflow")
app = FastAPI(
    title="TeachFlow API",
    description=(
        "Instructor-only course planning API. AI-generated plans remain proposals "
        "until an instructor explicitly approves them."
    ),
    version="0.2.0",
)
@app.exception_handler(HTTPException)
async def http_error_handler(_request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": detail}},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Request validation failed.",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.get("/manus-routes.json", include_in_schema=False)
async def route_manifest() -> JSONResponse:
    return JSONResponse({"routes": [{"path": "/", "title": "Instructor dashboard"}, {"path": "/roadmap", "title": "Course roadmap"}]})


@app.get("/", include_in_schema=False)
async def prototype() -> FileResponse:
    return FileResponse(
        Path(__file__).resolve().parents[2] / "frontend" / "index.html"
    )


app.include_router(router)
