
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
        csrf = m.group(1)
        data = {'comment': 'Test AJAX 2', 'csrf_token': csrf} # No submit
        res2 = client.post(f'/event/{event.id}', data=data, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        print('Status:', res2.status_code)
        if res2.status_code == 200 and b'Test AJAX 2' in res2.data:
            print('Returned HTML instead of JSON? Oh wait, validate_on_submit() failed.')
        else:
            print('Success JSON' if res2.is_json else 'HTML')

