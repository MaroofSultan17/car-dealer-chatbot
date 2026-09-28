from car_chatbot.data import get_car_with_dealer, get_dealer, search_cars


def test_search_car():
    results = search_cars(make="Toyota", model="Corolla")

    assert not results.empty
    assert len(results) == 2
    assert all(results["make"] == "Toyota")
    assert all(results["model"] == "Corolla")


def test_search_is_case_insensitive():
    results = search_cars(make="toyota", model="corolla")

    assert len(results) == 2


def test_search_by_variant():
    results = search_cars(
        make="Toyota",
        model="Corolla",
        variant="Hybrid",
    )

    assert len(results) == 2


def test_car_not_found():
    results = search_cars(
        make="Ferrari",
        model="SF90",
    )

    assert results.empty


def test_get_dealer():
    dealer = get_dealer("D001")

    assert dealer is not None
    assert dealer["name"] == "Utrecht Auto Centre"


def test_invalid_dealer():
    assert get_dealer("D999") is None


def test_car_with_dealer():
    cars = search_cars(
        make="Tesla",
        model="Model 3",
    )

    result = get_car_with_dealer(cars.iloc[0])

    assert result["car"]["model"] == "Model 3"
    assert result["dealer"] is not None
    assert result["dealer"]["name"] == "Amsterdam EV Centre"


from car_chatbot.models import CarSearch


def test_car_search_model():
    search = CarSearch(
        make="Toyota",
        model="Corolla",
        variant="Hybrid",
    )

    assert search.make == "Toyota"
    assert search.model == "Corolla"
    assert search.variant == "Hybrid"


def test_car_search_allows_missing_fields():
    search = CarSearch(model="Corolla")

    assert search.make is None
    assert search.model == "Corolla"
    assert search.variant is None