import logging

import pandas as pd

from car_chatbot.config import CARS_FILE, DEALERS_FILE

logger = logging.getLogger(__name__)


def load_cars() -> pd.DataFrame:
    """Load car inventory from the CSV file."""
    if not CARS_FILE.exists():
        logger.error("Car inventory file not found: %s", CARS_FILE)
        raise FileNotFoundError(f"Car inventory file not found: {CARS_FILE}")

    return pd.read_csv(CARS_FILE)


def load_dealers() -> pd.DataFrame:
    """Load dealer information from the CSV file."""
    if not DEALERS_FILE.exists():
        logger.error("Dealer file not found: %s", DEALERS_FILE)
        raise FileNotFoundError(f"Dealer file not found: {DEALERS_FILE}")

    return pd.read_csv(DEALERS_FILE)


def search_cars(
    make: str | None = None,
    model: str | None = None,
    variant: str | None = None,
) -> pd.DataFrame:
    """Search available cars using optional make, model and variant filters."""
    cars = load_cars()

    filters = {
        "make": make,
        "model": model,
        "variant": variant,
    }

    for column, value in filters.items():
        if value and value.strip():
            cars = cars[
                cars[column].astype(str).str.contains(
                    value.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ]

    return cars.reset_index(drop=True)


def get_dealer(dealer_id: str) -> dict | None:
    """Return dealer details for a dealer ID."""
    dealers = load_dealers()

    match = dealers[dealers["dealer_id"] == dealer_id]

    if match.empty:
        logger.warning("Dealer not found for ID: %s", dealer_id)
        return None

    return match.iloc[0].to_dict()


def get_car_with_dealer(car: pd.Series) -> dict:
    """Combine a car record with its associated dealer."""
    car_data = car.to_dict()
    dealer = get_dealer(car_data["dealer_id"])

    return {
        "car": car_data,
        "dealer": dealer,
    }