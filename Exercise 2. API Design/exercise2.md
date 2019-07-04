# 学习目标
在本章练习中你将学会如何设计自己的超媒体接口，同时学会如何利用[Apiary](https://apiary.io/a%20professional%20documentation%20framework)来创建专业的接口文档。

# 超媒体接口和文档设计
在实现自己的接口前完成一份专业的API文档十分重要。第一，实现接口前你需要考虑到客户端访问API的最佳方式，从而得出最好的设计方案，如果没有提前写好的设计文档，直接完成的API的就会过分基于接口实现的代码，从而会有一定的局限性。第二，在设计文档的过程中你需要考虑到API的返回情况，即能在实现接口前接收到API的反馈，与修改已实现的API相比，对设计和文档的更正会容易很多。

# API概念
本章练习中的API是一个基于音乐元数据存储的服务接口，主要可以用来管理与完善和音乐有关的数据。在这个例子当中，数据结构并不是很复杂：音乐元数据总共分为三个模块：艺术家（artist），专辑（album）和播放记录（track）；艺术家是专辑的作者，每个专辑会有一个播放记录。拥有一个清晰的结构后就很容易去创建数据库。

## 难点一
在这个例子中，第一个难点是艺术家或专辑的重名问题，记录重名的艺术家和专辑是一件很棘手的事情；其次对于同一张专辑来说，可能会出现多个‘未命名’的播放记录。所以说，在设计API之前，需要找到一个方法或者调用其他接口来解决‘不唯一’这个难题。

## 难点二
第二个难点是‘群星’（various artists）问题，简称VA。由于会存在多个艺术家合作的情况，同一张专辑就会有多个艺术家，所以在这种情况下，对这张专辑的播放记录就需要根据不同艺术家来分开处理。

## 相关服务
为了更好地理解本例中的API，我们在此提供几个相似的基于音乐数据的服务：[Musicbrainz](https://musicbrainz.org/),  [FreeDB](http://www.freedb.org/).
此外，我们提供一个可以用到本例中API的数据源：[last.fm](https://www.last.fm/)

# 数据库设计
根据上面所提到的概念，我们可以创建一个拥有三个模型（models）的数据库：album，artist和track. 同时，我们在创建数据库的时候还需要考虑到‘群星’的情况，即还有两个需要特别注意的存在：拥有多个艺术家的专辑（VA album）和基于多个艺术家的播放记录（VA track）。在创建数据库的过程中，我们要考虑到每个模块的‘唯一性约束’；同时在此提醒，在创建模块时，我们应该避免使用原始数据库ID来定位API中的资源，第一是因为原始ID并不具有任何意义，第二是因为这样会给一些不希望未经授权用户推断出有关信息的API带来漏洞。


‘唯一性约束’允许我们定义更复杂的唯一性，而不仅仅是将单个列定义为唯一。如果想定义模块中的多个列为唯一，即这些列中的特定值组合只能出现一次，我们可以将多个列设进‘唯一性约束’中。例如，我们可以假设同一个艺术家不会有两个相同名字的专辑（不考虑多次编辑的情况），但是不同艺术家的专辑可能有相同的名字，那么将单个专辑的标题定义为唯一就是不够全面的，而专辑标题加上艺术家ID的组合是可以确定为唯一的，所以此时我们就可以将这两列一起设进‘唯一性约束’中。
```python
def Album(db.Model):
    __table_args__ = (db.UniqueConstraint("title", "artist_id", name="_artist_title_uc"), )
```
注意上述代码中最后的逗号：这是告诉Python这是一个元组而不是一个正常插入的普通值。你可以在‘唯一性约束’中的元组参数中加上任何想加的列。上述代码中的‘name’是必须存在的，所以请尽量让它具有表达意义。对单个播放记录来说，我们应该给它一个更完善的‘唯一性约束’：对一张专辑来说，每个播放记录都应该有一个单独的索引号，所以对播放记录来说，‘唯一性约束’应该是专辑ID，播放记录数量和播放记录索引号的组合。
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
# 资源设计
在定义完数据库模块后，我们可以开始考虑设计资源。在RESTful API中，资源可以是任何一个客户想要获取的东西。现在我们需要根据上面定义的三个数据库模块来定义我们的资源。之后，我们还将解释在这个API例子中，该如何基于RESTful规则使用HTTP方法来对我们的资源进行操作。

## 数据库模块中的资源
一个资源，应该是一个对客户有足够吸引力，值得我们为其定义一个URI（统一资源标识符）的数据，同样地，每个资源都应该通过自己的URI被定义为唯一资源。对一个API来说，资源的数量有数据库表数量的两倍之多是一件很正常的事情，第一是因为对每个数据库表来说，客户可能会想要获取整个表作为一个‘集合’数据，也可能会想要单独访问表中某一行来获取‘个体’数据。有时候，即使‘集合’数据中已经包含了所有‘个体’数据，但是为了能让客户操纵数据，我们仍需要将‘个体’数据设置为一个单独的资源。

根据上面的这个解释，我们可以暂时定义6个资源：
1. artist collection
2. artist item
3. album collection
4. album item
5. track collection
6. track item

值得注意的是，一个‘集合’类资源并不是一定要包含相关表中的所有内容。举例说明，对在整个数据层次中处于最高层的艺术家而言，拥有一个包含所有艺术家的集合是一个有意义的操作；
但像track表中包含了所有有关播放记录的数据，这所有的播放记录放在一起作为一个集合的意义并不大，我们需要的更有意义的集合，例如根据不同专辑分组的播放记录集合。
对专辑来说，和播放记录的处理方式一样，将根据不同艺术家分组的专辑合集定为资源更有意义（一个特定艺术家的所有专辑）。同时，我们还需要考虑到‘群星’问题，那么我们可以定义两个不同的‘集合’资源：一个是某个特定艺术家的所有专辑，另一个是多个艺术家的所有专辑。
最终我们将资源定义为：
1. artist collection
2. artist item
3. albums by artist collection
4. VA albums collection
5. album item(incorporates track collection)
6. track item

与普通专辑相比，我们对VA专辑的处理方式略有不同。为了更好地记录VA专辑的播放数据，我们需要再加一些单独的数据表达作为资源。最后我们也可以加上所有专辑的集体资源，这是为了让客户可以看到我们的API提供了哪些专辑数据。
1. artist collection 
2. artist item
3. all albums collection
4. albums by artist collection
5. VA albums collection
6. album item(incorporates track collection)
7. track item
8. VA track item

## 定位资源
在定义完资源后，并且分析出资源重要性排名后，我们需要给每个资源定义一个URI，使每个资源是被唯一定义的（addressability principle）。
我们需要定义URI层次结构，我们希望通过URIs来传达资源之间的联系。对于普通专辑来说，资源层次结构如下：
```python
artist collection
└── artist
    └── album collection
        └── album
            └── track
```
我们设定专辑标题加上艺术家ID是唯一的，同时，识别一个唯一的播放记录的最好方式就是将其索引号和播放名称与一张具体的专辑结合起来作为识别符。
将上面所有的因素考虑进去，我们最终可以得到一个路径：
```python
/api/artists/{artist_unique_name}/albums/{album_title}/{disc}/{track}/
```
上面这个路径可以唯一地定义每一个播放记录，并且将数据层次清晰地表达了出来，所有在层次结构中的资源（包括集合和个体），都可以通过从上面这个路径的结尾逐渐删除一个或多个部分来获得。
对于VA专辑的播放记录，我们可以通过将上面路径中的{artist_unique_name}换成VA来区分，路径如下：
```python
/api/artists/VA/albums/{album_title}/{disc}/{track}/
```
除此之外我们还需要专门为存储所有专辑的数据加另一个分支：
```python
/api/albums/
```
那么整个URI树变成了下面这样：
```python
api
├── artists
│   ├── {artist}
│   │   └── albums
│   │       └── {album}
│   │           └── {disc}
│   │               └── {track}
│   └── VA
│       └── albums
│           └── {album}
│               └── {disc}
│                   └── {track}
└── albums
```
## 对资源的操作
遵循REST原则，我们的API应该提供针对资源的HTTP方法。我们在此重申每个HTTP方法该如何使用：
* GET - 返回一个资源的表达形式；不做出任何修改
* POST - 对目标集合添加一个新的示例
* PUT - 将一个目标资源用新的表达形式替换（只当目标资源存在的时候）
* DELETE - 删除目标资源

大多数资源都应该实现GET方法；POST方法一般针对‘集合’资源，PUT和DELETE方法一般针对于‘个体’资源实现。
在我们这个例子中有两个例外，第一：album资源既可以作为‘集体’资源也可以作为‘个体’资源，所以这四个HTTP方法都可以实现；
第二：对于all album这个资源来说，作为一个‘集体’资源，它并不能实现POST方法，因为我们可以看到它的路径是`/api/albums/`，我们从URI中并不能知道这张专辑的作者是谁，即路径中缺少我们创建新专辑需要的艺术家的信息，而艺术家是作为专辑的父节点存在的，即必须要先有艺术家才能有专辑。
所以如果我们想创建一个新的子节点，这个子节点的父节点应该要在URI中可以被找到，而不是被放在请求中。

我们将每个资源对应的HTTP方法在下表列出：

| **Resource** | **URI** | **GET** | **POST** | **PUT** | **DELETE** |
|---|---|---|---|---|---|
| artist collection | /api/artists/ |X|X|-|-|
| artist item | /api/artists/{artist}/ |X|-|X|X|
| albums by artist | /api/artists/{artist}/albums/ |X|X|-|-|
| albums by VA | /api/artists/VA/albums/ |X|X|-|-|
| all albums | /api/albums/ |X|-|-|-|
| album | /api/artists/{artist}/albums/{album}/ |X|X|X|X|
| VA album | /api/artists/VA/albums/{album}/ |X|X|X|X|
| track | /api/artists/{artist}/albums/{album}/{disc}/{track}/ |X|-|X|X|
| VA track | /api/artists/VA/albums/{album}/{disc}/{track}/ |X|-|X|X|

可以看到我们遵守了REST原则，每个HTTP方法都按在预期执行。上面这张表告诉了我们很多有用的信息：它显示了可以发出的所有可能的HTTP请求，甚至提示了它们的含义。
例如，如果你向track资源提交一个PUT申请，它将修改track的数据（更具体地，它会用请求中的数据代替原数据）.

### 练习：添加一个播放记录
利用上面所学到的概念，你是否能写出一个URI来添加一个新的名为‘Happiness’的播放记录（该播放记录是专辑‘Kallocain’中第三个播放记录，该专辑的作者是‘Paatos’），在此练习中假设这个艺术家的名字是唯一的，并且请在URI中将艺术家的名字全部小写。



