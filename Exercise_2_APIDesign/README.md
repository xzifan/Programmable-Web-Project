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


‘唯一性约束’允许我们定义更复杂的唯一性，而不仅仅是将单个列定义为唯一。如果想定义模块中的多个列为唯一，即这些列中的特定值组合只能出现一次，我们可以将多个列设进‘唯一性约束’中。例如，我们可以假设同一个艺术家不会有两个相同名字的专辑（不考虑多次编辑的情况），但是不同艺术家的专辑可能有相同的名字，因此我们并不能将单张专辑的标题定为唯一，而是应该将专辑标题与艺术家ID的组合定为唯一，所以此时我们可以将这两列一起设进‘唯一性约束’中。
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

[models.py](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/models.py)
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

### 练习一：添加一个播放记录
利用上面所学到的概念，你是否能写出一个URI来添加一个新的名为‘Happiness’的播放记录（该播放记录是专辑‘Kallocain’中第三个播放记录，该专辑的作者是‘Paatos’），在此练习中假设这个艺术家的名字是唯一的，并且请在URI中将艺术家的名字全部小写。

### 答案：
正确答案：`/api/artists/paatos/albums/Kallocain/`

解释：我们第一步需要确定的是这个操作需要用哪一种HTTP方法，由于我们想要给某一张专辑加播放记录，那我们需要用到的方法是POST，所以根据上面资源表中的信息，能用POST方法的资源只有五个（一般只有‘集合’资源才能使用POST方法）：artist collection, albums by artist, albums by VA, album 和 VA album.
如果我们想给一张只有一个艺术家的专辑加播放记录，很明显我们需要操作的资源是album`/api/artists/{artist}/albums/{album}/`. 
那么我们可能会好奇播放记录的信息{track：Happiness； disc：3}该如何加进去呢？

注意，我们不能将播放记录的信息放在URI中，而是应该将播放记录的信息放进POST方法的请求中（request body）：
在这里把所有信息都写在URI中提交给track资源是不正确的（`/api/artists/paatos/albums/Kallocain/3/Happiness/`），因为track作为一个‘个体’资源，并不支持POST方法，我们只能给一个‘集合’中添加新元素，而不能给一个‘个体’添加新记录。
而`/api/artists/paatos/albums/Kallocain/3/Happiness/`这个URI支持的操作是GET,PUT,DELETE，即当我们想要获取，修改或删除某一个确切的track数据时可以调用该URI。

