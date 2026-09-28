from unittest.mock import patch

from car_chatbot.models import CarSearch
from car_chatbot.search import fallback_car_search, understand_car_request


def test_fallback_extracts_make_and_model():
    result = fallback_car_search("I want a Toyota Corolla")

    assert result.make == "Toyota"
    assert result.model == "Corolla"


def test_fallback_extracts_hybrid():
    result = fallback_car_search("I want a Toyota Corolla hybrid")

    assert result.make == "Toyota"
    assert result.model == "Corolla"
    assert result.variant == "hybrid"


def test_fallback_extracts_bmw_x3():
    result = fallback_car_search("Do you have any BMW X3?")

    assert result.make == "BMW"
    assert result.model == "X3"


def test_fallback_handles_unknown_car():
    result = fallback_car_search("I want a Ferrari SF90")

    assert result.make is None
    assert result.model is None


@patch("car_chatbot.search.extract_car_search")
def test_uses_gemini_when_available(mock_extract):
    mock_extract.return_value = CarSearch(
        make="Tesla",
        model="Model 3",
    )

    result, fallback_used = understand_car_request(
        "I want a Tesla Model 3"
    )

    assert result.make == "Tesla"
    assert result.model == "Model 3"
    assert fallback_used is False


@patch("car_chatbot.search.extract_car_search")
def test_falls_back_when_gemini_fails(mock_extract):
    mock_extract.side_effect = RuntimeError("Gemini unavailable")

    result, fallback_used = understand_car_request(
        "I want a Toyota Corolla hybrid"
    )

    assert result.make == "Toyota"
    assert result.model == "Corolla"
    assert result.variant == "hybrid"
    assert fallback_used is True