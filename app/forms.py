from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class ProfileUpdateForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit_profile = SubmitField('Update Profile')

    def validate_nickname(self, nickname):
        if nickname.data != current_user.nickname:
            user = User.query.filter_by(nickname=nickname.data).first()
            if user:
                raise ValidationError('Please use a different nickname.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Please use a different email address.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit_password = SubmitField('Change Password')

from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user:
            raise ValidationError('Please use a different nickname.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Please use a different email address.')

class CommentForm(FlaskForm):
    comment = StringField('Add a comment...', validators=[
        DataRequired(), 
        Length(max=500, message="Comment cannot be more than 500 characters.")
    ])
    submit = SubmitField('Post')

class CreateEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=100)])
    date = StringField('Date', render_kw={"type": "date"}, validators=[DataRequired()])
    time = StringField('Time', render_kw={"type": "time"}, validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    lat = HiddenField('Latitude', default="-31.9523")
    lng = HiddenField('Longitude', default="115.8613")
    category = SelectField('Category', choices=[('Tech', 'Tech'), ('Wellness', 'Wellness'), ('Business', 'Business'), ('Social', 'Social'), ('Other', 'Other')], validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional(), NumberRange(min=1)])
    price_label = StringField('Price', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Create Event')

class AnnouncementForm(FlaskForm):
    content = TextAreaField('Announcement Content', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Post Announcement')

class PaymentForm(FlaskForm):
    card_name = StringField('Cardholder Name', validators=[DataRequired(), Length(max=100)])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired(), Length(min=5, max=5)])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=3)])
    submit = SubmitField('Pay Now')

