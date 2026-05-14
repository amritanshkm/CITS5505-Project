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


def test_ajax_event_like_toggle_returns_like_count(client, app):
    """Event like AJAX endpoint should toggle likes and return live like count."""
    with app.app_context():
        creator = User(nickname='LikeHost', email='likehost@test.com')
        creator.set_password('12345678')

        liker = User(nickname='LikeUser', email='likeuser@test.com')
        liker.set_password('12345678')

        db.session.add_all([creator, liker])
        db.session.commit()

        ev = Event(
            title="Like Count Event",
            date="2027-01-01",
            time="12:00",
            location="Perth",
            description="Testing event like count.",
            category="Tech",
            price_label="Free",
            price_type="free",
            lat=-31.0,
            lng=115.0,
            creator_id=creator.id
        )
        db.session.add(ev)
        db.session.commit()
        event_id = ev.id

    client.post(
        '/login',
        data={'email': 'likeuser@test.com', 'password': '12345678'},
        follow_redirects=True
    )

    like_response = client.post(
        f'/event/{event_id}/like',
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    )

    assert like_response.status_code == 200
    assert like_response.is_json

    like_json = like_response.get_json()
    assert like_json['status'] == 'success'
    assert like_json['action'] == 'liked'
    assert like_json['like_count'] == 1

    unlike_response = client.post(
        f'/event/{event_id}/like',
        headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    )

    assert unlike_response.status_code == 200
    assert unlike_response.is_json

    unlike_json = unlike_response.get_json()
    assert unlike_json['status'] == 'success'
    assert unlike_json['action'] == 'unliked'
    assert unlike_json['like_count'] == 0