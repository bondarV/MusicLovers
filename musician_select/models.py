from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import String, Integer, ForeignKey, Table, Column, MetaData
from musician_select import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ReactionEmotion(db.Model):
    __tablename__ = 'reaction_emotions'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    def __repr__(self):
        return f"{self.name} - {self.description}"

UserMusicianReacts = Table(
    "user_musician_reacts",
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('musician_id', String(36), ForeignKey('musicians.id'), nullable=False),
    Column('reaction_id', Integer, ForeignKey('reaction_emotions.id'), nullable=False)
)

class Musician(db.Model):
    __tablename__ = 'musicians'
    id: Mapped[int] = mapped_column(String(36), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(40), unique=False, nullable=False)
    country: Mapped[str] = mapped_column(String(3), unique=False, nullable=False)
    type: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    gender:Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    disambiguation:Mapped[str] = mapped_column(String(50),unique=False, nullable=True)
    rating: Mapped[str] = mapped_column(String(40), unique=False, nullable=True)
    start_singing: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    end_singing: Mapped[str] = mapped_column(String(10), nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(90), nullable=False)
    musicians: Mapped[list['Musician']] = relationship(secondary=UserMusicianReacts, backref='users', lazy='subquery')


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
