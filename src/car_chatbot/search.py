import logging

from car_chatbot.data import load_cars
from car_chatbot.llm import extract_car_search
from car_chatbot.models import CarSearch

logger = logging.getLogger(__name__)


def fallback_car_search(user_message: str) -> CarSearch:
    """Extract basic car information using the local inventory."""
    message = user_message.lower()
    cars = load_cars()

    make = None
    model = None
    variant = None

    # Match known makes.
    for value in cars["make"].dropna().unique():
        if str(value).lower() in message:
            make = str(value)
            break

    # Match known models.
    for value in cars["model"].dropna().unique():
        if str(value).lower() in message:
            model = str(value)
            break

    # Variant matching is intentionally broader because users may say
    # "hybrid" instead of the complete inventory variant name.
    variant_keywords = [
        "hybrid",
        "m sport",
        "amg line",
        "long range",
        "r-line",
        "gt-line",
        "gr sport",
    ]

    for keyword in variant_keywords:
        if keyword in message:
            variant = keyword
            break

    return CarSearch(
        make=make,
        model=model,
        variant=variant,
    )


def understand_car_request(user_message: str) -> tuple[CarSearch, bool]:
    """
    Understand a car request with Gemini first.

    Returns:
        A CarSearch object and a boolean indicating whether
        the local fallback was used.
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