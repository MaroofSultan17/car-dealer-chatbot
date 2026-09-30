from decimal import Decimal

import pandas as pd

from car_chatbot.data import get_car_with_dealer, search_cars
from car_chatbot.schemas import (
    CarResponseDto,
    CarSearchResponseDto,
    DealerResponseDto,
    NoticeResponseDto,
)
from car_chatbot.search import recommend_alternatives, understand_car_request

ALTERNATIVES_LIMIT = 3

UNCLEAR_REQUEST_NOTICE = NoticeResponseDto(
    level="warning",
    text=(
        "I couldn't understand enough about the car you're looking for. "
        "Try mentioning a make, model, body type, fuel type, or feature."
    ),
)
ALTERNATIVES_NOTICE = NoticeResponseDto(
    level="warning",
    text=(
        "The exact car you're looking for isn't available in the current inventory. "
        "Here are some available alternatives you may want to consider."
    ),
)
NO_ALTERNATIVES_NOTICE = NoticeResponseDto(
    level="warning",
    text=(
        "The exact car you're looking for isn't available, and I couldn't find "
        "a suitable alternative in the current inventory."
    ),
)
PREFERENCE_MATCHES_NOTICE = NoticeResponseDto(
    level="info",
    text="I found these available cars based on what you're looking for.",
)
NO_PREFERENCE_MATCHES_NOTICE = NoticeResponseDto(
    level="warning",
    text="I couldn't find a suitable car matching your preferences in the current inventory.",
)
FALLBACK_NOTICE = NoticeResponseDto(
    level="info",
    text=(
        "AI assistance is temporarily unavailable. "
        "Basic inventory matching is being used instead."
    ),
)


def search_cars_for_message(message: str) -> CarSearchResponseDto:
    car_request, is_fallback_used = understand_car_request(message)
    has_vehicle_identity = any([car_request.make, car_request.model, car_request.variant])
    has_preferences = len(car_request.preferences) > 0
    notices: list[NoticeResponseDto] = []
    cars = pd.DataFrame()

    if not has_vehicle_identity and not has_preferences:
        notices.append(UNCLEAR_REQUEST_NOTICE)
    elif has_vehicle_identity:
        cars = search_cars(
            make=car_request.make,
            model=car_request.model,
            variant=car_request.variant,
        )

        if cars.empty:
            cars = recommend_alternatives(message, limit=ALTERNATIVES_LIMIT)

            if cars.empty:
                notices.append(NO_ALTERNATIVES_NOTICE)
            else:
                notices.append(ALTERNATIVES_NOTICE)
    else:
        cars = recommend_alternatives(message, limit=ALTERNATIVES_LIMIT)

        if cars.empty:
            notices.append(NO_PREFERENCE_MATCHES_NOTICE)
        else:
            notices.append(PREFERENCE_MATCHES_NOTICE)

    if is_fallback_used:
        notices.append(FALLBACK_NOTICE)

    car_dtos = [to_car_dto(car_row) for _, car_row in cars.iterrows()]
    search_response_dto = CarSearchResponseDto(cars=car_dtos, notices=notices)

    return search_response_dto


def to_car_dto(car_row: pd.Series) -> CarResponseDto:
    car_with_dealer = get_car_with_dealer(car_row)
    car_record = car_with_dealer["car"]
    dealer_record = car_with_dealer["dealer"]
    dealer_dto = None

    if dealer_record is not None:
        dealer_dto = DealerResponseDto(
            dealer_id=str(dealer_record["dealer_id"]),
            name=str(dealer_record["name"]),
            phone=str(dealer_record["phone"]),
            email=str(dealer_record["email"]),
            city=str(dealer_record["city"]),
        )

    price_in_cents = int(Decimal(str(car_record["price"])) * 100)
    car_dto = CarResponseDto(
        car_id=str(car_record["car_id"]),
        make=str(car_record["make"]),
        model=str(car_record["model"]),
        variant=str(car_record["variant"]),
        year=int(car_record["year"]),
        price_in_cents=price_in_cents,
        dealer=dealer_dto,
    )

    return car_dto
