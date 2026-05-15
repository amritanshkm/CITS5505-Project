import pytest
import json
from app.models import User, Event
from app import db


def test_map_page_accessible_without_login(client, app):
    """The full map page should be publicly accessible (no login required)."""
    response = client.get('/map')
    assert response.status_code == 200


def test_map_page_returns_event_data(client, app):
    """The map page should embed event coordinate data for all events."""
    with app.app_context():
        u = User(nickname='MapHost', email='maphost@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()

        ev = Event(
            title="Map Test Event",
            date="2027-08-01",
            time="14:00",
            location="Northbridge",
            description="Testing map rendering.",
            category="Art",
            price_label="Free",
            price_type="free",
            lat=-31.945,
            lng=115.860,
            creator_id=u.id
        )
        db.session.add(ev)
        db.session.commit()

    response = client.get('/map')
    assert response.status_code == 200

    html = response.data.decode()
    # The event title and coordinates should be embedded in the page
    assert 'Map Test Event' in html
    assert '-31.945' in html
    assert '115.860' in html


def test_map_page_empty_state(client, app):
    """The map page should render without errors even if there are no events."""
    response = client.get('/map')
    assert response.status_code == 200
    assert b'500' not in response.data
