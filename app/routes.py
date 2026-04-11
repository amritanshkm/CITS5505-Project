from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm, ProfileUpdateForm, ChangePasswordForm

bp = Blueprint('main', __name__)

EVENTS = [
    {
        "title": "Tech Networking Night",
        "date": "12 Apr",
        "time": "6:00 PM",
        "location": "Perth CBD",
        "description": "Meet developers, designers, and founders for an evening of networking and startup conversations.",
        "category": "Tech",
        "price_label": "Free",
        "price_type": "free",
        "coords": [-31.9523, 115.8613],
    },
    {
        "title": "Beginner Yoga in the Park",
        "date": "13 Apr",
        "time": "8:00 AM",
        "location": "Kings Park",
        "description": "A relaxed outdoor yoga session for beginners. Bring a mat, water bottle, and a friend.",
        "category": "Wellness",
        "price_label": "$10",
        "price_type": "paid",
        "coords": [-31.9617, 115.8327],
    },
    {
        "title": "Startup Pitch Evening",
        "date": "15 Apr",
        "time": "7:00 PM",
        "location": "Subiaco",
        "description": "Watch early-stage founders pitch ideas, connect with mentors, and explore local startup opportunities.",
        "category": "Business",
        "price_label": "$15",
        "price_type": "paid",
        "coords": [-31.9478, 115.8233],
    },
    {
        "title": "Sunset Beach Meetup",
        "date": "16 Apr",
        "time": "5:30 PM",
        "location": "Cottesloe Beach",
        "description": "Casual beach meetup with games, snacks, and a chance to make new friends while watching the sunset.",
        "category": "Social",
        "price_label": "Free",
        "price_type": "free",
        "coords": [-31.9937, 115.7528],
    },
]

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home', events=EVENTS)

@bp.route('/event/<int:event_id>')
def event_detail(event_id):
    if event_id < 0 or event_id >= len(EVENTS):
        flash('Event not found', 'danger')
        return redirect(url_for('main.index'))
    event = EVENTS[event_id]
    return render_template('event_detail.html', title=event['title'], event=event, event_id=event_id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # TODO: integrate with actual User model handling
        flash('Login successful (mock)!', 'success')
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # TODO: integrate with actual User model and db.session.commit()
        flash('Registration successful (mock)!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    # TODO: integrate with flask_login
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

MOCK_USER = {
    "nickname": "AgileDev",
    "email": "agile@uwa.edu.au"
}

MOCK_COLLECTIONS = [
    {"event": "Tech Networking Night", "date": "12 Apr, 2026", "location": "Perth CBD"},
    {"event": "Beginner Yoga in the Park", "date": "13 Apr, 2026", "location": "Kings Park"}
]

MOCK_LIKES = [
    {"event": "Startup Pitch Evening", "date": "15 Apr, 2026", "location": "Subiaco"},
    {"event": "Sunset Beach Meetup", "date": "16 Apr, 2026", "location": "Cottesloe Beach"}
]

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    profile_form = ProfileUpdateForm(prefix='profile')
    password_form = ChangePasswordForm(prefix='password')
    
    if profile_form.submit_profile.data and profile_form.validate():
        MOCK_USER['nickname'] = profile_form.nickname.data
        MOCK_USER['email'] = profile_form.email.data
        flash('Profile information updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    if password_form.submit_password.data and password_form.validate():
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    if request.method == 'GET':
        profile_form.nickname.data = MOCK_USER['nickname']
        profile_form.email.data = MOCK_USER['email']
        
    return render_template('profile.html', 
                           title='My Profile', 
                           profile_form=profile_form, 
                           password_form=password_form,
                           user=MOCK_USER,
                           collections=MOCK_COLLECTIONS,
                           likes=MOCK_LIKES)
