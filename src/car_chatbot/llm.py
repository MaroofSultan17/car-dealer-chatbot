import logging
import os

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

from car_chatbot.models import CarRecommendations, CarSearch

logger = logging.getLogger(__name__)

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"


def get_client() -> Groq:
    """Create a Groq client using the API key from the environment."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    return Groq(api_key=api_key)


def extract_car_search(user_message: str) -> CarSearch:
    """Understand a user's car request using the LLM."""
    if not user_message.strip():
        return CarSearch()

    client = get_client()

    prompt = f"""
You are helping a user search for a car.

Extract the following information from the user's request:

- make: manufacturer if mentioned
- model: model if mentioned
- variant: specific trim or variant if mentioned
- preferences: any other requirements or characteristics

Preferences can include body style, engine type, fuel type,
performance, luxury, economy, size, drivetrain, or other
vehicle characteristics.

Do not invent information the user did not provide.

Examples:

User: I want a Toyota Corolla
make: Toyota
model: Corolla
variant: null
preferences: []

User: Porsche GTR
make: Porsche
model: GTR
variant: null
preferences: []

User: I want a V8
make: null
model: null
variant: null
preferences: ["V8"]

User request:
{user_message}

Return only valid JSON with these keys:
make, model, variant, preferences
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured car search "
                        "information and return only JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            return CarSearch()

        return CarSearch.model_validate_json(content)

    except Exception:
        logger.exception(
            "LLM failed to understand the car request."
        )
        raise


def recommend_inventory_cars(
    user_message: str,
    cars: pd.DataFrame,
    limit: int = 3,
) -> list[str]:
    """
    Ask the LLM to select suitable alternatives from real inventory.

    The LLM may only return car IDs that exist in the supplied inventory.
    """
    if cars.empty:
        return []

    client = get_client()

    inventory_lines = []

    for _, car in cars.iterrows():
        inventory_lines.append(
            f"{car['car_id']}: "
            f"{car['year']} {car['make']} {car['model']} "
            f"{car['variant']}, price €{car['price']}"
        )

    inventory = "\n".join(inventory_lines)

    prompt = f"""
A customer requested:

"{user_message}"

The exact requested vehicle may not be available.

Choose up to {limit} vehicles from the AVAILABLE INVENTORY
that are the most reasonable alternatives.

Consider the customer's likely intent, including manufacturer,
vehicle type, performance, powertrain, size, luxury level,
price positioning, and other relevant characteristics.

IMPORTANT RULES:
- Recommend only vehicles from AVAILABLE INVENTORY.
- Never invent a vehicle.
- Never invent an inventory ID.
- Return the most relevant alternatives first.
- Return only valid JSON in this format:
  {{"car_ids": ["C001", "C002"]}}

AVAILABLE INVENTORY:

{inventory}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You recommend vehicles only from the "
                        "provided inventory and return only JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            return []

        recommendations = CarRecommendations.model_validate_json(
            content
        )

        valid_ids = set(cars["car_id"].astype(str))

        return [
            car_id
            for car_id in recommendations.car_ids
            if car_id in valid_ids
        ][:limit]

    except Exception:
        logger.exception(
            "LLM failed to recommend inventory cars."
        )
        raise