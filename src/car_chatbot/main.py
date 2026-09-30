import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from car_chatbot.routers import cars

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Car Dealer Assistant")

app.include_router(cars.router)


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"

    return response


if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        index_file = FileResponse(FRONTEND_DIST / "index.html")

        return index_file

    @app.get("/favicon.svg", include_in_schema=False)
    def favicon() -> FileResponse:
        favicon_file = FileResponse(FRONTEND_DIST / "favicon.svg")

        return favicon_file
