from datetime import datetime

import data
import requests
from sqlalchemy import and_
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import select, exists, func
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.orm import selectinload

from musician_select.forms import RegisterForm, LoginForm
from musician_select.models import User, Musician, Alias, URL, Record, Genre, UserRecord, ReactionType, \
    UserMusicianReaction
from musician_select import db, app


@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')


def add_musician_to_db(musician_id):
    """Додає музиканта в базу даних, якщо його ще немає."""
    musician_retrieved = requests.get(
        f'https://musicbrainz.org/ws/2/artist/{musician_id}?inc=aliases+genres+tags+ratings+url-rels&fmt=json'
    ).json()

    retrieve_genres = musician_retrieved.get('genres')
    genre_objects = []

    if retrieve_genres:
        for genre in retrieve_genres:
            genre_id = genre.get('id')
            q = select(Genre).where(Genre.id == genre.get("id"))
            if not db.session.scalar(q):
                new_genre = Genre(id=genre_id, name=genre.get("name"))
                db.session.add(new_genre)
                db.session.commit()
            genre_objects.append(db.session.scalar(q))

    musician = Musician(
        id=musician_id,
        name=musician_retrieved.get('name'),
        country=musician_retrieved.get('country'),
        type=musician_retrieved.get('type'),
        gender=musician_retrieved.get('gender'),
        disambiguation=musician_retrieved.get('disambiguation'),
        rating=musician_retrieved['rating'].get('value') if musician_retrieved.get('rating') else None,
        start_singing=normalize_data(musician_retrieved['life-span'].get("begin")),
        end_singing=normalize_data(musician_retrieved['life-span'].get('end')),
    )
    db.session.add(musician)
    musician.genres = genre_objects
    db.session.commit()

    if musician_retrieved.get('aliases', []):
        for alias in musician_retrieved.get('aliases', []):
            alias = Alias(name=alias.get('name'), musician_id=musician_id)
            db.session.add(alias)
            db.session.commit()

    if musician_retrieved.get('relations', []):
        for relation in musician_retrieved.get('relations', []):
            url_id = relation['url'].get('id')
            exists_query = db.session.execute(
                select(func.count()).select_from(URL).filter_by(id=url_id)
            ).scalar()
            if exists_query:
                continue
            url = URL(id=url_id, resource=relation['url'].get('resource'), musician_id=musician_id)
            db.session.add(url)
            db.session.commit()

    return musician


@app.route('/musician_display', methods=['GET', 'POST'])
@login_required
def musician_display():
    if request.method == 'GET':
        # Отримуємо параметри з URL або з сесії
        musician_name = request.args.get('musician') or session.get('musician_name')
        limit = request.args.get('limit') or session.get('limit')
    else:
        # Отримуємо параметри з форми
        musician_name = request.form.get('musician') or session.get('musician_name')
        limit = request.form.get('limit') or session.get('limit')
        session['musician_name'] = musician_name
        session['limit'] = limit

    # Додаткові фільтри
    alias = request.args.get('alias')
    primary_alias = request.args.get('primary_alias')
    area = request.args.get('area')
    country = request.args.get('country')
    gender = request.args.get('gender')
    artist_type = request.args.get('type')

    query_params = []
    if musician_name:
        query_params.append(f"artist:{musician_name}")
    if alias:
        query_params.append(f"alias:{alias}")
    if primary_alias:
        query_params.append(f"primary_alias:{primary_alias}")
    if area:
        query_params.append(f"area:{area}")
    if country:
        query_params.append(f"country:{country}")
    if gender:
        query_params.append(f"gender:{gender}")
    if artist_type:
        query_params.append(f"type:{artist_type}")

    query = " AND ".join(query_params)

    if musician_name:
        response_limited = requests.get(
            f"https://musicbrainz.org/ws/2/artist/?query={query}&limit={limit}&inc=aliases+genres+tags+ratings+url-rels&fmt=json"
        )
        if response_limited.status_code == 200:
            musicians_data = response_limited.json()
            founded_data = musicians_data.get("count")
            musicians = musicians_data.get('artists', [])
            musicians = [m for m in musicians if m.get('country') != 'RU' and m.get('country') != 'BY']
            if musicians:
                final_dictionary_of_request = {}
                for musician in musicians:
                    # is_checked = db.session.query(Record.id).join(Musician.users).filter(
                    #     and_(User.id == current_user.id, Musician.id == musician.get("id"))
                    # ).first() is not None
                    user_reactions = db.session.query(ReactionType).join(ReactionType.users).join(
                        ReactionType.musicians).filter(
                        User.id == current_user.id,
                        Musician.id == musician.get("id")
                    ).all()

                    final_dictionary_of_request[musician.get("id")] = {
                        'musician': musician,
                        'choices': user_reactions,
                    }
                print(final_dictionary_of_request)
                return render_template('musician_display.html', musicians_data=final_dictionary_of_request,
                                       musician_name=musician_name,
                                       limit=limit,
                                       founded_data=founded_data)
            else:
                return render_template('musician_display.html', limit=limit,
                                       error="Упсс..не було нічого знайдено(можливо вбудований фільтр проти маніпуляцій)",
                                       musician_name=musician_name, founded_data=founded_data)
        else:
            error = "API error: Unable to fetch data."
            return render_template('musician_display.html', error=error)
    return render_template('musician_display.html', musicians_data=[], error="Не було обрано жодного виконавця")


