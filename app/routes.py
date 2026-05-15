from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import (
    LoginForm,
    RegistrationForm,
    ProfileUpdateForm,
    ChangePasswordForm,
    CommentForm,
    CreateEventForm,
    AnnouncementForm,
    PaymentForm,
)
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Event, Comment, Announcement, Order
from app import db
from datetime import datetime

bp = Blueprint('main', __name__)


def wants_json_response():
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.is_json
        or 'application/json' in request.accept_mimetypes
    )


@bp.route('/')
@bp.route('/index')
def index():
    events = Event.query.all()
    return render_template('index.html', title='Home', events=events)


@bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)

    is_creator = current_user.is_authenticated and (event.creator_id == current_user.id)

    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.accept_mimetypes:
                return {'status': 'error', 'message': 'Please login to comment.'}, 401
            flash('Please login to comment.', 'warning')
            return redirect(url_for('main.login'))

        new_comment = Comment(
            content=form.comment.data,
            author=current_user,
            event=event
        )
        db.session.add(new_comment)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or 'application/json' in request.accept_mimetypes:
            avatar_url = url_for('main.user_avatar', user_id=current_user.id) if current_user.avatar else None
            return {
                'status': 'success',
                'comment': {
                    'id': new_comment.id,
                    'content': new_comment.content,
                    'author_id': current_user.id,
                    'author_nickname': current_user.nickname,
                    'author_avatar_url': avatar_url,
                    'author_initial': current_user.nickname[0].upper(),
                    'timestamp': new_comment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'likes': 0
                }
            }
            
        flash('Comment posted successfully!', 'success')
        return redirect(url_for('main.event_detail', event_id=event_id))

    sorted_comments = event.comments.order_by(Comment.timestamp.desc()).all()
    sorted_announcements = event.announcements.order_by(Announcement.timestamp.desc()).all()
    announcement_form = AnnouncementForm()

    attendee_count = event.orders.count()
    like_count = event.liked_by.count()

    spots_left = None
    capacity_reached = False
    if event.capacity is not None:
        spots_left = max(0, event.capacity - attendee_count)
        capacity_reached = spots_left == 0

    user_liked = False
    user_bookmarked = False
    user_joined = False

    if current_user.is_authenticated:
        user_liked = current_user.liked_events.filter_by(id=event.id).count() > 0
        user_bookmarked = current_user.bookmarked_events.filter_by(id=event.id).count() > 0
        user_joined = current_user.orders.filter_by(event_id=event.id).count() > 0

    return render_template(
        'event_detail.html',
        title=event.title,
        event=event,
        event_id=event_id,
        form=form,
        comments=sorted_comments,
        is_creator=is_creator,
        announcements=sorted_announcements,
        announcement_form=announcement_form,
        current_user_id=current_user.id if current_user.is_authenticated else None,
        user_liked=user_liked,
        user_bookmarked=user_bookmarked,
        user_joined=user_joined,
        like_count=like_count,
        attendee_count=attendee_count,
        spots_left=spots_left,
        capacity_reached=capacity_reached
    )


