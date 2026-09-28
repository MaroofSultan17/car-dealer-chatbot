import logging
import os

from dotenv import load_dotenv
from google import genai

from car_chatbot.models import CarSearch

logger = logging.getLogger(__name__)

load_dotenv()


def get_client() -> genai.Client:
    """Create a Gemini client using the API key from the environment."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    return genai.Client(api_key=api_key)


def extract_car_search(user_message: str) -> CarSearch:
    """Extract car search information from a natural-language request."""
    if not user_message.strip():
        return CarSearch()

    client = get_client()

    prompt = f"""
Extract the car make, model, and variant from the user's request.

Only extract information that the user actually provided.
Do not invent missing information.

Examples:
"I want a Toyota Corolla"
make: Toyota
model: Corolla
variant: null

"I'm looking for a Corolla hybrid"
make: null
model: Corolla
variant: hybrid

"I want a BMW 330i M Sport"
make: BMW
model: 3 Series
variant: 330i M Sport

User request:
{user_message}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": CarSearch,
            },
        )

        if not response.text:
            return CarSearch()

        return CarSearch.model_validate_json(response.text)

    except Exception:
        logger.exception("Gemini failed to extract the car search.")
        raise