from sqlalchemy import insert
from sqlalchemy import delete


def normalize_data(date_str):
    if date_str is not None and len(date_str) == 4:
        return datetime.strptime(date_str, '%Y').date().replace(month=1, day=1)
    if date_str is not None and len(date_str) == 10:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    if date_str is not None and len(date_str) == 7:
        return datetime.strptime(date_str, '%Y-%m').date().replace(day=1)
    return None


@app.route("/update-reaction", methods=['POST'])
@login_required
def update_reaction():
    data = request.get_json()
    print(data)
    is_checked = data.get('is_checked')
    musician_id = data.get('musician_id')
    user_id = current_user.id
    reaction_value = data.get('reaction_value')

    if reaction_value not in ['following', 'adoring', 'hating']:
        return jsonify({'error': 'Invalid reaction value'}), 400

    try:
        # Перевірка існування музиканта в базі даних
        musician = db.session.query(Musician).filter_by(id=musician_id).first()
        if musician is None:
            musician = add_musician_to_db(musician_id)

        reaction_type = db.session.query(ReactionType).filter_by(name=reaction_value).first()
        if not reaction_type:
            return jsonify({'error': 'Reaction type not found'}), 400

        existing_reaction = db.session.query(UserMusicianReaction).filter_by(
            user_id=user_id,
            musician_id=musician_id,
            reaction_type_id=reaction_type.id
        ).first()

        # Логіка для видалення протилежної реакції
        if reaction_value == 'adoring':
            opposite_reaction_type = db.session.query(ReactionType).filter_by(name='hating').first()
            if opposite_reaction_type:
                db.session.execute(delete(UserMusicianReaction).where(
                    UserMusicianReaction.c.user_id == user_id,
                    UserMusicianReaction.c.musician_id == musician_id,
                    UserMusicianReaction.c.reaction_type_id == opposite_reaction_type.id
                ))
        elif reaction_value == 'hating':
            opposite_reaction_type = db.session.query(ReactionType).filter_by(name='adoring').first()
            if opposite_reaction_type:
                db.session.execute(delete(UserMusicianReaction).where(
                    UserMusicianReaction.c.user_id == user_id,
                    UserMusicianReaction.c.musician_id == musician_id,
                    UserMusicianReaction.c.reaction_type_id == opposite_reaction_type.id
                ))

        if is_checked:
            if existing_reaction is None:
                new_reaction = UserMusicianReaction.insert().values(
                    user_id=user_id,
                    musician_id=musician_id,
                    reaction_type_id=reaction_type.id
                )
                db.session.execute(new_reaction)
                print(f"Added new reaction: {new_reaction}")
        else:
            if existing_reaction:
                print(f"Deleting existing reaction: {existing_reaction}")
                db.session.execute(delete(UserMusicianReaction).where(
                    UserMusicianReaction.c.user_id == user_id,
                    UserMusicianReaction.c.musician_id == musician_id,
                    UserMusicianReaction.c.reaction_type_id == reaction_type.id
                ))

        db.session.commit()

        return jsonify({'message': 'Reaction updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/remove-reaction", methods=['POST'])
@login_required
def remove_reaction():
    data = request.get_json()
    musician_id = data.get('musician_id')
    user_id = current_user.id

    try:
        # Check for existing 'adoring' and 'hating' reactions and remove them
        remove_reactions(user_id, musician_id)

        db.session.commit()

        return jsonify({'message': 'Reactions removed successfully', 'musician_id': musician_id}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


def remove_reactions(user_id, musician_id):
    # Remove 'adoring' and 'hating' reactions for the given user and musician
    adoring = db.session.query(ReactionType).filter_by(name='adoring').first()
    hating = db.session.query(ReactionType).filter_by(name='hating').first()

    if adoring:
        db.session.execute(delete(UserMusicianReaction).where(
            UserMusicianReaction.c.user_id == user_id,
            UserMusicianReaction.c.musician_id == musician_id,
            UserMusicianReaction.c.reaction_type_id == adoring.id
        ))
    if hating:
        db.session.execute(delete(UserMusicianReaction).where(
            UserMusicianReaction.c.user_id == user_id,
            UserMusicianReaction.c.musician_id == musician_id,
            UserMusicianReaction.c.reaction_type_id == hating.id
        ))
    print(f"Removed 'adoring' and 'hating' reactions for user {user_id} and musician {musician_id}")


@app.route('/info', methods=['POST'])
@login_required
def musician_info():
    # Перевірка наявності musician_id у формі
    musician_id = request.form.get('musician_id')
    if not musician_id:
        return "Musician ID is required", 400

    # Запит до бази даних для перевірки наявності музиканта
    q = select(Musician).where(Musician.id == musician_id)
    musician = db.session.scalar(q)

    # Якщо музикант не знайдений, додати його до бази даних
    if musician is None:
        musician = add_musician_to_db(musician_id)
    else:
        try:
            # Отримання даних музиканта з MusicBrainz
            musician_retrieved = requests.get(
                f'https://musicbrainz.org/ws/2/artist/{musician_id}?inc=aliases+genres+tags+ratings+url-rels&fmt=json'
            ).json()
        except requests.exceptions.RequestException as e:
            # Обробка помилки запиту
            return f"Error retrieving data: {e}"

        # Оновлення даних, якщо вони змінилися
        if musician_retrieved.get('disambiguation') != musician.disambiguation:
            musician.disambiguation = musician_retrieved.get('disambiguation')
            db.session.commit()

        if musician_retrieved.get('life-span', {}).get('end') != musician.end_singing:
            musician.end_singing = normalize_data(musician_retrieved.get('life-span', {}).get('end'))
            db.session.commit()

        if musician_retrieved.get('rating', {}).get('value') != musician.rating:
            musician.rating = musician_retrieved.get('rating', {}).get('value')
            db.session.commit()

    # Запит на отримання підписаних пісень для цього музиканта
    q = select(Record).join(Record.users).filter(
        and_(User.id == current_user.id, Record.musician_id == musician_id)
    )
    all_subscribed_songs = db.session.scalars(q).all()

    # Повернення результатів у шаблон
    return render_template(
        'info_musicians.html',
        musician=musician,
        all_subscribed_songs=all_subscribed_songs
    )


import requests


@app.route('/add_record_to_user', methods=['POST'])
@login_required
def add_record_to_user():
    data = request.get_json()
    record_id = data.get('record_id')
    user_id = current_user.id
    is_checked = data.get('is_checked')
    print(user_id)
    if not record_id:
        return jsonify({"message": "Record ID is required."}), 400

    # Fetch record data if checked
    if is_checked:
        response = requests.get(
            f"https://musicbrainz.org/ws/2/recording/{record_id}?inc=artist-credits+isrcs+releases&fmt=json"
        )
        if response.status_code != 200:
            return jsonify({"message": "Failed to fetch record data."}), 400

        record_data = response.json()

        # Check if record exists, otherwise create
        record_exist = db.session.query(Record).filter_by(id=record_id).first()
        if not record_exist:
            # Extract musician information safely
            musician_id = record_data.get("artist-credit", [{}])[0].get("artist", {}).get("id")
            if not musician_id:
                return jsonify({"message": "Musician information is missing."}), 400

            if not record_data.get("title"):
                return jsonify({"message": "Record title is missing."}), 400

            record = Record(
                id=record_id,
                title=record_data.get("title"),
                disambiguation=record_data.get("disambiguation"),
                release_date=record_data.get("release-date"),
                musician_id=musician_id,
            )
            db.session.add(record)
            db.session.commit()
        else:
            record = record_exist

        # Find the user
        find_user = db.session.query(User).filter_by(id=user_id).first()
        if not find_user:
            return jsonify({"message": "User not found."}), 404

        if record in find_user.records:
            return jsonify({"message": "Record already added."}), 400

        # Add the record to the user's records
        find_user.records.append(record)
        db.session.commit()
        return jsonify({'success': True, 'record_id': record_id, 'record_title': record.title})

    # When is_checked is False, we need to remove the record
    find_user = db.session.query(User).filter_by(id=user_id).first()
    if not find_user:
        return jsonify({"message": "User not found."}), 404

    record_to_remove = db.session.query(Record).filter_by(id=record_id).first()
    if record_to_remove:
        # Check if the record exists in the user's list of records
        if record_to_remove in find_user.records:
            # Remove the record from the user's records
            find_user.records.remove(record_to_remove)
            db.session.commit()  # Commit the changes after removing the record
            return jsonify({'record_id': record_id, "success": True, "message": "Record removed successfully!"}), 200
        else:
            return jsonify({"message": "Record not found in user's records."}), 404
    else:
        return jsonify({"message": "Record not found."}), 404


@app.route('/search_records', methods=['GET'])
@login_required
def search_records():
    musician_id = request.args.get('musician_id')
    search_engine_text = request.args.get('search_engine_text')

    # Перевірка на порожній запит
    if not musician_id and not search_engine_text:
        return jsonify({'records': []})

    response = requests.get(
        f"https://musicbrainz.org/ws/2/recording?query=arid:{musician_id}+AND+recording:{search_engine_text}&inc=artist-credits&limit=5&fmt=json")

    # Перевірка статусу відповіді
    if response.status_code != 200:
        return jsonify({'records': []})

    data = response.json()
    user_id = session.get('user_id')
    # Формування результатів
    result = []
    for recording in data['recordings']:
        # Check if the user has subscribed to this recording
        record_id = recording['id']
        is_checked = False

        # Assuming `current_user` is a Flask-Login user and has a relationship with the `Record` model
        if current_user.is_authenticated:
            user_records = current_user.records
            if any(record.id == record_id for record in user_records):
                is_checked = True

        result.append({
            'id': recording['id'],
            'title': recording['title'],
            'is_checked': is_checked
        })

    return jsonify({'records': result})


@app.route('/remove_record_from_user', methods=['POST'])
@login_required
def remove_record_from_user():
    data = request.get_json()
    record_id = data.get('record_id')
    user_id = current_user.id

    if not record_id or not user_id:
        return jsonify({"message": "Record ID and User ID are required."}), 400

    # Знайти користувача
    find_user = db.session.query(User).filter_by(id=user_id).first()
    if not find_user:
        return jsonify({"message": "User not found."}), 404

    # Знайти запис
    record_to_remove = db.session.query(Record).filter_by(id=record_id).first()
    if not record_to_remove:
        return jsonify({"message": "Record not found."}), 404

    # Видалити зв'язок між користувачем і записом
    find_user.records.remove(record_to_remove)
    db.session.commit()  # Зберегти зміни

    return jsonify({"message": "Record removed from user successfully", "record_id": record_id}), 200


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
            flash(f"There was an error with creating user: {err_msg}", "danger")
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
            flash(f"Mismatch happened, try again", "danger")
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was an error with login: {err_msg}", "danger")
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home_page'))


@app.route("/awful_bands")
@login_required
def awful_bands_page():
    current_user_id = current_user.id
    # Використовуємо scalar() для отримання одиничного значення
    hating_reaction_id = db.session.query(ReactionType.id).filter(ReactionType.name == 'hating').scalar()

    if hating_reaction_id:
        # Фільтруємо за реакцією "hating" у таблиці UserMusicianReaction
        awful_musicians = db.session.query(Musician).join(
            UserMusicianReaction, Musician.id == UserMusicianReaction.c.musician_id
        ).filter(
            UserMusicianReaction.c.reaction_type_id == hating_reaction_id,
            UserMusicianReaction.c.user_id == current_user_id
        ).all()

        return render_template('awful_bands.html', musicians=awful_musicians)




@app.route("/favorites_bands")
@login_required
def favorites_bands_page():
    current_user_id = current_user.id
    # Отримуємо id реакції "adoring"
    adoring_reaction_id = db.session.query(ReactionType.id).filter(ReactionType.name == 'adoring').scalar()

    if adoring_reaction_id:
        # Фільтруємо за реакцією "adoring" у таблиці UserMusicianReaction
        favorite_musicians = db.session.query(Musician).join(
            UserMusicianReaction, Musician.id == UserMusicianReaction.c.musician_id
        ).filter(
            UserMusicianReaction.c.reaction_type_id == adoring_reaction_id,
            UserMusicianReaction.c.user_id == current_user_id
        ).all()

        return render_template('favorites_bands.html', musicians=favorite_musicians)


@app.route("/remember_bands")
@login_required
def remember_bands_page():
    current_user_id = current_user.id
    # Припустимо, ми фільтруємо музикантів по будь-якій іншій реакції або умові
    remembered_musicians = db.session.query(Musician).join(
        UserMusicianReaction, Musician.id == UserMusicianReaction.c.musician_id
    ).filter(
        UserMusicianReaction.c.user_id == current_user_id
    ).all()

    return render_template('remember_bands.html', musicians=remembered_musicians)


@app.route("/delete-directly-reaction", methods=['POST'])
@login_required
def delete_directly_reaction():
    data = request.get_json()
    musician_id = data.get('musician_id')
    reaction_value = data.get('reaction_value')
    current_user_id = current_user.id

    try:
        # Перевірка на правильність значення реакції
        if reaction_value not in ['following', 'adoring', 'hating']:
            return jsonify({'error': 'Invalid reaction value'}), 400

        # Видалення відповідної реакції
        remove_specific_reaction(current_user_id, musician_id, reaction_value)

        db.session.commit()

        return jsonify({'message': 'Reaction removed successfully', 'musician_id': musician_id}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


def remove_specific_reaction(user_id, musician_id, reaction_value):
    # Вибір реакції по її типу
    reaction_type = db.session.query(ReactionType).filter_by(name=reaction_value).first()

    if not reaction_type:
        raise ValueError("Reaction type not found")

    # Видалення конкретної реакції для музиканта
    db.session.execute(delete(UserMusicianReaction).where(
        UserMusicianReaction.c.user_id == user_id,
        UserMusicianReaction.c.musician_id == musician_id,
        UserMusicianReaction.c.reaction_type_id == reaction_type.id
    ))

    print(f"Removed '{reaction_value}' reaction for user {user_id} and musician {musician_id}")

