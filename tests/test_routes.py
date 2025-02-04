import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import pytest


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test the "/" route."""
    response = client.get('/')

    assert response.status_code == 200
    assert b'Hello, Arthur!' in response.data
    assert b'Arthur says: Uma vez Flamengo, sempre Flamengo!' in response.data
    assert b'John says: Muita chuva em Natal.' in response.data
    assert b'<div>MiniBlog: <a href="/">Home</a></div>' in response.data
    assert b'<title>Home - MiniBlog</title>' in response.data
