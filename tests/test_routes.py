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
    assert response.text == 'Hello from MiniBlog!'