# 进入超媒体世界
为了让前端开发者了解到底前端需要传入什么数据以及所期待的返回值，我们需要将API详细记载。
在本课程中，我们将在API给出的响应中运用超媒体，在本章的例子中，我们选择用[Mason](https://github.com/JornWildt/Mason)作为我们的超媒体格式，因为对于定义超媒体元素并将它们连接到数据中，Mason有着非常清晰的语法。

## 数据表达形式
我们的API是通过JSON交流的，对数据表达来说，这是一个很简单的序列化过程。如果客户端给`/api/artists/scandal/`发出了一个GET请求，返回的数据将会被序列化，如下：
```python
{
    "name": "Scandal",
    "unique_name": "scandal",
    "location": "Osaka, JP",
    "formed": "2006-08-21",
    "disbanded": null
}
```
如果客户想要添加一个新的艺术家，他们需要发送一个几乎相同的JSON数据（除去unique_name，因为这个是API服务器自动生成的）。
这个数据的序列化过程几乎可以运用到所有模块上。

对于‘集体’资源来说，在它们的数据体中会包含一个‘items’的属性--‘items’是一个包含了这个集体资源中一部分数据或全部数据的列表。
例如albums资源中不仅包含描述自身信息的根级数据，还包括一个存储了track信息的列表。
值得注意的是，‘items’中并不用将相应的资源数据全部包含进去，只需要包含必要的信息，例如对于album collections来说，在‘items’中包含的数据只需要有专辑标题和艺术家名字就足够了：
```python
{
    "items": [
        {
            "artist": "Scandal",
            "title": "Hello World"
        },
    ]
}
```
如果客户想要得到‘items’中某个个体的更多详细信息，可以直接通过URI访问album个体资源来获取。

## 超媒体控件（Hypermedia Controls）
你可以将API想象成一张地图，而每一个资源就是地图中一个点，一个你最近发送了GET请求的资源就像是一个在说‘你在这里’的点。而‘超媒体控件’能描述逻辑上的下一步操作：下一步你将走到哪里，或者是你在的这个点下一步可以做什么。
‘超媒体控件’与资源一起形成了一个能解释说明该如何在API中‘航行’的客户端状态图（state diagram）.在我们刚刚学到的数据表达中，‘超媒体控件’是作为一个额外属性存在于其中的。

超媒体控件是至少两件事情的组合：链接关系（"rel"）和目标URI（"href"）.这说明了两个问题：这个控件做了什么，以及在哪里可以激活这个动作。请注意，链接关系是机器可读的关键字，而不是面向人类的描述。
许多我们常用的链接关系正在标准化，可参考（[完整列表](https://www.iana.org/assignments/link-relations/link-relations.xhtml)），但是API也可以在需要的时候给出自己的定义 - 只要每个链接关系是一直表达同一种意思即可。
当客户想要做某事时，他将使用可用的链接关系来找到这个请求应该用到的URI。这意味着使用我们API的客户端永远不需要知道硬编码的URIs - 他们将通过搜索正确的链接关系来找到URI。

Mason还为超媒体控件定义了一些额外的属性。其中“method”是我们将会经常使用的方法，因为它告诉应该使用哪个HTTP方法来发出请求（由于默认方法是GET，所以通常GET方法会被省略）。
还有“title”可帮助客户（人类用户）弄清楚控件的作用。除此之外，我们还可以定义一个[JSON模式](https://json-schema.org/)来规定发送到API的数据表达格式。

在Mason中，可以通过添加"@controls"属性将超媒体控件附加给任何对象。"@controls"本身就是一个对象，其中的属性是‘链接关系’，其值是至少具有一个属性（href）的对象。例如，这是一个带有多媒体控件的track个体资源，用于返回其所在的专辑的链接关系为（“向上”），编辑其信息的链接关系为（“编辑”）：
```python
{
    "title": "Wings of Lead Over Dormant Seas",
    "disc_number": 2,
    "track_number": 1,
    "length": "01:00:00",
    "@controls": {
        "up": {
            "href": "/api/artists/dirge/albums/Wings of Lead Over Dormant Seas/"
        },
        "edit": {
            "href": "/api/artists/dirge/albums/Wings of Lead Over Dormant Seas/2/1/",
            "method": "PUT"
        }
    }
}
```
或者，如果我们希望集合中的每个个例上都有自己的URI可供客户端使用：
```python
{
    "items": [
        {
            "artist": "Scandal",
            "title": "Hello World",
            "@controls": {
                "self": {
                    "href": "/api/artists/scandal/albums/Hello World/"
                }
            }
        },
        {
            "artist": "Scandal",
            "title": "Yellow",
            "@controls": {
                "self": {
                    "href": "/api/artists/scandal/albums/Yellow/"
                }
            }
        }
    ]
}
```
## 自定义链接关系
在定义我们的链接关系的时候，虽然尽可能使用标准是好的，但实际上每个API都有许多控件，其含义无法用任何标准化关系明确表达。因此，Mason文档可以使用链接关系命名空间来扩展可用的链接关系。Mason命名空间定义了前缀及其关联的命名空间（类似于XML命名空间，请参阅[CURIE](https://www.w3.org/TR/curie/)）。该前缀将被添加到[IANA列表](https://www.iana.org/assignments/link-relations/link-relations.xhtml)中未定义的链接关系上。
当一个链接关系以命名空间前缀为前缀时，它应被解释为在命名空间的末尾附加了关系并使关系唯一 - 即使另一个API定义了具有相同名称的关系，它也会有不同的命名空间前缀。例如，如果想要一个名为“albums-va”的关系来标明一个指向所有VA专辑集合的控件，则其完整标识符可以是`http://wherever.this.server.is/musicmeta/link-relations#albums-by`,
我们可以定义一个名为“mumeta”的命名空间前缀，然后这个控件看上去将会是这样：
```python
{
    "@namespaces": {
        "mumeta": {
            "name": "http://wherever.this.server.is/musicmeta/link-relations#"
        }
    },
    "@controls": {
        "mumeta:albums-va": {
            "href": "/api/artists/VA/albums"
        }
    }
}
```
此外，如果客户端开发人员访问完整的URL，他们应该找到有关链接关系的描述。另请注意，通常这是一个完整的URL，因为服务器部分保证了唯一性。在后面的示例中，你将看到我们正在使用相对URI - 这样即使服务器在不同的地址（最有可能的是localhost：someport）中运行，指向关系描述的链接也会起作用。

有关链接关系的信息必须存储在某处。请注意，这适用于客户端开发人员，即人类。在我们的例子中，一个简单的HTML文档应该足以支持每个关系。这就是我们的命名空间名称以＃结尾的原因。它可以方便地找到每个关系的描述。在继续之前，这里是我们的API使用的自定义链接关系的完整列表：
`add-album, add-artist, add-track, albums-all, albums-by, albums-va, artists-all, delete`。

## API 地图
设计API的最后一项业务是创建一个包含所有资源和超媒体控件的完整地图。在这个状态图中，资源是状态，控件是转换。一般来说，只有GET方法用于从一种状态移动到另一种状态，因为其他方法不会返回资源表达。我们已经提出了其他方法作为箭头回到相同的状态。这是完整地图：
![MusicMeta API state diagram](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/appendix/musicmeta_api_state_diagram.png)

注意 1：地图中每个盒子颜色的代码仅用于教育目的，以显示数据库中的数据是如何连接到资源 - 你不需要在现实生活或自己的项目中实现这样的细节。

注意 2：地图中的链接关系“item”并不存在，这实际上是“self”。在此图中，“item”用于表示这是通过个体数据的“self”链接从集合转换到个体。

这样的映射图在设计API时很有用，应该在设计API返回每个单独的资源表达之前完成。由于所有操作都在这个地图中可见，因此更容易查看是否缺少某些内容。
在制作图表时请记住，必须要有从一个状态到另一个状态的联通路径（连通原理）。在我们的例子中，我们在URI树中有三个独立的分支，
因此我们必须确保每个分支之间的转换（例如，AlbumCollection资源具有“artists-all”和“albums-va”）。

### 练习二：The Road to Transcendence
考虑上面的状态图。我们假设你是一个机器客户端。你当前正站在ArtistCollection节点上，目标是要查找和修改有关一个有群星艺术家的专辑“Transcendental”（Mono和The Ocean的合作）的数据。
为了做到这一点，必须遵循哪些链接？这条路径有意义吗？
请给出最短的链接关系列表（使用与上面状态图中相同的名称），从而将你从ArtistCollection导出到修改VA专辑的数据（edit）。

### 答案：	
正确答案：`albums-all,albums-va,item,edit`

注意，最后我们是需要修改VA专辑的数据，所以到达了VAAlbum我们还需要通过访问‘edit’链接关系来修改数据。

## 入口点
关于API映射图的最后一点概念是入口点（Entry Point）。这应该是API的根源（在我们的例子中：/api/。它有点像API的索引页面。它不是资源，通常不返回（这就是为什么它不在状态图中的原因）。它只是显示了客户在“进入”API时的合理启动选项。
在我们的例子中，它应该包含多媒体控件来调用GET方法来获取艺术家集合或专辑集合（也有可能是VA专辑集合）。

### 练习三：Enter the MAZE
创建一个MusicMeta API入口点的JSON文档。它应该包含两个超媒体控件：链接到艺术家集合（Artist Collection），并链接到专辑集合（Album Collection）。
你应该能够从上面的状态图中找出这些控件的链接关系。不要忘记使用mumeta命名空间！

### 答案：
正确答案：[answer_ex2_t3](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/answer_ex2_t3.json)

















































































