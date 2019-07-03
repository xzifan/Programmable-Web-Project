# 学习目标
在本章练习中你将学会如何设计自己的超媒体接口，同时学会如何利用[Apiary](https://apiary.io/a%20professional%20documentation%20framework)来创建专业的接口文档。

# 超媒体接口和文档设计
在实现自己的接口前完成一份专业的API文档十分重要。第一，实现接口前你需要考虑到客户端访问API的最佳方式，从而得出最好的设计方案，如果没有提前写好的设计文档，直接完成的API的就会过分基于接口实现的代码，从而会有一定的局限性。第二，在设计文档的过程中你需要考虑到API的返回情况，即能在实现接口前接收到API的反馈，与修改已实现的API相比，对设计和文档的更正会容易很多。

# API概念
本章练习中的API是一个基于音乐元数据存储的服务接口，主要可以用来管理与完善和音乐有关的数据。在这个例子当中，数据结构并不是很复杂：音乐元数据总共分为三个模块：艺术家（artist），唱片集（album）和播放记录（track）；艺术家是唱片集的作者，每个唱片集会有一个播放记录。拥有一个清晰的结构后就很容易去创建数据库。

## 难点一
在这个例子中，第一个难点是艺术家或唱片集的重名问题，记录重名的艺术家和唱片集是一件很棘手的事情；其次对于同一张唱片集来说，可能会出现多个‘未命名’的播放记录。所以说，在设计API之前，需要找到一个方法或者调用其他接口来解决‘不唯一’这个难题。

## 难点二
第二个难点是‘群星’（various artists）问题，简称VA。由于会存在多个艺术家合作的情况，同一张唱片集就会有多个艺术家，所以在这种情况下，对这张唱片集的播放记录就需要根据不同艺术家来分开处理。

## 相关服务
为了更好地理解本例中的API，我们在此提供几个相似的基于音乐数据的服务：[Musicbrainz](https://musicbrainz.org/),  [FreeDB](http://www.freedb.org/),  [Rate Your Music]().
此外，我们提供一个可以用到本例中API的数据源：[last.fm](https://www.last.fm/)

# 数据库设计
根据上面所提到的概念，我们可以创建一个拥有三个模型（models）的数据库：album，artist和track. 同时，我们在创建数据库的时候还需要考虑到‘群星’的情况，即还有两个需要特别注意的存在：拥有多个艺术家的唱片（VA album）和基于多个艺术家的播放记录（VA track）。在创建数据库的过程中，我们要考虑到每个模块的‘唯一性约束’；同时在此提醒，在创建模块时，我们应该避免使用原始数据库ID来定位API中的资源，第一是因为原始ID并不具有任何意义，第二是因为这样会给一些不希望未经授权用户推断出有关信息的API带来漏洞。


‘唯一性约束’允许我们定义更复杂的唯一性，而不仅仅是将单个列定义为唯一。如果想定义模块中的多个列为唯一，即这些列中的特定值组合只能出现一次，我们可以将多个列设进‘唯一性约束’中。例如，我们可以假设同一个艺术家不会有两个相同名字的唱片集（不考虑多次编辑的情况），但是不同艺术家的唱片集可能有相同的名字，所以单个唱片集的标题并不一定是唯一的，而唱片集标题加上艺术家ID就可以是唯一的，此时我们就可以将这两列设进‘唯一性约束中’。
```python
def Album(db.Model):
    __table_args__ = (db.UniqueConstraint("title", "artist_id", name="_artist_title_uc"), )
```
注意上述代码中最后的逗号：这是告诉Python这是一个元组而不是一个正常插入的普通值。你可以在‘唯一性约束’中加上任何想加的列。上述代码中的‘name’是必须存在的，所以请尽量让它具有表达意义。对单个播放记录来说，我们应该给它一个更完善的‘唯一性约束’：对一张唱片集来说，每个播放记录都应该有一个单独的索引号，所以对播放记录来说，‘唯一性约束’应该是唱片ID，播放记录数量和播放记录索引号的组合。
```python
def Track(db.Model):
    __table_args__ = (db.UniqueConstraint("disc_number", "track_number", "album_id", name="_track_index_uc"), )
```
为了解决‘群星’问题，我们将允许album模块中的外键‘artist’为空，并且加一个可选字段‘va_artist’。最终的数据库代码如下：
```python
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
```