@bp.route('/event/<int:event_id>/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(event_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    already_liked = comment.liked_by.filter_by(id=current_user.id).count() > 0

    if already_liked:
        comment.liked_by.remove(current_user)
        comment.likes = max(0, comment.likes - 1)
        action = 'unliked'
    else:
        comment.liked_by.append(current_user)
        comment.likes += 1
        action = 'liked'

    db.session.commit()

    if wants_json_response():
        return {'status': 'success', 'action': action, 'likes': comment.likes}
    return redirect(url_for('main.event_detail', event_id=event_id))


@bp.route('/event/<int:event_id>/like', methods=['POST'])
@login_required
def like_event(event_id):
    event = Event.query.get_or_404(event_id)
    already_liked = current_user.liked_events.filter_by(id=event.id).count() > 0
    action = 'liked'

    if already_liked:
        current_user.liked_events.remove(event)
        action = 'unliked'
    else:
        current_user.liked_events.append(event)

    db.session.commit()

    if wants_json_response():
        return {
            'status': 'success',
            'action': action,
            'like_count': event.liked_by.count()
        }
    return redirect(url_for('main.event_detail', event_id=event_id))


@bp.route('/event/<int:event_id>/bookmark', methods=['POST'])
@login_required
def bookmark_event(event_id):
    event = Event.query.get_or_404(event_id)
    already_bookmarked = current_user.bookmarked_events.filter_by(id=event.id).count() > 0
    action = 'bookmarked'

    if already_bookmarked:
        current_user.bookmarked_events.remove(event)
        action = 'unbookmarked'
        flash('Event removed from bookmarks.', 'info')
    else:
        current_user.bookmarked_events.append(event)
        flash('Event saved to bookmarks!', 'success')

    db.session.commit()

    if wants_json_response():
        return {'status': 'success', 'action': action}
    return redirect(url_for('main.event_detail', event_id=event_id))


@bp.route('/event/<int:event_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(event_id, comment_id):
    event = Event.query.get_or_404(event_id)
    comment = Comment.query.get_or_404(comment_id)

    if comment.event_id != event.id:
        flash('Comment mismatch.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    is_creator = (event.creator_id == current_user.id)
    is_sender = (comment.user_id == current_user.id)

    if not (is_creator or is_sender):
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('main.event_detail', event_id=event_id))


@bp.route('/event/<int:event_id>/announcement/create', methods=['POST'])
@login_required
def create_announcement(event_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            content=form.content.data,
            event=event
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement added!', 'success')
    return redirect(url_for('main.event_detail', event_id=event_id))


@bp.route('/event/<int:event_id>/announcement/<int:ann_id>/delete', methods=['POST'])
@login_required
def delete_announcement(event_id, ann_id):
    event = Event.query.get_or_404(event_id)
    if event.creator_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    announcement = Announcement.query.get_or_404(ann_id)
    if announcement.event_id != event.id:
        flash('Mismatch warning', 'danger')
        return redirect(url_for('main.event_detail', event_id=event_id))

    db.session.delete(announcement)
    db.session.commit()
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
        event.capacity = form.capacity.data

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
        form.capacity.data = event.capacity

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


@bp.route('/event/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.price_type != 'free':
        if wants_json_response():
            return {
                'status': 'error',
                'message': 'Paid events must be completed through checkout.'
            }, 400
        flash('Paid events must be completed through checkout.', 'warning')
        return redirect(url_for('main.event_detail', event_id=event.id))

    existing_orders = current_user.orders.filter_by(event_id=event.id).all()

    # Leave event if already joined
    if existing_orders:
        for order in existing_orders:
            db.session.delete(order)
        db.session.commit()

        attendee_count = event.orders.count()
        spots_left = None if event.capacity is None else max(0, event.capacity - attendee_count)

        if wants_json_response():
            return {
                'status': 'success',
                'action': 'left',
                'joined': False,
                'attendee_count': attendee_count,
                'spots_left': spots_left,
                'sold_out': spots_left == 0 if spots_left is not None else False
            }

        flash('You have left this event.', 'info')
        return redirect(url_for('main.event_detail', event_id=event.id))

    # Block new joins if sold out
    if event.capacity is not None and event.orders.count() >= event.capacity:
        if wants_json_response():
            return {
                'status': 'error',
                'message': 'Registrations are full for this event.',
                'sold_out': True,
                'attendee_count': event.orders.count(),
                'spots_left': 0
            }, 409

        flash('Registrations are full for this event.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    order = Order(
        user_id=current_user.id,
        event_id=event.id,
        total=event.price_label,
        status="Free Registration"
    )
    db.session.add(order)
    db.session.commit()

    attendee_count = event.orders.count()
    spots_left = None if event.capacity is None else max(0, event.capacity - attendee_count)

    if wants_json_response():
        return {
            'status': 'success',
            'action': 'joined',
            'joined': True,
            'attendee_count': attendee_count,
            'spots_left': spots_left,
            'sold_out': spots_left == 0 if spots_left is not None else False
        }

    flash('Successfully joined the free event!', 'success')
    return redirect(url_for('main.event_detail', event_id=event.id))


@bp.route('/event/<int:event_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(event_id):
    event = Event.query.get_or_404(event_id)

    if event.price_type == 'free':
        flash('This is a free event. Use the join button instead.', 'info')
        return redirect(url_for('main.event_detail', event_id=event.id))

    existing_order = current_user.orders.filter_by(event_id=event.id).first()
    if existing_order:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('main.event_detail', event_id=event.id))

    if event.capacity is not None and event.orders.count() >= event.capacity:
        flash('Tickets are sold out for this event.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    form = PaymentForm()
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            event_id=event.id,
            total=event.price_label,
            status="Paid"
        )
        db.session.add(order)
        db.session.commit()

        flash('Payment Successful! You have joined the event.', 'success')
        return redirect(url_for('main.order_detail', order_id=order.order_id))

    return render_template('payment.html', title='Event Checkout', event=event, form=form)


@bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
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
            capacity=form.capacity.data,
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

        if profile_form.avatar.data:
            avatar_data = profile_form.avatar.data.read()
            if len(avatar_data) > 2 * 1024 * 1024:
                flash('Avatar file is too large! Maximum size is 2MB.', 'danger')
                return redirect(url_for('main.profile'))
            current_user.avatar = avatar_data

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

    return render_template(
        'profile.html',
        title='My Profile',
        profile_form=profile_form,
        password_form=password_form,
        user=current_user,
        collections=current_user.bookmarked_events.all() if current_user.is_authenticated else [],
        likes=current_user.liked_events.all() if current_user.is_authenticated else [],
        my_events=current_user.created_events.all(),
        orders=current_user.orders.order_by(Order.timestamp.desc()).all()
    )


@bp.route('/user/<int:user_id>/avatar')
def user_avatar(user_id):
    from app.models import User
    from flask import current_app
    user = User.query.get_or_404(user_id)
    if user.avatar:
        return current_app.response_class(user.avatar, mimetype='image/jpeg')
    return current_app.response_class(b'', mimetype='image/jpeg')



@bp.route('/my-events')
@login_required
def my_events():
    upcoming_events = []
    past_events = []
    today = datetime.now().date()

    for order in current_user.orders:
        event = order.event
        # Convert string date from database into proper date object
        event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
        if event_date >= today:
            upcoming_events.append(event)
        else:
            past_events.append(event)

    return render_template(
        'my_events.html',
        upcoming_events=upcoming_events,
        past_events=past_events
    )


@bp.route('/saved-events')
@login_required
def saved_events():
    bookmarked_events = current_user.bookmarked_events.all()
    return render_template(
        'saved_events.html',
        events=bookmarked_events
    )
