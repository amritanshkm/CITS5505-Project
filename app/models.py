from datetime import datetime, timezone
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association Tables for Many-to-Many Relationships
user_bookmarks = db.Table('user_bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

user_event_likes = db.Table('user_event_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

user_comment_likes = db.Table('user_comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    join_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    avatar = db.Column(db.LargeBinary, nullable=True)

    # Relationships (One-to-Many)
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    # Relationships (Many-to-Many)
    bookmarked_events = db.relationship('Event', secondary=user_bookmarks,
                                        backref=db.backref('bookmarked_by', lazy='dynamic'), lazy='dynamic')
    liked_events = db.relationship('Event', secondary=user_event_likes,
                                   backref=db.backref('liked_by', lazy='dynamic'), lazy='dynamic')
    liked_comments = db.relationship('Comment', secondary=user_comment_likes,
                                     backref=db.backref('liked_by', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

from app import login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price_type = db.Column(db.String(20), nullable=False)
    price_label = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(30), nullable=False)
    location = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=True) # Null if unlimited
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    @property
    def coords(self):
        return [self.lat, self.lng]

    # Relationships
    announcements = db.relationship('Announcement', backref='event', lazy='dynamic', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='event', lazy='dynamic', cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='event', lazy='dynamic', cascade="all, delete-orphan")

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), nullable=False)
    total = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
