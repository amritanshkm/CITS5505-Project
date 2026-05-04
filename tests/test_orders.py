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
        assert ev.orders.count() == 1 # Still 1 order!
        
        db.session.delete(ev)
        db.session.commit()
