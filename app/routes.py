from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm, ProfileUpdateForm, ChangePasswordForm, CommentForm, CreateEventForm, AnnouncementForm, PaymentForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Event
from app import db

bp = Blueprint('main', __name__)

MOCK_COMMENTS = {}
MOCK_COMMENT_ID_COUNTER = 1

MOCK_ANNOUNCEMENTS = {}

MOCK_COMMENTS = {}
MOCK_COMMENT_ID_COUNTER = 1


@bp.route('/')
@bp.route('/index')
def index():
    events = Event.query.all()
    return render_template('index.html', title='Home', events=events)

@bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    
    is_creator = current_user.is_authenticated and (event.creator_id == current_user.id)
    
    global MOCK_COMMENT_ID_COUNTER
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please login to comment.', 'warning')
            return redirect(url_for('main.login'))
            
        if event_id not in MOCK_COMMENTS:
            MOCK_COMMENTS[event_id] = []
            
        new_comment = {
            "id": MOCK_COMMENT_ID_COUNTER,
            "user_id": current_user.id,
            "user": current_user.nickname,
            "content": form.comment.data,
            "likes": 0
        }
        MOCK_COMMENTS[event_id].append(new_comment)
        MOCK_COMMENT_ID_COUNTER += 1
        flash('Comment posted successfully!', 'success')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    # Get comments and sort by likes descending
    event_comments = MOCK_COMMENTS.get(event_id, [])
    sorted_comments = sorted(event_comments, key=lambda c: c['likes'], reverse=True)
    
    # Get announcements and sort by id descending (newest first)
    event_announcements = MOCK_ANNOUNCEMENTS.get(event_id, [])
    sorted_announcements = sorted(event_announcements, key=lambda a: a['id'], reverse=True)
    
    announcement_form = AnnouncementForm()
    
    return render_template('event_detail.html', title=event.title, event=event, event_id=event_id, 
                           form=form, comments=sorted_comments, is_creator=is_creator, 
                           announcements=sorted_announcements, announcement_form=announcement_form,
                           current_user_id=current_user.id if current_user.is_authenticated else None)

@bp.route('/event/<int:event_id>/comment/<int:comment_id>/like', methods=['POST'])
def like_comment(event_id, comment_id):
    event_comments = MOCK_COMMENTS.get(event_id, [])
    for c in event_comments:
        if c['id'] == comment_id:
            c['likes'] += 1
            break
    return redirect(url_for('main.event_detail', event_id=event_id))

