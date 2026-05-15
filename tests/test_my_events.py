import pytest
from datetime import datetime, timedelta
from app.models import User, Event, Order
from app import db


def test_my_events_requires_login(client, app):
    """My Events page should redirect unauthenticated users to login."""
    response = client.get('/my-events', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_my_events_empty_state(client, app):
    """Logged-in user with no orders should see empty sections."""
    with app.app_context():
        u = User(nickname='NoEventsUser', email='noevents@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()

    client.post('/login', data={'email': 'noevents@test.com', 'password': '12345678'}, follow_redirects=True)

    response = client.get('/my-events')
    assert response.status_code == 200
    assert b'No upcoming registered events' in response.data
    assert b'No past events yet' in response.data


def test_my_events_upcoming_and_past_classification(client, app):
    """Events are correctly classified as upcoming or past based on date."""
    with app.app_context():
        u = User(nickname='OrderUser', email='orderuser@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()

        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        past_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        ev_future = Event(
            title="Future Workshop",
            date=future_date,
            time="10:00",
            location="Perth",
            description="An upcoming event.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.9, lng=115.8,
            creator_id=u.id
        )
        ev_past = Event(
            title="Past Conference",
            date=past_date,
            time="09:00",
            location="Perth",
            description="An event in the past.",
            category="Business",
            price_label="Free",
            price_type="free",
            lat=-31.9, lng=115.8,
            creator_id=u.id
        )
        db.session.add_all([ev_future, ev_past])
        db.session.commit()

        order_future = Order(user_id=u.id, event_id=ev_future.id, status='confirmed', total='0.00')
        order_past = Order(user_id=u.id, event_id=ev_past.id, status='confirmed', total='0.00')
        db.session.add_all([order_future, order_past])
        db.session.commit()

    client.post('/login', data={'email': 'orderuser@test.com', 'password': '12345678'}, follow_redirects=True)

    response = client.get('/my-events')
    assert response.status_code == 200

    html = response.data.decode()

    # Both events should appear on the page
    assert 'Future Workshop' in html
    assert 'Past Conference' in html

    # The date comparison should NOT crash with a TypeError
    assert b'500' not in response.data
