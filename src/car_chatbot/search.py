import logging

import pandas as pd

from car_chatbot.data import load_cars
from car_chatbot.llm import (
    extract_car_search,
    recommend_inventory_cars,
)
from car_chatbot.models import CarSearch

logger = logging.getLogger(__name__)


def fallback_car_search(user_message: str) -> CarSearch:
    """
    Perform basic literal matching against local inventory.

    The fallback does not try to reproduce full LLM reasoning.
    If no inventory make/model/variant can be identified, the
    original request is preserved as a preference so the
    application can still handle it gracefully.
    """
    message = user_message.strip()
    message_lower = message.lower()

    if not message:
        return CarSearch()

    cars = load_cars()

    make = None
    model = None
    variant = None

    for value in cars["make"].dropna().unique():
        if str(value).lower() in message_lower:
            make = str(value)
            break

    for value in cars["model"].dropna().unique():
        if str(value).lower() in message_lower:
            model = str(value)
            break

    for value in cars["variant"].dropna().unique():
        if str(value).lower() in message_lower:
            variant = str(value)
            break

    preferences = []

    if not any([make, model, variant]):
        preferences.append(message)

    return CarSearch(
        make=make,
        model=model,
        variant=variant,
        preferences=preferences,
    )


    for value in cars["variant"].dropna().unique():
        if str(value).lower() in message:
            variant = str(value)
            break

    return CarSearch(
        make=make,
        model=model,
        variant=variant,
    )


def understand_car_request(
    user_message: str,
) -> tuple[CarSearch, bool]:
    """
    Understand a car request using Gemini.

    Falls back to literal inventory matching if Gemini
    is temporarily unavailable.
    """
    try:
        search = extract_car_search(user_message)
        return search, False

    except Exception:
        logger.warning(
            "Gemini unavailable. Using local inventory fallback.",
            exc_info=True,
        )

        search = fallback_car_search(user_message)

        return search, True


def recommend_alternatives(
    user_message: str,
    limit: int = 3,
) -> pd.DataFrame:
    """
    Recommend real inventory vehicles for an unavailable request.

    Gemini ranks the inventory semantically, but every returned
    recommendation is validated against the local CSV.
    """
    cars = load_cars()

    if cars.empty:
        return cars

    try:
        recommended_ids = recommend_inventory_cars(
            user_message=user_message,
            cars=cars,
            limit=limit,
        )

        if recommended_ids:
            ranked_cars = []

            for car_id in recommended_ids[:limit]:
                match = cars[cars["car_id"] == car_id]

                if not match.empty:
                    ranked_cars.append(match.iloc[0])

            if ranked_cars:
                return pd.DataFrame(ranked_cars).reset_index(
                    drop=True
                )

    except Exception:
        logger.warning(
            "Gemini recommendation failed. "
            "Using basic inventory alternatives.",
            exc_info=True,
        )

    # Graceful fallback:
    # don't return arbitrary cars
    return cars.iloc[0:0].copy()