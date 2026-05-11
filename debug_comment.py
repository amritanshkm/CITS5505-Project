
import sys
from app import create_app, db
from app.models import User, Event

app = create_app()
with app.app_context():
    user = User.query.first()
    event = Event.query.first()
    with app.test_client() as client:
        client.post('/login', data={'email': user.email, 'password': '12345678'})
        res = client.get(f'/event/{event.id}')
        import re
        m = re.search(r'name=\x22csrf_token\x22 type=\x22hidden\x22 value=\x22([^\x22]+)\x22', res.data.decode())
        if not m:
            print('No CSRF found')
            sys.exit(1)
        
        csrf = m.group(1)
        data = {'comment': 'Test AJAX', 'csrf_token': csrf, 'submit': 'Post'}
        
        # Test standard POST first
        res2 = client.post(f'/event/{event.id}', data=data, headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        })
        print(res2.status_code)
        print(res2.data.decode()[:500])

