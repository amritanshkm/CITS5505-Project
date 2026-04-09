from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('base.html', title='Home')

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
