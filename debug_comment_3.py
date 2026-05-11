
import sys
from app import create_app, db
from app.models import User, Event

app = create_app()
with app.test_client() as client:
    with app.app_context():
        # Clean up existing users to be safe
        db.drop_all()
        db.create_all()
        
        user = User(nickname='TestUser', email='test@test.com')
        user.set_password('12345678')
        db.session.add(user)
        db.session.commit()
        
        event = Event(title='Test Event', description='foo', date='2027', time='09:00', location='bar', category='Tech', price_label='Free', price_type='free', creator_id=user.id)
        db.session.add(event)
        db.session.commit()
        
        event_id = event.id

    client.post('/login', data={'email': 'test@test.com', 'password': '12345678'}, follow_redirects=True)
    res = client.get(f'/event/{event_id}')
    import re
    m = re.search(r'name=\x22csrf_token\x22 type=\x22hidden\x22 value=\x22([^\x22]+)\x22', res.data.decode())
    csrf = m.group(1)
    
    data = {'comment': 'Test AJAX 3', 'csrf_token': csrf}
    res2 = client.post(f'/event/{event_id}', data=data, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    })
    print('Status:', res2.status_code)
    print('Data:', res2.data.decode()[:500])

