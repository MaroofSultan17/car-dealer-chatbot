from unittest.mock import patch

from car_chatbot.models import CarSearch
from car_chatbot.search import (
    fallback_car_search,
    recommend_alternatives,
    understand_car_request,
)

def test_fallback_extracts_make_and_model():
    result = fallback_car_search("I want a Toyota Corolla")

    assert result.make == "Toyota"
    assert result.model == "Corolla"


def test_fallback_extracts_make_and_model_from_hybrid_request():
    result = fallback_car_search(
        "I want a Toyota Corolla hybrid"
    )

    assert result.make == "Toyota"
    assert result.model == "Corolla"
    assert result.variant is None

def test_fallback_extracts_bmw_x3():
    result = fallback_car_search("Do you have any BMW X3?")

    assert result.make == "BMW"
    assert result.model == "X3"


def test_fallback_handles_unknown_car():
    result = fallback_car_search("I want a Ferrari SF90")

    assert result.make is None
    assert result.model is None


def test_car_search_with_preferences():
    search = CarSearch(
        preferences=["V8", "sports car"]
    )

    assert search.preferences == ["V8", "sports car"]


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
    mock_extract.side_effect = RuntimeError(
        "Gemini unavailable"
    )

    result, fallback_used = understand_car_request(
        "I want a Toyota Corolla hybrid"
    )

    assert result.make == "Toyota"
    assert result.model == "Corolla"
    assert result.variant is None
    assert fallback_used is True

@patch("car_chatbot.search.recommend_inventory_cars")
def test_recommend_alternatives_returns_ranked_inventory_cars(
    mock_recommend,
):
    mock_recommend.return_value = ["C005", "C012"]

    results = recommend_alternatives(
        "I want a performance car",
        limit=2,
    )

    assert len(results) == 2
    assert results.iloc[0]["car_id"] == "C005"
    assert results.iloc[1]["car_id"] == "C012"

@patch("car_chatbot.search.recommend_inventory_cars")
def test_recommend_alternatives_respects_limit(
    mock_recommend,
):
    mock_recommend.return_value = [
        "C001",
        "C002",
        "C003",
    ]

    results = recommend_alternatives(
        "I want a hybrid car",
        limit=2,
    )

    assert len(results) == 2


@patch("car_chatbot.search.recommend_inventory_cars")
def test_recommend_alternatives_does_not_return_random_cars(
    mock_recommend,
):
    mock_recommend.side_effect = RuntimeError(
        "Recommendation service unavailable"
    )

    results = recommend_alternatives(
        "Nissan",
        limit=3,
    )

    assert results.empty