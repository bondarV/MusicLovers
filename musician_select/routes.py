import requests
from flask import render_template, request, redirect, url_for, flash, session

from musician_select.forms import RegisterForm, LoginForm
from musician_select.models import User, Musician
from musician_select import db, app
from sqlalchemy import select
from flask_login import login_user, current_user, login_required, logout_user


@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/about')
def about_page():
    return render_template('story.html')


@app.route('/band', methods=['GET', 'POST'])
@login_required
def musician_display():
    if request.method == 'GET':
        musician_name = request.args.get('musician')  # Отримуємо музиканта з параметрів URL
        limit = request.args.get('limit')
    else:
        musician_name = request.form['musician']
        limit = request.form['limit']
    if musician_name:
        response_limited = requests.get(
            f"https://musicbrainz.org/ws/2/artist/?query={musician_name} AND country:*&limit={limit}&fmt=json")
        if response_limited.status_code == 200:
            musicians_data = response_limited.json()
            founded_data = musicians_data.get("count")
            musicians = musicians_data.get('artists', [])
            musicians = [m for m in musicians if m.get('country') != 'RU' and m.get('country') != 'BY']
            if musicians:
                return render_template('band.html', musicians=musicians, musician_name=musician_name, limit=limit,
                                       founded_data=founded_data)
            else:
                return render_template('band.html', limit=limit,
                                       error="Упсс..не було нічого знайдено(можливо вбудований фільтр проти маніпуляцій)",
                                       musician_name=musician_name, founded_data=founded_data)
        else:
            error = "API error: Unable to fetch data."
            return render_template('band.html', error=error)
    return render_template('band.html', musicians=[], error="Не було обрано жодного виконавця")


@app.route('/info', methods=['POST'])
@login_required
def musician_info():
    musician_id = request.form['musician_id']
    print(musician_id)
    q = select(Musician).where(Musician.id == musician_id)
    if db.session.scalar(q) is None :
        musician_retrieved = requests.get(f'https://musicbrainz.org/ws/2/artist/{musician_id}?inc=aliases+genres+tags+ratings&fmt=json').json()
        print(musician_retrieved)
        musician = Musician(id=musician_id,
                            name=musician_retrieved.get('name'),
                            country=musician_retrieved.get('country'),
                            type=musician_retrieved.get('type'),
                            gender=musician_retrieved.get('gender'),
                            disambiguation=musician_retrieved.get('disambiguation'),
                            rating=musician_retrieved['rating'].get('value'),
                            start_singing=musician_retrieved['life-span'].get("begin"),
                            end_singing=musician_retrieved['life-span'].get('end',"2004"),
                            )
        db.session.add(musician)
        db.session.commit()
        q = select(Musician).where(Musician.id == musician_id)
        return render_template('info_musicians.html', musician=db.session.scalar(q))
    return render_template('info_musicians.html', musician=db.session.scalar(q))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Successfully logged in as {user_to_create.username}.", "success")
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was a error with creating user: {err_msg}", "danger")
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f"Successfully logged in as {attempted_user.username}.", "success")
            return redirect(url_for('home_page'))
        else:
            flash(f"Mismatch happened,try again", "danger")
        # user_to_create = User(username=form.username.data,
        #                       email=form.email.data,
        #                       password=form.password1.data)
        # db.session.add(user_to_create)
        # db.session.commit()
        # return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was a error with creating user: {err_msg}", "danger")
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home_page'))


# Dropdown-items for saving and CRUD operations in general!
@app.route("/awful_bands")
@login_required
def awful_bands_page():
    # flash("Logged out successfully.", "success")
    return render_template('awful_bands.html')


@app.route("/favorites_bands")
@login_required
def favorites_bands_page():
    # flash("Logged out successfully.", "success")
    return render_template('favorites_bands.html')


@app.route("/remember_bands")
@login_required
def remember_bands_page():
    # flash("Logged out successfully.", "success")
    return render_template('remember_bands.html')
# @app.route("/info")
# @login_required
# def remember_bands_page():
#     # flash("Logged out successfully.", "success")
#     return render_template('login.html')
