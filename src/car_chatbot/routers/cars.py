import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from car_chatbot.car_search_service import search_cars_for_message
from car_chatbot.schemas import CarSearchRequestDto, CarSearchResponseDto

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cars", tags=["cars"])


def require_json(request: Request) -> None:
    content_type = request.headers.get("content-type", "")
    media_type = content_type.split(";")[0].strip().lower()

    if media_type != "application/json":
        raise HTTPException(status_code=415, detail="Content-Type must be application/json.")


@router.post("/search", dependencies=[Depends(require_json)])
def search(request_dto: CarSearchRequestDto) -> CarSearchResponseDto:
    try:
        search_response_dto = search_cars_for_message(request_dto.message)
    except FileNotFoundError as error:
        logger.exception("Inventory data could not be loaded.")
        raise HTTPException(
            status_code=503,
            detail="The inventory data is currently unavailable. Please try again later.",
        ) from error

    return search_response_dto
