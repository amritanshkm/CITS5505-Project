import pytest
from datetime import datetime, timedelta
from app.models import User, Event
from app import db


def _create_event(db_session, title, date_str, creator_id):
    ev = Event(
        title=title,
        date=date_str,
        time="10:00",
        location="Perth",
        description="Test event.",
        category="Tech",
        price_label="Free",
        price_type="free",
        lat=-31.9, lng=115.8,
        creator_id=creator_id
    )
    db_session.add(ev)
    db_session.commit()
    return ev


def test_index_no_filter_shows_all_events(client, app):
    """Without any filter, the index page shows all events."""
    with app.app_context():
        u = User(nickname='FilterHost', email='filterhost@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        _create_event(db.session, "Event Alpha", "2027-01-01", u.id)
        _create_event(db.session, "Event Beta", "2027-06-01", u.id)

    response = client.get('/')
    assert response.status_code == 200
    assert b'Event Alpha' in response.data
    assert b'Event Beta' in response.data


def test_index_today_filter(client, app):
    """The 'today' quick filter only shows events for today."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    future_str = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')

    with app.app_context():
        u = User(nickname='TodayHost', email='todayhost@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        _create_event(db.session, "Today Only Event", today_str, u.id)
        _create_event(db.session, "Future Only Event", future_str, u.id)

    response = client.get('/?quick_filter=today')
    assert response.status_code == 200
    html = response.data.decode()
    assert 'Today Only Event' in html
    assert 'Future Only Event' not in html


def test_index_this_week_filter(client, app):
    """The 'this_week' filter shows events within the next 7 days."""
    today = datetime.now().date()
    in_3_days = (today + timedelta(days=3)).strftime('%Y-%m-%d')
    in_30_days = (today + timedelta(days=30)).strftime('%Y-%m-%d')

    with app.app_context():
        u = User(nickname='WeekHost', email='weekhost@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        _create_event(db.session, "This Week Event", in_3_days, u.id)
        _create_event(db.session, "Far Future Event", in_30_days, u.id)

    response = client.get('/?quick_filter=this_week')
    assert response.status_code == 200
    html = response.data.decode()
    assert 'This Week Event' in html
    assert 'Far Future Event' not in html


def test_index_custom_date_filter(client, app):
    """A custom 'from' date filter shows only events on that exact date."""
    target_date = "2028-03-15"
    other_date = "2028-04-20"

    with app.app_context():
        u = User(nickname='CustomDateHost', email='customdate@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        _create_event(db.session, "March Event", target_date, u.id)
        _create_event(db.session, "April Event", other_date, u.id)

    response = client.get(f'/?from={target_date}')
    assert response.status_code == 200
    html = response.data.decode()
    assert 'March Event' in html
    assert 'April Event' not in html
