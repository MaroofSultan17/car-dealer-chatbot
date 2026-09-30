import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from car_chatbot.routers import cars

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
    response.headers["Cache-Control"] = "no-store"

    return response
