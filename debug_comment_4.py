
import pytest
from app import create_app, db
from app.models import User, Event

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='creator@test.com').first()
    if not user:
        user = User(nickname='EventCreator2', email='creator2@test.com')
        user.set_password('12345678')
        db.session.add(user)
        db.session.commit()
    
    event = Event(title='PyTest Conf', date='2027', time='09:00', location='bar', description='foo', category='Tech', price_label='Free', price_type='free', lat=-31.0, lng=115.0, creator_id=user.id)
    db.session.add(event)
    db.session.commit()
    event_id = event.id

with app.test_client() as client:
    client.post('/login', data={'email': user.email, 'password': '12345678'}, follow_redirects=True)
    res = client.get(f'/event/{event_id}')
    import re
    m = re.search(r'name=\x22csrf_token\x22 type=\x22hidden\x22 value=\x22([^\x22]+)\x22', res.data.decode())
    csrf = m.group(1)
    
    data = {'comment': 'Test AJAX 4', 'csrf_token': csrf}
    res2 = client.post(f'/event/{event_id}', data=data, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    })
    print('Status:', res2.status_code)
    print('Data:', res2.data.decode()[:500])

