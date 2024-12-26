from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Table, Column, Numeric, Date, Unicode, Float
from musician_select import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Association Tables
UserMusicianReaction = Table(
    "user_musician_reactions",
    db.Model.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True, nullable=False),
    Column('reaction_type_id', ForeignKey('reaction_types.id'), primary_key=True, nullable=False),
    Column('musician_id', ForeignKey('musicians.id'), primary_key=True, nullable=False)
)

MusicianGenre = Table(
    "musician_genres",
    db.Model.metadata,
    Column('musician_id', ForeignKey('musicians.id'), primary_key=True, nullable=False),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True, nullable=False)
)

UserRecord = Table(
    'user_records', db.Model.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True, nullable=False),
    Column('record_id', ForeignKey('records.id'), primary_key=True, nullable=False),
    Column('rating', Float, nullable=False, default=0)  # Додаємо значення за замовчуванням
)

# Models
class Musician(db.Model):
    __tablename__ = 'musicians'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Unicode(40), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(3), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    disambiguation: Mapped[str] = mapped_column(Unicode(200), nullable=True)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=True)
    start_singing: Mapped[Date] = mapped_column(Date, nullable=True)
    end_singing: Mapped[Date] = mapped_column(Date, nullable=True)

    reactions: Mapped[list['ReactionType']] = relationship(
        "ReactionType",
        secondary=UserMusicianReaction,
        back_populates="musicians",
        overlaps="users"
    )
    users: Mapped[list['User']] = relationship(
        "User",
        secondary=UserMusicianReaction,
        back_populates="musicians"
    )
    genres: Mapped[list['Genre']] = relationship(secondary=MusicianGenre, back_populates="musicians")
    records: Mapped[list['Record']] = relationship(
        "Record",
        back_populates="musician"
    )
    aliases: Mapped[list['Alias']] = relationship('Alias', back_populates='musician')

    # Додати атрибут для urls
    urls: Mapped[list['URL']] = relationship(
        'URL', back_populates='musician'
    )

    def __repr__(self):
        return f"{self.name} - {self.country}"

class ReactionType(db.Model):
    __tablename__ = 'reaction_types'
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    users: Mapped[list['User']] = relationship(
        "User",
        secondary=UserMusicianReaction,
        back_populates="reactions"
    )
    musicians: Mapped[list['Musician']] = relationship(
        "Musician",
        secondary=UserMusicianReaction,
        back_populates="reactions"
    )

    def __repr__(self):
        return f"{self.name} - {self.description}"

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(90), nullable=False)

    musicians: Mapped[list['Musician']] = relationship(
        "Musician",
        secondary=UserMusicianReaction,
        back_populates="users"
    )
    reactions: Mapped[list['ReactionType']] = relationship(
        "ReactionType",
        secondary=UserMusicianReaction,
        back_populates="users",
        overlaps="musicians"
    )
    records: Mapped[list['Record']] = relationship(
        "Record",
        secondary=UserRecord,
        back_populates="users"
    )

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, plain_password_text):
        self.password_hash = bcrypt.generate_password_hash(plain_password_text).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Genre(db.Model):
    __tablename__ = 'genres'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    musicians: Mapped[list['Musician']] = relationship(secondary=MusicianGenre, back_populates="genres")

    def __repr__(self):
        return f"{self.name}"

class Record(db.Model):
    __tablename__ = 'records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(Unicode(150), nullable=False)
    disambiguation: Mapped[str] = mapped_column(Unicode(100), nullable=True)
    release_date: Mapped[Date] = mapped_column(Date, nullable=True)
    musician_id: Mapped[str] = mapped_column(ForeignKey('musicians.id'), nullable=False)
    musician: Mapped['Musician'] = relationship('Musician', back_populates='records')
    users: Mapped[list['User']] = relationship("User", secondary=UserRecord, back_populates="records")

    def __repr__(self):
        return f"{self.title} - {self.disambiguation}"

class Alias(db.Model):
    __tablename__ = 'aliases'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Unicode(40), nullable=False)
    musician_id: Mapped[str] = mapped_column(ForeignKey('musicians.id'), nullable=False)
    musician: Mapped['Musician'] = relationship('Musician', back_populates='aliases')

    def __repr__(self):
        return f"{self.name}"

class URL(db.Model):
    __tablename__ = 'urls'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    resource: Mapped[str] = mapped_column(Unicode(200), unique=True, nullable=False)
    musician_id: Mapped[str] = mapped_column(ForeignKey('musicians.id'), nullable=False)
    musician: Mapped['Musician'] = relationship('Musician', back_populates='urls')

    def __repr__(self):
        return f"{self.resource}"
