import pytest
from app.models import User, Event, Order
from app import db


def test_order_generation_and_capacity_limits(client, app):
    """Test generating orders securely and validating strict boundary capacities."""
    with app.app_context():
        # Setup users
        creator = User(nickname='Host', email='host@test.com')
        creator.set_password('12345678')
        buyer1 = User(nickname='Buyer1', email='b1@test.com')
        buyer1.set_password('12345678')
        buyer2 = User(nickname='Buyer2', email='b2@test.com')
        buyer2.set_password('12345678')

        db.session.add_all([creator, buyer1, buyer2])
        db.session.commit()

        # Setup Event with Capacity = 1
        ev = Event(
            title="Exclusive Workshop",
            date="2027-01-01",
            time="09:00",
            location="Virtual",
            description="Limited seats available.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.0,
            lng=115.0,
            capacity=1,
            creator_id=creator.id
        )
        db.session.add(ev)
        db.session.commit()

        # Scenario 1: Buyer 1 joins event successfully
        client.post('/login', data={'email': 'b1@test.com', 'password': '12345678'}, follow_redirects=True)
        response1 = client.post(f'/event/{ev.id}/join', follow_redirects=True)
        assert b"Successfully joined the free event" in response1.data

        # Verify order in DB
        assert ev.orders.count() == 1

        client.get('/logout', follow_redirects=True)

        # Scenario 2: Buyer 2 attempts to join, but capacity handles it safely
        client.post('/login', data={'email': 'b2@test.com', 'password': '12345678'}, follow_redirects=True)
        response2 = client.post(f'/event/{ev.id}/join', follow_redirects=True)

        assert b"Registrations are full for this event" in response2.data
        assert ev.orders.count() == 1  # Still 1 order!

        db.session.delete(ev)
        db.session.commit()


def test_ajax_free_event_join_leave_flow_returns_counts(client, app):
    """Free event AJAX join/leave should return JSON state and attendee counts."""
    with app.app_context():
        creator = User(nickname='AjaxJoinHost', email='ajaxjoinhost@test.com')
        creator.set_password('12345678')

        attendee = User(nickname='AjaxJoinUser', email='ajaxjoinuser@test.com')
        attendee.set_password('12345678')

        db.session.add_all([creator, attendee])
        db.session.commit()

        ev = Event(
            title="AJAX Join Event",
            date="2027-01-01",
            time="12:00",
            location="Perth",
            description="Testing AJAX join and leave.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.0,
            lng=115.0,
            capacity=5,
            creator_id=creator.id
        )
        db.session.add(ev)
        db.session.commit()
        event_id = ev.id

    client.post(
        '/login',
        data={'email': 'ajaxjoinuser@test.com', 'password': '12345678'},
        follow_redirects=True
    )

    join_response = client.post(
        f'/event/{event_id}/join',
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    )

    assert join_response.status_code == 200
    assert join_response.is_json

    join_json = join_response.get_json()
    assert join_json['status'] == 'success'
    assert join_json['action'] == 'joined'
    assert join_json['joined'] is True
    assert join_json['attendee_count'] == 1
    assert join_json['spots_left'] == 4
    assert join_json['sold_out'] is False

    with app.app_context():
        assert Order.query.filter_by(event_id=event_id).count() == 1

    leave_response = client.post(
        f'/event/{event_id}/join',
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    )

    assert leave_response.status_code == 200
    assert leave_response.is_json

    leave_json = leave_response.get_json()
    assert leave_json['status'] == 'success'
    assert leave_json['action'] == 'left'
    assert leave_json['joined'] is False
    assert leave_json['attendee_count'] == 0
    assert leave_json['spots_left'] == 5
    assert leave_json['sold_out'] is False

    with app.app_context():
        assert Order.query.filter_by(event_id=event_id).count() == 0