@bp.route('/event/<int:event_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(event_id, comment_id):
    event = Event.query.get_or_404(event_id)
    is_creator = (event.creator_id == current_user.id)
    event_comments = MOCK_COMMENTS.get(event_id, [])
    comment_to_del = next((c for c in event_comments if c['id'] == comment_id), None)
    
    if not comment_to_del:
        flash('Comment not found.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
        
    is_sender = (comment_to_del.get("user_id") == current_user.id)
    if not (is_creator or is_sender):
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
    
    event_comments = MOCK_COMMENTS.get(event_id, [])
    MOCK_COMMENTS[event_id] = [c for c in event_comments if c['id'] != comment_id]
    flash('Comment deleted.', 'info')
    return redirect(url_for('main.event_detail', event_id=event_id))

MOCK_ANNOUNCEMENT_ID_COUNTER = 1

@bp.route('/event/<int:event_id>/announcement/create', methods=['POST'])
@login_required
def create_announcement(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
        
    global MOCK_ANNOUNCEMENT_ID_COUNTER
    form = AnnouncementForm()
    if form.validate_on_submit():
        if event_id not in MOCK_ANNOUNCEMENTS:
            MOCK_ANNOUNCEMENTS[event_id] = []
        MOCK_ANNOUNCEMENTS[event_id].append({
            "id": MOCK_ANNOUNCEMENT_ID_COUNTER,
            "content": form.content.data
        })
        MOCK_ANNOUNCEMENT_ID_COUNTER += 1
        flash('Announcement added!', 'success')
    return redirect(url_for('main.event_detail', event_id=event_id))

@bp.route('/event/<int:event_id>/announcement/<int:ann_id>/delete', methods=['POST'])
@login_required
def delete_announcement(event_id, ann_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))
        
    announcements = MOCK_ANNOUNCEMENTS.get(event_id, [])
    MOCK_ANNOUNCEMENTS[event_id] = [a for a in announcements if a['id'] != ann_id]
    flash('Announcement deleted.', 'info')
    return redirect(url_for('main.event_detail', event_id=event_id))

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.profile'))
        
    form = CreateEventForm()
    if form.validate_on_submit():
        price_val = form.price_label.data.strip()
        if price_val == "0" or price_val.lower() == "free":
            price_label = "Free"
            price_type = "free"
        else:
            price_label = price_val if "$" in price_val else f"${price_val}"
            price_type = "paid"
            
        event.title = form.title.data
        event.date = form.date.data
        event.time = form.time.data
        event.location = form.location.data
        event.description = form.description.data
        event.category = form.category.data
        event.price_label = price_label
        event.price_type = price_type
        event.lat = float(form.lat.data)
        event.lng = float(form.lng.data)
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    if request.method == 'GET':
        form.title.data = event.title
        form.date.data = event.date
        form.time.data = event.time
        form.location.data = event.location
        form.category.data = event.category
        form.price_label.data = "0" if event.price_label == "Free" else event.price_label.replace('$', '')
        form.description.data = event.description
        form.lat.data = event.lat
        form.lng.data = event.lng
        
    return render_template('create_event.html', title='Edit Event', form=form, is_edit=True)

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.profile'))
        
    db.session.delete(event)
    db.session.commit()
        
    flash('Event deleted.', 'success')
    return redirect(url_for('main.profile'))

MOCK_ORDERS = []
MOCK_ORDER_ID_COUNTER = 1000

@bp.route('/event/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    global MOCK_ORDER_ID_COUNTER
    event = Event.query.get_or_404(event_id)
        
    order_id = MOCK_ORDER_ID_COUNTER
    MOCK_ORDER_ID_COUNTER += 1
    
    order = {
        "order_id": order_id,
        "event_id": event.id,
        "event_title": event.title,
        "date": event.date,
        "location": event.location,
        "total": event.price_label,
        "status": "Free Registration"
    }
    MOCK_ORDERS.append(order)
    
    flash('Successfully joined the free event!', 'success')
    return redirect(url_for('main.order_detail', order_id=order_id))

@bp.route('/event/<int:event_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(event_id):
    global MOCK_ORDER_ID_COUNTER
    event = Event.query.get_or_404(event_id)
        
    form = PaymentForm()
    if form.validate_on_submit():
        order_id = MOCK_ORDER_ID_COUNTER
        MOCK_ORDER_ID_COUNTER += 1
        
        order = {
            "order_id": order_id,
            "event_id": event.id,
            "event_title": event.title,
            "date": event.date,
            "location": event.location,
            "total": event.price_label,
            "status": "Paid"
        }
        MOCK_ORDERS.append(order)
        
        flash('Payment Successful! You have joined the event.', 'success')
        return redirect(url_for('main.order_detail', order_id=order_id))
        
    return render_template('payment.html', title='Event Checkout', event=event, form=form)

@bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = next((o for o in MOCK_ORDERS if o['order_id'] == order_id), None)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('main.profile'))
    return render_template('order_detail.html', title='Order Receipt', order=order)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

MOCK_LIKES = [
    {"event": "Startup Pitch Evening", "date": "15 Apr, 2026", "location": "Subiaco"},
    {"event": "Sunset Beach Meetup", "date": "16 Apr, 2026", "location": "Cottesloe Beach"}
]

@bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit():
        price_val = form.price_label.data.strip()
        if price_val == "0" or price_val.lower() == "free":
            price_label = "Free"
            price_type = "free"
        else:
            price_label = price_val if "$" in price_val else f"${price_val}"
            price_type = "paid"
            
        event = Event(
            title=form.title.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            description=form.description.data,
            category=form.category.data,
            price_label=price_label,
            price_type=price_type,
            lat=float(form.lat.data),
            lng=float(form.lng.data),
            creator_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('create_event.html', title='Create Event', form=form, is_edit=False)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileUpdateForm(prefix='profile')
    password_form = ChangePasswordForm(prefix='password')
    
    if profile_form.submit_profile.data and profile_form.validate_on_submit():
        current_user.nickname = profile_form.nickname.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash('Profile information updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    if password_form.submit_password.data and password_form.validate_on_submit():
        if not current_user.check_password(password_form.old_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    if request.method == 'GET':
        profile_form.nickname.data = current_user.nickname
        profile_form.email.data = current_user.email
        
    return render_template('profile.html', 
                           title='My Profile', 
                           profile_form=profile_form, 
                           password_form=password_form,
                           user=current_user,
                           collections=[],
                           likes=[],
                           my_events=current_user.created_events.all(),
                           orders=MOCK_ORDERS)
