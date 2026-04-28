from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class ProfileUpdateForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit_profile = SubmitField('Update Profile')

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

from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
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

    price_label = StringField('Price (e.g. Free or $10)', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Create Event')

class AnnouncementForm(FlaskForm):
    content = TextAreaField('Announcement Content', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Post Announcement')
