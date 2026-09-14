import pytest
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


# --- Tests for search_listings ---

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    # Failure mode: zero matches should return empty list without error
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


# --- Tests for suggest_outfit ---

def test_suggest_outfit_success():
    wardrobe = get_example_wardrobe()
    item = {"title": "Vintage Band Tee", "brand": "Fruit of the Loom", "size": "M", "price": 25}
    outfit = suggest_outfit(item, wardrobe)
    assert isinstance(outfit, str)
    assert len(outfit) > 0


def test_suggest_outfit_empty_wardrobe_handled():
    # Failure mode: empty wardrobe should return styling advice using staples, not crash
    empty_wardrobe = get_empty_wardrobe()
    item = {"title": "Vintage Band Tee", "brand": "Fruit of the Loom", "size": "M", "price": 25}
    outfit = suggest_outfit(item, empty_wardrobe)
    assert isinstance(outfit, str)
    assert len(outfit) > 0


# --- Tests for create_fit_card ---

def test_create_fit_card_success():
    item = {"title": "Faded Band Tee", "price": 22, "platform": "Depop"}
    outfit = "Pair with wide-leg jeans and chunky sneakers."
    fit_card = create_fit_card(outfit, item)
    assert isinstance(fit_card, str)
    assert len(fit_card) > 0


def test_create_fit_card_empty_outfit_handled():
    # Failure mode: empty outfit must be guarded against
    item = {"title": "Faded Band Tee", "price": 22, "platform": "Depop"}
    fit_card = create_fit_card("", item)
    assert "Cannot generate fit card" in fit_card 