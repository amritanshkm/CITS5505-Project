import pytest
from app.models import User, Event, Comment, Announcement
from app import db

def test_create_event_in_db(client, app):
    """Test standard Event CRUD backend logic."""
    with app.app_context():
        u = User(nickname='EventCreator', email='creator@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        
        # Test Create
        ev = Event(
            title="PyTest Conference",
            date="2027-01-01",
            time="09:00",
            location="Virtual",
            description="Testing events programmatically.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.0,
            lng=115.0,
            creator_id=u.id
        )
        db.session.add(ev)
        db.session.commit()
        
        # Phase 4 Test Addition: Discussion Board and N:N relations
        db.session.refresh(ev)
        
        c = Comment(content="This is awesome!", author=u, event=ev)
        a = Announcement(content="Event starting soon!", event=ev)
        
        u.bookmarked_events.append(ev)
        
        db.session.add(c)
        db.session.add(a)
        db.session.commit()
        
        # Verify nested properties
        assert ev.comments.count() == 1
        assert ev.announcements.count() == 1
        assert u.bookmarked_events.count() == 1
        assert ev.comments[0].content == "This is awesome!"
        
        # Test Read
        fetched = Event.query.filter_by(title="PyTest Conference").first()
        assert fetched is not None
        assert fetched.coords == [-31.0, 115.0]
        
        # Test Update
        fetched.title = "Updated Conference"
        db.session.commit()
        fetched_updated = Event.query.get(fetched.id)
        assert fetched_updated.title == "Updated Conference"
        
        # Test Delete
        db.session.delete(fetched_updated)
        db.session.commit()
        assert Event.query.count() == 0

def test_ajax_comment_submission(client, app):
    """Test posting a comment via AJAX (Phase 4 fix)."""
    with app.app_context():
        u = User(nickname='AjaxCommenter', email='ajax@test.com')
        u.set_password('12345678')
        db.session.add(u)
        db.session.commit()
        
        ev = Event(
            title="AJAX Event",
            date="2027-01-01",
            time="09:00",
            location="Virtual",
            description="Testing events programmatically.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.0,
            lng=115.0,
            creator_id=u.id
        )
        db.session.add(ev)
        db.session.commit()
        event_id = ev.id
        
    client.post('/login', data={'email': 'ajax@test.com', 'password': '12345678'}, follow_redirects=True)
    
    # Get CSRF
    res = client.get(f'/event/{event_id}')
    import re
    m = re.search(r'name="csrf_token".*?value="([^"]+)"', res.data.decode())
    app.config["WTF_CSRF_ENABLED"] = False
    csrf = "dummy"
    
    # Post Comment
    data = {'comment': 'Test AJAX Comment', 'csrf_token': csrf}
    res2 = client.post(f'/event/{event_id}', data=data, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    })
    
    print("STATUS:", res2.status_code)
    print("RESPONSE:", res2.data.decode())
    
    assert res2.status_code == 200
    assert res2.is_json
    
    json_data = res2.get_json()
    assert json_data['status'] == 'success'
    assert json_data['comment']['content'] == 'Test AJAX Comment'





