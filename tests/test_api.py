from datetime import datetime
import json
from mock import patch
import pytest

from reviews_app.app import create_app
from reviews_app.resources import get_reviews


# TODO actually test database with a dummy one, currently test is hooked to actual db being used
@pytest.fixture
def client():
    app = create_app()
    app.debug = True
    return app.test_client()


def test_base_get_success(client):
    response = client.get("/reviews")
    assert response.status_code == 200


def test_get_lender_reviews(client):
    response = client.get("/reviews/not-real")
    assert response.status_code == 200
    assert json.loads(response.data) == {"reviews": []}


def test_post_no_body(client):
    response = client.post("/reviews")
    assert response.status_code == 400
    assert json.loads(response.data) == {"message": "search url is required"}


def test_post_wrong_param(client):
    data = '{"wrong_param": "test"}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 400
    assert json.loads(response.data) == {"message": "search url is required"}


def test_post_invalid_url(client):
    data = '{"company_url": "test"}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 404
    assert json.loads(response.data) == {"message": "not a valid url"}


def test_post_bad_url(client):
    data = '{"company_url": "http://eqpoijgelwqje.com"}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "message": "not a valid url"
    }


def test_post_wrong_url(client):
    data = '{"company_url": "http://test.com"}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 404
    assert json.loads(response.data) == {
        "message": "invalid lender url, try getting the correct url for the given lender"
    }


def test_post_success_with_limit(client):
    data = '{"company_url": "https://www.lendingtree.com/reviews/personal/first-midwest-bank/52903183", "limit":10}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 200
    assert len(json.loads(response.data)['reviews']) == 10


def test_post_success(client):
    data = '{"company_url": "https://www.lendingtree.com/reviews/personal/first-midwest-bank/52903183", "limit":10}'
    response = client.post("/reviews", data=data, content_type='application/json')
    assert response.status_code == 200


@pytest.fixture
def mock_response():
    with patch('resources.requests') as m_requests:
        mock_response = m_requests.get.return_value
        yield mock_response


# TODO more url test cases
correct_result_1 = {
                "reviews": [
                    {
                      "author": "Laura from GUSTINE, CA",
                      "content": "The process was quick and easy. Within minutes after I submitted my request I got a email from Carmen Gonzalez. Carmen stayed in contact with me everyday to keep me updated on my loan. Carmen was there for all my questions and made this fast and easy for me. Thank you Carmen.",
                      "date_of_review": datetime(2019, 8, 1, 0, 0),
                      "lender_name": "first-midwest-bank",
                      "recommended": True,
                      "star_rating": 5,
                      "title": "Great Experience"
                    }
                ],
                "status_code": 200
}
success_test = [
    (
        "https://www.lendingtree.com/reviews/personal/first-midwest-bank/52903183", 1,
        correct_result_1
    )
]


@pytest.mark.parametrize("url, limit, expected_result", success_test)
def test_valid_results(url, limit, expected_result):
    result = get_reviews(url, review_limit=limit)
    assert result == expected_result
