import pytest
from fastapi.testclient import TestClient

from car_chatbot.main import app

SEARCH_URL = "/api/v1/cars/search"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    test_client = TestClient(app)

    return test_client


def test_search_returns_matching_cars_with_dealer(client):
    response = client.post(SEARCH_URL, json={"message": "I want a Toyota Corolla"})
    search_response = response.json()

    assert response.status_code == 200
    assert len(search_response["cars"]) > 0

    for car in search_response["cars"]:
        assert car["make"] == "Toyota"
        assert car["model"] == "Corolla"
        assert car["dealer"]["name"]

    assert search_response["cars"][0]["priceInCents"] == 3290000


def test_search_for_unknown_car_returns_no_cars_and_a_warning(client):
    response = client.post(SEARCH_URL, json={"message": "Ferrari SF90"})
    search_response = response.json()

    assert response.status_code == 200
    assert search_response["cars"] == []
    assert search_response["notices"][0]["level"] == "warning"


def test_extra_fields_are_ignored(client):
    response = client.post(
        SEARCH_URL,
        json={"message": "Toyota Corolla", "priceInCents": 1},
    )

    assert response.status_code == 200
    assert response.json()["cars"][0]["priceInCents"] == 3290000


@pytest.mark.parametrize(
    "request_body",
    [{}, {"message": ""}, {"message": "   "}, {"message": 123}, {"message": "a" * 501}],
)
def test_invalid_payload_returns_422(client, request_body):
    response = client.post(SEARCH_URL, json=request_body)

    assert response.status_code == 422


def test_wrong_method_returns_405(client):
    response = client.get(SEARCH_URL)

    assert response.status_code == 405


def test_post_that_is_not_json_returns_415(client):
    response = client.post(
        SEARCH_URL,
        content="message=Toyota",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415


def test_responses_send_security_headers(client):
    response = client.post(SEARCH_URL, json={"message": "Toyota Corolla"})

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"
