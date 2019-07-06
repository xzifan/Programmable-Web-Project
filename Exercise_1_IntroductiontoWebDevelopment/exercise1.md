# 网络开发导论

这个练习中涵盖了比较基础的简单网页应用开发，目的是开发一个能远程访问、管理服务器数据库的简单应用。这个项目涉及到的知识较为宽泛——会有比较多不同方面的知识都被稍稍提及。并且我们会用到一些现代python web 开发工具，这些工具封装了许多开发上的细节之处并对开发者隐藏。了解这些有利于我们理解高级开发工具的工作原理，但我们不要求掌握如何使用。

两个在此课程中主要要使用到的工具就是[Flask](http://flask.pocoo.org/)和[SQLAlchemy](https://www.sqlalchemy.org/)。Flask是一个用于Python web开发的微框架（microframework）。十分适合用于不需要像Django那样大型框架的小应用。SQLAlchemy是一个数据库工具包，可以绕过使用它的需要结构化查询语言，允许完全通过Python对象进行数据库管理。

# 部署静态内容

在python虚拟环境中安装flask，并且通过浏览器访问服务令它说 hello

## python 虚拟环境 (Virtual environments)

尽管这一步操作不是必要的，但虚拟环境在各种python开发中都是强烈建议使用的。虚拟环境多用于创建纯净的Python环境并与系统的Python环境相隔离。每一个虚拟环境独立于主环境而管理着自有的一系列模块。虚拟环境也能在用户的主目录下管理，这将允许安装没有管理员权限的新模块。

如果你需要安装具有特定的第三方模块但希望为其他所有模块创建另一个版本，则虚拟环境特别有用。这在具有多个第三方组件的项目中很容易发生：一个组件（模块A）经历向后不兼容的更改，而另一个组件（模块B）将模块A作为依赖关系不会立即跟进更新，从而破坏模块B - 除非安装保留模块A的最后一个兼容版本。此外，在另一个系统上设置应用程序时，虚拟环境可用于确保Python环境与开发系统中的相同。

当然，如果你以某种方式弄乱你的Python环境，你可以删除这个环境并重新开始。此外，在具有包管理的Linux系统上，使用Pip安装Python模块可能会破坏包管理器安装的Python模块。但是，在虚拟环境中使用Pip安装模块是完全安全的。

## 创建并启动虚拟环境

我们以python 3.3为例子，必备的工具都会自动安装。以防万一，你需要安装Pip并用它安装virtualenv模块。创建虚拟环境你只需要输入：

```
python -m venv myvenv /path/to/the/virtualenv
```

其中"myvenv"为自定义虚拟环境名,可省略  

在OS X和许多linux发行版上你需要使用python3（在Python 2上运行上面的命令会产生“没有名为venv的模块”的错误消息）

**启动虚拟环境**  
windows：  

```
[虚拟环境路径]\Scripts\activate.bat
```  

在OS X或Linux中:

```
source /path/to/the/virtualenv/bin/activate
```

然后你就能看到提示符  

```
(myvenv) C:\>  
```

当在虚拟环境中进行cd时 - 请注意，你实际上不需要在虚拟环境文件夹中工作，它只是包含你的Python环境。只要你在括号中看到名称，就会知道这个虚拟环境是激活的。当你运行Python时，它将通过虚拟环境启动。同样，当您使用Pip安装模块时，它们将仅安装到这个虚拟环境文件夹中。  

对于剩下的步骤，请确保您始终在virtualenv中。
## web框架的简单介绍
如果我们尽可能地简化来看，web应用就是一个读取HTTP请求（request）相应产生一个HTTP响应（response）的‘软件’。这种情况也发生在一些与HTTP服务器的神秘通信中。request和response中包汉各种各样的请求头部（headers）和一个request body（并非一定有）。参数可以通过URL或者消息的body传递。在这个项目中既然我们已经将结构相当简化了，我们可以通俗地说这个web框架（framework）是用来将HTTP请求转化为Python函数调用并将Python函数返回的值放到HTTP response中去。

当你在使用web框架的时候，URL会通过路由（routing）映射到函数。路由支持[URL模板](https://en.wikipedia.org/wiki/URL_Template)，那么部分URL会被定义为变量  

```
http://api.hundredacrewood.org/profile/winnie  
http://api.hundredacrewood.org/profile/tigger
```

以上两个URL都匹配同一URL模板  
```
/profile/{用户名}
```

用户名就会作为参数（或以其它方式）传递给被分配到指定URL的函数中。这些意味着你的web应用实际上包含了许多处理response和路由注册的函数上。这些函数被称为view函数。  

## 简单的flask应用

现在我们简单地了解了一下给予开发者便利的web框架，现在我们来尝试一下。在所有的例题和练习中我们都使用Flask，并需要使用到十分基础简单的python web框架功能，那么Flask就十分合适。  
安装Flask（确保在你的虚拟环境中）

```Shell Session
pip install Flask
```

以及我们马上要用到的模块：

```Shell Session
pip install pysqlite3
pip install flask-sqlalchemy
```

这个Flask应用十分简单。你可以查阅[Flask官方文档](http://flask.pocoo.org/docs/1.0/quickstart/#a-minimal-application)了解更多。创建一个文件夹然后把以下文件下载到这。  

[app.py](./app.py)  

```python
from flask import Flask
app = Flask("hello")

@app.route("/")
def index():
    return "You expected this to say hello, but it says \"donkey swings\" instead. Who would have guessed?"
```  

<p>如果你的这段代码文件名也是app.py，你就可以通过输入以下命令启动：

``` 
flask run
```

在终端上，假设你正在你的app文件所在文件夹。（如果你用了其他文件名，你需要设置环境变量FLASK_APP来指向你的代码文件）那现在你可以在浏览器中通过访问`http://localhost:5000`或`http://127.0.0.1:5000`预览你的应用。Flask开发服务器会默认将你的应用放到本地5000端口上运行。  

如果我们正在编写一个能让人通过浏览器使用的web应用，显然我们更需要返回一个HTML文件而不是纯字符串。在这里我们不会把重心放在HTML上。  

# 驱动简单的动态内容

静态网页是十分90年代的东西了，几乎没必要在那上面使用web框架。然而现在如果你希望一些东西变成动态的，web框架的好处便显而易见了。向HTTP请求传参有许多方法，每个方法都略微有其独特用途，但我们就简单地介绍两种并展示Flask如何将他们传递给你的Python函数。第三个也会在稍后介绍。

## 尝试对某人说Hello

第一种传参方法就是把他们放在URL中作为变量，正如上面讲到的。通常这种机制用于辨别你想要访问的是哪个资源。比如你想在网站上访问你自己的资料，你就可以用这样的URL `/profile/jack` 。  

让我们按照以上例子，在app.py中添加一个函数以响应所有匹配以下模板的URL：

```
/hello/
```

我们现在来演示如何向路由设置变量并且变量在对应函数中如何得以使用。这个匹配路径的新函数如下：

```python
@app.route(("/hello/<name>")
def hello(name):
    return "Hello {}".format(name)
```

那么现在所有以/hello/开头且带有任何字符串的url都会使该函数被调用并将字符串放到name参数中


> ## 练习1：数学计算
>
> 为了稍微练习以下基本的路由，我们引入简单的编程，让这个web程序通过URL中提供的变量进行一些基本数学运算。  
>
> **学习目标**：了解如何使用Flask的路由系统创建简单Web应用程序。  
>
> **如何开始**：  
> 在你的虚拟环境中创建一个项目文件夹，在文件夹中创建`app.py`并将所有代码放在此文件中。代码应包含5个函数，如下：  
>
> **函数1**：`index`  
>
> - 路径：`"/"`  
> - 返回：
>   - 任意字符串  
>
> **函数2**：`plus`
>
> - 路径：`"/add/<float:number_1>/<float:number_2>"`  
> - 参数：
>   - 第一个数（浮点）
>   - 第二个数（浮点）
> - 返回：
>   - 格式化的加法计算结果字符串  
>
> **函数3**：`minus`
>
> - 路径：`"/sub/<float:number_1>/<float:number_2>"`  
> - 参数：
>   - 第一个数（浮点）
>   - 第二个数（浮点）
> - 返回：
>   - 格式化的减法结果字符串
>
> **函数4**：`mult`
>
> - 路径：`"/mul/<float:number_1>/<float:number_2>"`  
> - 参数：
>   - 第一个数（浮点）
>   - 第二个数（浮点）
> - 返回：
>   - 格式化的乘法结果字符串  
>
> **函数5**：`/div/<float:number_1>/<float:number_2>`
>
> - 路径：`"/"`  
> - 参数：
>   - 被除数（浮点）
>   - 除数（浮点）
> - 返回：
>   - 格式化的除法结果字符串或NaN（当除数为0.0时返回NaN)
>
>> [答案_t1](./answer_ex1_t1.py)

## 查询  

第二种将参数作为URL的一部分传递的另一种机制是使用**查询参数**。如果你在进行Google搜索后查看了地址栏，你会注意到这些内容，例如搜索“eeyore”（已略去许多其他无关查询参数）：

```
https://www.google.fi/search?q=eeyore&oq=eeyore
```

在URL中所有？之后的都是查询参数。每个都属于键值对，其中=左边为键，=右边是值，他们被&彼此分开。查询参数是传递具有人一直的参数的正确方法。例如，上面计算器则更适合用这种方法。同样适用“Hello”的例子。让我们将hello函数转换为使用查询参数：

```py
@app.route("/hello/")
def hello():
    try:
        name = request.args["name"]
    except KeyError:
        return "Missing query parameter: name", 400
    return "Hello {}".format(name)
```

第一个重要的区别在于route的声明上：完全找不到name的出处。这并不是一个错误：查询参数并不是路径的一部分 —— 如果你尝试把他们放在那，你的URL将不会生效。同样`name`参数也不会出现在hello函数的声明中，因为它不是route的一个变量。相反，我们必须从请求对象（request object）中“挖掘”出来。这个对象是完整web框架功能的一部分并且包含了所有可能从客户端发出的HTTP请求中获取到的信息。从Flask中引入后便能全局地使用它。  

查询参数可以在一个类字典对象`request.args`中找到（具体请看[这里](http://werkzeug.pocoo.org/docs/0.14/datastructures/)）。另一个在这个例子中的不同点是我们在最后报告错误的匹配。之前当name变量还是URL的一部分时，空值会造成404 Not Found。然而，这里404不是一个合适的错误提示，因为就算没有查询参数这个目标URL仍是存在的。而400 (Bad Request) 不是很准确，但在这种情况下是合适的。意思是当客户端确实将请求发送到正确位置是，请求因为缺少所需信息而无法被处理。

实际上有几种不同的方法可以向客户端返回错误响应。在这种情况下，我们只是添加了状态代码的return语句。其他方法将会在之后的课程中介绍。或者你可以阅读[Flask中文文档](https://dormousehole.readthedocs.io/en/latest/)以了解更多。使用这样的return语句并不理想，因为这不容易将此结果归为错误。在此我们只是为了简化示例。  

>
>## 练习2：三角运算
>
>**学习目标**：学会如何在Flask应用中使用查询参数，如何在view函数中返回错误码，如何在view函数中的校验请求里控制相关的数据。
>
>**如何开始**：
>你可以在之前的计算练习文件中直接添加函数，也可以创建一个新的app文件。这次我们只需要编写一个函数：功能由路径变量选择的三角运算。同时你需要从Flask中引入request对象的组件，将引入的代码改成如下：  
>
>```py
>from flask import Flask, request
>```
>
>**函数**：trig
>
> - 路径：`"/trig/<func>"`
> - 参数：
>   - 需要执行的三角运算名（cos，sin 或 tan）
> - 查询参数
>   - `angle` 用于三角运算的角度（必填）
>   - `unit` 单位，"radian"（弧度）或 "degree"（角度），默认为弧度（选填）
> - 返回值
>   - 200：三角运算的结果字符串（精确到三位小数）
>     - 例：`/trig/sin?angle=3.14`
>     - 例：`/trig/sin?angle=90&unit=degree`
>   - 404：错误信息`Missing query parameter: angle`或`Invalid query parameter value(s)`
>     - 例：`/trig/cos/`
>     - 例：`/trig/tan?angle=pi`
>     - 例：`/trig/sin?angle=4&unit=donkey`  
>
>这个view函数计算角的sine，cosine或tangent值。如果给出的角的单位是度，那首先需要将其转换为弧度。如果func路径变量与任何一个三角运算都不匹配就给出404状态码。如果角度没给出或者查询参数值不正确，则返回400状态码以及相对应的错误信息。
>
>> [答案_t2](./answer_ex1_t2.py)


# 数据库和ORM

目前，我们还只能处理不需要存储数据的请求。数据库是Web开发不可或缺的一部分，因为这是存储所有长期性信息的地方。所有数据都不是静态的，存储在数据库中可以进行有效地查询。至少相对有效 - 最终数据库交互最可能成为Web服务性能瓶颈。由于本课程的重点是开发利用数据库的Web API，因此省略了有关数据库的大部分细节。这些可以从其他课程获得或在线学习。遵循现代网络开发的实践，我们甚至会跳过SQL（结构化查询语言），鼓励使用对象关系映射器 （object relation mapper ORM）。

这篇文章涉及数据库的几个主题（稍稍提及）：数据库是什么，设计考虑因素，如何在Python应用程序中使用它们以及如何在开发过程中维护它们。

## 数据库的结构

在本课程中，我们使用的是“传统”数据库，这些数据库具有预定义的结构，可存储所有信息。这包括众所周知的在Web开发中常用的MySQL和PostgreSQL，以及经常用于原型设计的SQLite。这些类型的数据库包含数据表。每个表都有一组预定义的列定义该表中的项必须或可以具有的属性。这些项目存储在行。此外，数据库中的不同表可以具有它们之间的关系，以便一个表中的列引用另一个表中的行。所有这一切都在数据库架构（database schema）中定义。

在数据表中一个比较重要的保证行独特性的概念就是主键（Primary key）。每个表至少指定一列为主键（简称PK）。对于每一行，PK值必须是唯一的。

另一种键叫外键（简称FK），通常在创建表之间的关系时要用到。表A中的外键字段是一个列，它只能通过使用表B中的唯一列来识别关系，从而获取引用表B中行的值。

## 对象关系映射
在本课程中，通过对象关系映射（简称ORM）管理数据库。在此方法中，数据库表及其关系在代码中作为对象进行管理。就像Flask如何隐藏很多有关如何使用的细节一样使HTTP请求成为Python函数调用，对象关系映射器隐藏了很多关于数据库表如何成为Python类（class）的细节，数据库操作变成了方法调用。虽然理解ORM自动生成的基础SQL查询对性能考虑很有用，但在正常的小规模使用中，我们所关注的一切都是Python代码。我们的示例使用的SQLAlchemy通过Flask SQLAlchemy的。它实际上不仅仅是ORM（实际上ORM只是它的一个可选组件），但是与本课程的总体主题一致，我们只是在表面上涉猎。

无论使用哪种ORM，定义数据库结构的基本方法是创建具有表示所调用列的各种属性的Python类，叫模型类（model class）。每个类对应于数据库中的一个表，并且初始化为列的类的每个属性表示表中的列。类实例（即对象）表示已从数据库检索到程序工作空间的行。请注意，通常是数据库架构（schema）是从类定义生成的。这就是为什么不事先创建模式的原因。事实上，因为我们现在正在使用SQLite，所以我们也不需要费心去创建数据库。使用Flask SQLAlchemy，创建简单表的类将如下所示：  

```py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(20), nullable=False)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
```

开头介绍了为了将SQLAlchemy与Flask一起使用所需要做的事情。我们只需要知道我们想要数据库的位置（同一文件夹中的文件）。第二个配置行是为了禁用警告，因为我们现在不需要跟踪修改。通过从flask_sqlalchemy初始化SQLAlchemy来获取数据库接口，然后使用此对象来定义我们的单个数据库类。在SQLAlchemy中，通过使用db.Column构造函数将属性定义为列，该构造函数将列类型作为第一个参数，将其他列属性作为关键字参数 - 请参阅[列属性](./appendix/ColomnAttribute.md) 术语表示常用关键字列表。  

如果您愿意，还可以覆盖模型的`__repr__`方法。这样做会更改模型实例在控制台中的显示方式。我们在本页的示例中没有这样做，但是将在后面的示例中执行此操作。否则它将显示为例如（型号名称和主键值）。例如，您可以编写一个显示测量值的方法，例：
```
<Measurement 1>uo-donkeysensor-1: 44.51 @ 2019-01-01 00:00:00
```

## 用ORM做些实事

此时我们还没有数据库。它可以从python控制台创建。转到flask应用的文件夹，激活Python控制台。这里使用[iPython](https://z42.readthedocs.io/zh/latest/devtools/ipython.html)，然后执行：

```py
In [1]: from app import db
In [2]: db.create_all()
```

>## 练习3：模型中的基础类
>
>**学习目的**：学会如何定义一个模型类
>**模型**：StorageItem
>
> - 列：
>   - id (integer, primary key)
>   - handle (string, max length 64, unique, not null)
>   - qty (integer, not null)
>   - price (float, not null)
>
>用Model作为基础类定义这个类，然后像例子中一样调用列构造器。
>
>> [答案_t3](./answer_ex1_t3.py)

## 添加对象

在此之后，您的应用程序文件夹会包含test.db文件，该文件现在是一个带有一个空表（名为measurement）的SQLite数据库。下一步是在表中添加一些行。在ORM模式中，这是通过创建模型类的实例来完成的。默认情况下，模型类有一个构造函数，它接受数据库列名作为关键字参数。请注意，单独创建实例不会对数据库执行任何操作。它需要标记为添加然后提交。因此，我们可以通过以下方式创建measurement实例：

```py
In [1]: from app import db, Measurement
In [2]: from datetime import datetime
In [3]: meas = Measurement(
   ...:     sensor="donkeysensor2000",
   ...:     value=44.51,
   ...:     time=datetime(2018, 11, 21, 11, 20, 30)
   ...: )
In [4]: db.session.add(meas)
In [5]: db.session.commit()
```

检验是否与数据库结构一致是在最后完成的，如果由于违反约束而无法完成一个或多个插入则会引发异常。通常为IntegrityError，并附有导致错误的原因解释。

## 检索对象

我们现在已将measurement值保存到数据库中。为了应用程序中使用这些数据，需要检索它。使用类的查询属性完成表中的搜索。检索起来十分很简单：

```py
In [1]: from app import db, Measurement
In [2]: Measurement.query.all()
Out[2]: [<Measurement 1>]
```

查询对象的all方法将表中的所有记录作为Python列表返回。这在我们的小测试中运行得很好，但在现实生活中我们一般不用将所有内容加载到内存中。这时应该使用filter_by方法执行过滤。  

```py
In [3]: Measurement.query.filter_by(sensor="donkeysensor2000").all()
Out[3]: [<Measurement 1>]
```

最后的all方法再次返回过滤结果，filter_by只返回一个查询对象。值得注意的是，filter_by是一种简单的过滤方法，仅适用于精确匹配。通过某个sensor查找值很有用，但如果我们想要找到高于某个阈值的值，则需要使用filter方法。语法不同：

```py
In [4]: Measurement.query.filter(Measurement.value > 100).all()
Out[4]: []
```

总而言之，我们可以使用SQLAlchemy的查询对象做各种查询（[SQLAlchemy文档-query](https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#querying) - 注意在我们使用Flask SQLAlchemy的例子中，是一个简写，完整写作`Measurement.querydb.session.query(Measurement)`）。  
不论是哪种查询，一旦我们取出查询结果，他们就是Measurement实例：
```py
In [5]: meas = Measurement.query.first()
In [6]: type(meas)
Out[6]: app.Measurement
In [7]: meas.sensor
Out[7]: 'donkeysensor2000'
In [8]: meas.value
Out[8]: 44.51
In [9]: meas.time
Out[9]: datetime.datetime(2018, 11, 21, 11, 20, 30)
```

## 删除和修改对象

修改十分简单，每当一个对象被修改了，它就会被标记（marked as dirty），之后的任何提交都会将这个修改应用到数据库中。  

```py
In [10]: meas.sensor = "donkeysensor2001"
In [11]: db.session.commit()
In [12]: Measurement.query.first().sensor
Out[12]: "donkeysensor2001"
```

从数据库中删除行也简单，和添加很相似：

```py
In [13]: db.session.delete(meas)
In [14]: db.session.commit()
```

如果这项操作失败了不会报错，只会给出警告。

## 新建关系

在ORM中管理由外键连接的表已经很方便了。通常有一种允许模型类相互引用的机制以便一个实例里的属性能与另一个模型类的产生直接联系。在我们的例子中，我们可以创建另一个包含sensors表，而不通过name来识别sensor。所以我们定义第二个模型类：

```py
class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    measurements = db.relationship("Measurement", back_populates="sensor")
```

我们可以看到，此表包含有关我们之前能够呈现的sensor的更多信息。我们还定义了一个关系属性。这创建了我们的外键连接的反面，可以方便地访问为此传感器记录的所有测量值。为了创建连接，我们需要修改Measurement类：

```py
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    sensor = db.relationship("Sensor", back_populates="measurements")
```

关系构造函数中的back_populates关键字参数表示它将在关系的另一侧（Sensor类）引用回该模型的属性。另请注意，使用db.ForeignKey定义外键时，必须使用表名（默认为小写的模型名），在创建与db.relationship的关系时，必须使用模型名称。

此时我们的数据库结构就改变了。这意味着我们必须删除数据库并从头开始重新创建它。用于生产的数据库，有一个名为的流程叫做数据库迁移（migration），不删除而是保留数据并修改它以适应新样式。  
我们删除数据库文件后，再次启动控制台并做一些操作：

```py
In [1]: from app import db
In [2]: db.create_all()
In [3]: from app import Sensor, Measurement
In [4]: from datetime import datetime
In [5]: sensor = Sensor( 
   ...:     name="uo-donkeysensor-1", 
   ...:     model="donkeysensor2000", 
   ...:     location="kylymä", 
   ...: )
In [6]: meas = Measurement( 
   ...:      value=55.41, 
   ...:      sensor=sensor, 
   ...:      time=datetime.now() 
   ...: )
```

较为奇妙的是：我们可以直接定义sensor属性而不是在Measurement对象中定义sensor_id，它会自动填充外键字段。这是比较方便的，因为这时我们的sensor实际上没有id，因为我们还没提交修改。提交后可以尝试查询并查看实际关系：

```py
In [7]: db.session.add(sensor)
In [8]: db.session.add(meas)
In [9]: db.session.commit()
In [10]: Sensor.query.first().measurements
Out[10]: [<Measurement 1>]
In [11]: Measurement.query.first().sensor_id
Out[11]: 1
In [12]: Measurement.query.first().sensor
Out[12]: <Sensor 1>
```

注意：在meas中添加sensor也可以省略，转而通过append方法把sensor实例添加到其属性上。（注意`db.session.add`也被省略了）

```py
In [13]: meas2 = Measurement( 
    ...:     value=12.35, 
    ...:     time=datetime.now() 
    ...:     )
In [14]: sensor.measurements.append(meas2)
In [15]: db.session.commit()
In [16]: Sensor.query.first().measurements
Out[16]: [<Measurement 1>, <Measurement 2>]
```

>
> ## 练习4：构造关系
>
> **学习目的**：学会如何用SQLAlchemy ORM定义一对多/多对一关系。
>
> 您将通过直接添加一个新的模型来拓展上一个练习。与示例类似，我们希望你创建的表能包含products的更多信息。另一个需要添加的是位置字段，以便数据库可以跟踪存储在不同位置的数据。
>
> **修改模型**：`StorageItem`
>
> - 需要新建的列：
>   - product_id (integer, foreign key product.id)
>   - location: (string, max length 64, not null)
> - 需要删除的列：
>   - handle
>   - price
>
> 这个模型类还需要定义一个叫product的关系，并带有Product表in_storage属性的反向引用（back reference）。
>
>> [答案_t4](./answer_ex1_t4.py)

**注：SQLite中的外键**  

默认情况下SQLite不强制执行外键约束。换句话说，如果你使用上面的方法来创建相关的对象，你就不被允许违反它们。唯一的方法是手动将外键字段（例如sensor_id）值设置为无效的值。但是，你仍然应该知道将此代码段放在应用程序中会为SQLite启用外键（来源：[SQLite文档](https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html)）：

```py
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

## “同生共死”

由于外键被约束到另一个表中存在的值，当删除另一个表中的目标行时会发生什么？答案是：取决于给它分配的操作。最常用的操作是将指向被删除行的那一行也删除（CASCADE）。或者将它的值设为空（SET NULL）。同理，更新项目也适用：如果设置cascade，外键的值也会随着它指向的值改变。当同时把主键设为外键时作用不大，因为此时一般主键不会改变。设置这些属性只需要在外键构造器中添加ondelete和onupdate属性并赋以相应字符串值，例如："CASCADE" 和 "SET NULL"。

操作的选择取决于它将如何被应用。例如，删除sensor数据时，我们例子中的sensor如果使用cascade将会丢失measurement数据，所以我们设置set null，measurement记录得以保存，但它将不属于任何sensor。通常这两种做法都不是很好，最好不要删除sensor，而是给他们做一个标记“inactive”。  
这里我们暂且只选择set null。

```py
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    sensor = db.relationship("Sensor", back_populates="measurements")
```

## 通过关系查询

有时候把数据放到关联起来的表里就行了，但当我们想要，比如，查找所有被同一个sensor测量出的measurement记录时该怎么办？简单的查询做不到这一点，因为我们要的信息不在一张表上。这就需要用到SQLAlchemy的join方法。它是一个SQL连接语句的简化版本，可用于涉及多个表的查询。那么刚刚问题的答案就是：

```py
In [1]: from app import db, Measurement, Sensor
In [2]: Measurement.query.join(Sensor).filter(Sensor.model == "donkeysensor2000").all()
Out[2]: [<Measurement 1>]
```

我们需要的结果来自左表，同时也有我们要用作join方法搜索的参数列。我们当然可以从measurement中向过滤方法中填加列以筛选到超过某阈值的记录：

```py
In [3]: Measurement.query.join(Sensor).filter(Sensor.model == "donkeysensor2000",  Measurement.value > 1.0).all()
Out[3]: [<Measurement 1>]
```

## 现代关系模型

如果我们的数据库中只可能有一种关系，那就有些落后了。尽管多对一在这门课程中最常用的用例关系，但wine本周股市该应知道如何使用SQLAlchemy定义其他类型关系。一对一的关系很容易定义，因为它只是对上述多对一关系的修改。这是通过将关系构造函数的关键字参数`uselist`设置为`False`来实现的。例如，让我们将传感器的位置参数转换为位置表，每个位置只能容纳一个传感器：

```py
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    description=db.Column(db.String(256), nullable=True)

    sensor = db.relationship("Sensor", back_populates="location", uselist=False)

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))

    location = db.relationship("Location", back_populates="sensor")
    measurements = db.relationship("Measurement", back_populates="sensor")
```

多对多关系就没有那么简单明了。它需要创建一个由引用对组成的“关系表”，每个关系的两边都各有一个外键。这些是必须的，因为数据库的列中不能存在可变的序列类型变量（比如你的数据库表中不能有python list - 尽管理论上你可以将list序列化但这会很不明智，因为数据库将不能理解表之间的关系了，从而使你的查询效率低下）

举个例子，如果我们创建一个deployments新表 - 描述在一段时间内sensor所部署的位置。由于deployment包含许多sensor，sensor也可以表示在许多deployment中，这就是一个多对多关系。正如之前所说，需要新建一个辅助表来实现这个关系。由于我们不打算直接使用这个表，因此应将其定义为表而不是模型：

```py
deployments = db.Table("deployments",
    db.Column("deployment_id", db.Integer, db.ForeignKey("deployment.id"), primary_key=True),
    db.Column("sensor_id", db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
)
```

通过同时设置二者为主键，两个列共同形成了这个表。来自两列的每一对值都是独一无二的，它产生一个类似这样的表：  
| deployment_id | sensor_id |
|--|--|
|1|1|
|1|2|
|2|1|
|2|2|
  
>  
> ## 练习5：关系干预
>
>我们来练习使用关系模型。当尝试创建错误时会发生什么？在python控制台中创建模型也是一种很好的做法。 
>
>**学习目标**：测试当关系限制时会发生什么  
>
>**在你开始之前**：下载sensorhub应用文件: <a href="./appendix/app_ex1_t5.py" download>app_ex1_t5.py</a>  
>
>将它放在虚拟环境中的文件夹中，然后打开IPython。键入以下两行。其余的你必须弄清楚自己。
>
>```py
>In [1]: from app import db, Deployment, Location, Sensor
>In [2]: db.create_all()
>```
>
>你需要为每个位置创建两个location实例（A 和 B）和相应的sensor（s1对应地址A，s2对应B）。最后你需要创建一个包含两个sensor的deployment实例。你的任务是弄清如何创建这些实例。在多对多关系中，使用append来向关系中添加对象（例：`deployment.sensor.append(s1)`）  
>
>**任务步骤**
>
>该任务有两个步骤，答案分为四行，请使用print在控制台查看你需要读取的值。  
>
>**注意**：如果出现一场，你需要在继续之前使用`db.session.rollback()`来回滚事务。
>
>1. 将sensor s1位置改为B。
>    1. 首先改变模型中的位置，然后查看s2的location值
>    2. 提交此次更改，看是否出错，如果出错，查看是什么错误；否则查看传感器s2的location值
>2. 重复将s1添加到deployment中
>    1. 将s1 append到sensor列表中，查看deployment列表的值
>    2. 提交此次更改，看是否出错，如果出错，查看是什么错误；否则查看deployment的sensor列表
>
>>答案：  
>><Location 2>  
>>IntegrityError  
>>[<Sensor 1>, <Sensor 2>, <Sensor 1>]  
>>[<Sensor 1>, <Sensor 2>]  
>

## web开发中的数据库

尽管在控制台管理数据库有时会有用，但实际上我们不经常这么做。通常，当通过HTTP请求将某些内容添加到数据库时，它将使用POST方法完成，并且行的值包含在request body中。使用Flask，访问request body的方式因请求的MIME类型而有所不同。在交互式web应用中，这些值通常来自于一些表单，这可以通过`request.form`这个类似字典的对象（类似`request.args`）访问到。举一个带有最简化错误码返回的例子（并从服务器返回时间戳而非客户端）。

```py
@app.route("/measurements/add/", methods=["GET", "POST"])
def add_measurement():
    if request.method == "POST":
        # 当用户提交这个表单时：
        try:
            sensor_name = request.form["sensor"]
            sensor = Sensor.query.filter_by(name=sensor_name).first()
            if sensor:
                value = float(request.form["value"])
                meas = Measurement(
                    sensor=sensor,
                    value=value,
                    time=datetime.now()
                )
                db.session.add(meas)
                db.session.commit()
            else:
                abort(404)
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    else:
        # 当用户加载表单并将其渲染为HTML时
        pass
```

这是一个非常常见的处理表单的view函数代码结构。它同时用这个URL对表单进行查询和提交，并且把两种不同的请求方式区分开来（应当注意我们必须在路由中定义允许这两种方式）在实际应用中，我们返回更准确的的错误消息。而且，我们还需要对表单进行验证处理。

通常数据通过文档符号格式（document notation format）传输，目前大部分是JSON格式（以前是XML）。JSON有着自己的MIME类型并且Flask通过request.json使数据得以作为Python数据结构传输（实际上是json.loads对request body处理后的结果）。

假设JSON文件像这样：

```json
{
    "sensor": "uo-donkeysensor-1",
    "value": 44.51
}
```

我们的代码读取并像这样把它保存到数据库中。要注意这次只有一种请求方式是允许的，所以不需要过多的判断它：

```py
@app.route("/measurements/add/", methods=["POST"])
def add_measurement():
    # This branch happens when user submits the form
    try:
        sensor_name = request.json["sensor"]
        sensor = Sensor.query.filter_by(name=sensor_name).first()
        if sensor:
            value = float(request.json["value"])
            meas = Measurement(
                sensor=sensor,
                value=value,
                time=datetime.now()
            )
            db.session.add(meas)
            db.session.commit()
        else:
            abort(404)
    except (KeyError, ValueError, IntegrityError):
        abort(400)
```

但是，由于此处的sensor实际上是作为数据库中的对象存在的东西，因此通常最好将其作为变量包含在URL中，而不是从请求主体中提取的内容。这样，当API为未知sensor返回404时，客户端开发人员可以更容易地确定他们请求的sensor与任何现有的不匹配，并且问题出在URL中。

```py
@app.route("/<sensor_name>/measurements/add/", methods=["POST"])
def add_measurement(sensor_name):
    # This branch happens when user submits the form
    try:
        sensor = Sensor.query.filter_by(name=sensor_name).first()
        if sensor:
            value = float(request.json["value"])
            meas = Measurement(
                sensor=sensor,
                value=value,
                time=datetime.now()
            )
            db.session.add(meas)
            db.session.commit()
        else:
            abort(404)
    except (KeyError, ValueError, IntegrityError):
        abort(400)
```

> ## 练习6：库存管理：web api实现
>
> 总结本练习要点，暂时不考虑API设计原则创建小API应用。基于之前的任务，完善这个库存管理系统。  
>
> **学习目标**：创建一个简单的Flask应用，并允许通过接口的GET和POST请求管理数据库
> **在你开始之前**：  
> 在简历关系模型的练习中我们已经有了这个应用的基础。你可以基于那个开始本次练习。  
>
> 在实现使用POST功能时，你也需要了解如何进行[测试](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/testing-flask-applications#how-to-send-post-and-other-requests)  
>
> **注意**：由于Flask的测试客户端的实现方式，您的代码必须通过访问JSON数据`request.json`
> **第一个函数**：add_product
>
> - 路径： `"/products/add"`
> - 参数：
>   - 没有参数
> - 请求正文JSON字段：
>   - "handle" （字符串）
>   - "weight" （浮点）
>   - "price" （浮点）
> - 返回值：
>   - 201：如果成功的话
>   - 400："Weight and price must be numbers"或"Incomplete request - missing fields"
>   - 405："POST method required"或Flask的默认405消息
>   - 409："Handle already exists"- 如果已存在具有相同句柄的产品
>   - 415："Request content type must be JSON"- 如果请求正文无法作为json加载  
> 该函数将从客户端发送的JSON文档中获取产品信息，并使用给定信息在数据库中创建新产品。如果请求以多种方式出现故障，您可以选择要返回的错误代码。据推测，客户端开发人员将首先修复该错误，然后在后续尝试中获取第二个错误。
>  
> **第二个函数**： add_to_storage
>
> - 路径：`"/storage/<product>/add"`
> - 参数：
>   - 要添加到存储中的产品（产品手柄）
> - 请求正文JSON字段：
>   - "location" （串）
>   - "qty" （INT）
> - 返回：
>   - 201：如果成功的话
>   - 400："Qty must be an integer"或"Incomplete request - missing fields"
>   - 404："Product not found"- 如果手柄没有找到产品
>   - 405："POST method required"或烧瓶的默认405消息
>   - 415："Request content type must be JSON"- 如果请求正文无法作为json加载
>由于数据库ID并不具有任何意义，因此产品由其他唯一字段标识：handle。因此，该函数必须检查给定句柄是否与数据库中的产品匹配，如果不匹配则返回404。如果请求有效，则该函数必须创建与所选产品相关的存储条目。
>
> **第三功能**： get_inventory
>
> - 路线： "/storage/"
> - 参数：
>   - 没有参数
> - 返回：
>   - 200：包含作为对象数组的库存的JSON文档
>   - 405："GET method required"- 如果方法不是GET  
>
> 如果使用GET方法调用此URL，则会将完整清单提取到一个列表中，该列表将来自两个数据库表的数据汇总在一起。该列表为每个现有产品都有一个项目。这个项目是一个包含以下键的字典：
>
>- "handle"：产品的手柄
>- "weight"：产品重量
>- "price"：产品价格
>- "inventory"：此产品的存储条目列表 - 每个指示位置和数量的元组。  
>
>这个数据结构将作为JSON放入响应体中（您可以使用json.dumps对其进行序列化），例如（为读者的理智添加缩进）：
>
> ```js
>[
>    {
>        “handle”：“donkey plushie”，
>        “weight”：1.20，
>        “price”：20.00，
>        “inventory”：[
>            [“shop”，2]，
>            [“warehouse”，42]
>        ]
>    }
>]
> ```
>> 答案：[answer_ex1_t6.py](./answer_ex1_t6.py)  
> 