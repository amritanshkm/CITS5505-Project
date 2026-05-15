import pytest
from app.models import User, Event
from app import db


def test_saved_events_requires_login(client, app):
    """Saved events page should redirect unauthenticated users to login."""
    response = client.get('/saved-events', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_saved_events_empty_state(client, app):
    """Logged-in user with no bookmarks should see the empty-state UI."""
    with app.app_context():
        u = User(nickname='EmptyBookmarker', email='empty@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()

    client.post('/login', data={'email': 'empty@test.com', 'password': '12345678'}, follow_redirects=True)

    response = client.get('/saved-events')
    assert response.status_code == 200
    assert b'No Saved Events Yet' in response.data


def test_saved_events_shows_bookmarked_event(client, app):
    """Logged-in user with a bookmark should see that event on the saved events page."""
    with app.app_context():
        u = User(nickname='BookmarkUser', email='bookmarked@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()

        ev = Event(
            title="Bookmarked Yoga Session",
            date="2027-06-01",
            time="08:00",
            location="Perth",
            description="A relaxing yoga session by the beach.",
            category="Health",
            price_label="Free",
            price_type="free",
            lat=-31.9,
            lng=115.8,
            creator_id=u.id
        )
        db.session.add(ev)
        db.session.commit()

        # Bookmark the event
        u.bookmarked_events.append(ev)
        db.session.commit()

    client.post('/login', data={'email': 'bookmarked@test.com', 'password': '12345678'}, follow_redirects=True)

    response = client.get('/saved-events')
    assert response.status_code == 200
    assert b'Bookmarked Yoga Session' in response.data
    assert b'No Saved Events Yet' not in response.data
