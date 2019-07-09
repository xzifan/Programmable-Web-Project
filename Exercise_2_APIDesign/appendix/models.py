from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

va_artist_table = db.Table("va_artists", 
    db.Column("album_id", db.Integer, db.ForeignKey("album.id"), primary_key=True),
    db.Column("artist_id", db.Integer, db.ForeignKey("artist.id"), primary_key=True)
)


class Track(db.Model):
    
    __table_args__ = (db.UniqueConstraint("disc_number", "track_number", "album_id", name="_track_index_uc"), )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    disc_number = db.Column(db.Integer, default=1)
    track_number = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Time, nullable=False)
    album_id = db.Column(db.ForeignKey("album.id", ondelete="CASCADE"), nullable=False)
    va_artist_id = db.Column(db.ForeignKey("artist.id", ondelete="SET NULL"), nullable=True)
    
    album = db.relationship("Album", back_populates="tracks")
    va_artist = db.relationship("Artist")

    def __repr__(self):
        return "{} <{}> on {}".format(self.title, self.id, self.album.title)
    
    
class Album(db.Model):
    
    __table_args__ = (db.UniqueConstraint("title", "artist_id", name="_artist_title_uc"), )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release = db.Column(db.Date, nullable=False)
    artist_id = db.Column(db.ForeignKey("artist.id", ondelete="CASCADE"), nullable=True)
    genre = db.Column(db.String, nullable=True)
    discs = db.Column(db.Integer, default=1)
    
    artist = db.relationship("Artist", back_populates="albums")
    va_artists = db.relationship("Artist", secondary=va_artist_table)
    tracks = db.relationship("Track",
        cascade="all,delete",
        back_populates="album",
        order_by=(Track.disc_number, Track.track_number)
    )
    
    sortfields = ["artist", "release", "title"]
    
    def __repr__(self):
        return "{} <{}>".format(self.title, self.id)


class Artist(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    unique_name = db.Column(db.String, nullable=False, unique=True)
    formed = db.Column(db.Date, nullable=True)
    disbanded = db.Column(db.Date, nullable=True)
    location = db.Column(db.String, nullable=False)
    
    albums = db.relationship("Album", cascade="all,delete", back_populates="artist")
    va_albums = db.relationship("Album",
        secondary=va_artist_table,
        back_populates="va_artists",
        order_by=Album.release
    )

    def __repr__(self):
        return "{} <{}>".format(self.name, self.id)
