# 用FLASK实现REST API
本文将讲到如何使用[Flask-RESTFUL](http://www.pythondoc.com/Flask-RESTful/index.html)，一个Flask的扩展，实现REST API。我们也将讨论如何在你的开发过程中有条理地处理超媒体（hypermedia）

## Flask-Restful 简介  
在练习的第一部分，我们将介绍如何使用RESTful扩展包。为此我们回到第一篇文章中的[sensorhub例子](https://raw.githubusercontent.com/XCifer/Programmable-Web-Project/master/Exercise_1_IntroductiontoWebDevelopment/appendix/app_ex1_t5.py)。简单回顾一下，我们在sensorhub的例子中主要有4个概念：测量 measurements，传感器 sensors， 传感器位置 sensor locations 和 部署参数 deployment configurations。接下来我们将把这些概念变成API的资源（resources）。

### 安装
这里我们需要用到新的Python模块。启动之前创建的虚拟环境然后输入以下命令：

``` 
pip install flask-restful
pip install Flask-SQLAlchemy
pip install jsonschema
```

## 资源类
Flask-RESTful定义了一个称为Resource的类。就像Model是数据库中所有模型的基类一样，Resource是我们所有资源的基类。一个资源类都应有对应各HTTP请求的方法。这些方法的名称必须与小写的相应HTTP方法相同。例如，集合类型资源通常将具有两种方法：get和post。这些方法在实现上与view函数非常相似，但它们没有路由前缀——它们的路径取决于本身resource的路径。假设我们要在传感器sensor创建两个资源类：传感器的列表以及单独的能查看对应测量值的传感器。资源类的写法如下：

```python  
from flask_restful import Resource

class SensorCollection(Resource):

    def get(self):
        pass

    def post(self):
        pass


class SensorItem(Resource):

    def get(self, sensor):
        pass

    def put(self, sensor):
        pass

    def delete(self, sensor):
        pass
```

我们使用对单独的传感器使用SensorItem而不是Sensor，因为我们把model文件名命名sensor了，当所有代码都在一个文件中时容易引起冲突。当然我们在大型项目中推荐使用此项目[布局规范](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/flask-api-project-layout/)。

而这写方法看起来就像view函数一样。例如，这是SensorCollection的一个post方法，就像练习一种的add_measurement函数一样。

```python
    def post(self):
        if not request.json:
            abort(415)
            
        try:
            sensor = Sensor(
                name=request.json["name"],
                model=request.json["model"],
            )
            db.session.add(sensor)
            db.session.commit()
        except KeyError:
            abort(400)
        except IntegrityError:
            abort(409)
        
        return "", 201
```
注意：所有方法都必须具有相同的参数，因为它们都是源自相同的资源URI。但是你可以在这些方法中用不同的查询参数。比如，对某些支持筛选或排序的资源在其get方法里使用参数查询是可行的。

## 资源路由
为了使任何东西都能在Flask-RESTful中工作，我们需要初始化一个API对象。该对象将处理诸如路由之类的事情。继续我们的示例，我们将展示如何创建此对象，并且如何用它来注册到两个资源类的路由。在单文件的应用程序中十分简单，从flask_restul导入Api，并创建其实例：  
``` python
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
```
假设资源类位于同一文件中，现在可以通过在文件末尾写下这两行来为它们添加路由。
```
api.add_resource(SensorCollection, "/api/sensors/")
api.add_resource(SensorItem, "/api/sensors/<sensor>/")
```
现在你就能发送GET和POST请求到`/api/sensors/`了，也可以发送GET、PUT、DELETE到诸如`/api/sensors/uo-donkeysensor-4451/`的路径。

>  
> ## 资源“库存管理”
> **学习目标：** 使用Flask-RESTful用两种方法实现一个简单的集合类型资源。
> **开始之前：** 你可能需要之前相关练习的[代码](https://raw.githubusercontent.com/XCifer/Programmable-Web-Project/master/Exercise_1_IntroductiontoWebDevelopment/answer_ex1_t6.py)。具体来说，POST方法会与`"/products/add"`路径下的view函数相类似。  
> **资源：产品集合ProductCollection** 
> - 路径：`"/api/products/"`  
> - 方法：  
>   - GET - 获取所有产品列表（返回JSON格式的对象）
>   - POST - 创建新的产品  
>  
> **GET：** 这个方法从数据库中检索所有产品信息并返回一个列表，其中每个产品都是一个以数据表列名作键值的dictionary对象。这是一个较为有效的简版`"/storage/"`路径的view函数。返回值的一个例子：
>```json
>[
>    {
>        "handle": "donkey plushie",
>        "weight": 1.20,
>        "price": 20.0
>    }
>]
>``` 
>注意：如果在某个方法中有返回值，Flask-RESTful会自动把Python数据结构转换为JSON格式。所以与上次不同的是，这里我们**不需要**在返回值时用`json.dumps()`转换。  
> **POST：** 创建一个产品，如果成功返回201，如果失败就返回其他状态码。这也与之前的功能相类似。只需简单地把`"/products/add/"`路径下的view函数放到资源类的POST方法中。
>
>总的来说，你的代码需要做以下事情：Flask-RESTful初始化，每个资源类将要有两个方法，并且用`api.add_resource`方法为资源注册路径。
> > 答案：

注意：使用更复杂的项目结构时，资源都应放在`api.py`文件中，然后在使用时把对应的资源他们独立的文件中导入进来。下面是`api.py`的一个例子，并且假设资源类已经保存到resource文件夹的`sensor.py` 中。
```py
from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from sensorhub.resources.sensor import SensorCollection, SensorItem

api.add_resource(SensorCollection, "/sensors/")
api.add_resource(SensorItem, "/sensors/<sensor>/")

@api_bp.route("/"):
def index():
    return ""
```
## 更复杂的资源  
在寻址时，仅定义了每个资源都必须通过其独一无二的地址来进行标识，但没说明不能用多个地址。有时同一个资源需要能在不同的URI路径下找到，这也就讲得通了。举个例子，电子游戏通常有开发者和发行商，那么以下的两种URI格式就很有道理：  
- `/api/publishers/{publisher}/games/{game}/`
- `/api/developers/{developer}/games/{game}/`
以上两者是不同的识别同一资源的方法。幸运的是Flask-RESTful允许对每个资源定义多个地址。路由方式如下：
```py
api.add_resource(GameItem, 
    "/api/publishers/<publisher>/games/<game>/",
    "/api/developers/<developer>/games/<game>/"
)
```
如果你像这样定义路由，你必须考虑到它不是总能收到相同的关键参数，它会收到发行商或开发者中的一个。在这种情况下，资源GameItem的get方法可以像这样写：
```py
class GameItem(Resource):

    def get(game, publisher=None, developer=None):
        if publisher is not None:
            game_obj = Game.query.join(Publisher).filter(
                Game.title == game, Publisher.name == publisher
            ).first()
        elif developer is not None:
            game_obj = Game.query.join(Developer).filter(
                Game.title == game, Developer.name == developer
            ).first()
```
你也可以通过多个路由将多个类似的资源放到一个资源类中实现。例子MusicMeta API就是这么做的。将单个歌手的专辑和群星专辑一同归为专辑资源。事实上也没有单独的群星的路径，我们只是将群星作为艺术家名字的特殊值，路由如下：
```py
api.add_resource(AlbumItem, "/api/artists/<artist>/albums/<album>/")
```

## 反向路由  
另一个我们即将使用的功能是从路由生成URI。在超媒体资源中，URI将被反复使用，并且对其硬编码会很麻烦。用`api.url_for()`会方便很多。回到我们的sensorhub例子，在这里我们会需要检索URI（传感器集合和单个传感器）：
```py
collection_uri = api.url_for(SensorCollection)
sensor_uri = api.url_for(Sensor,sensor="uo-donkeysensor-4451")
```
这个方法会找到第一个与资源类和给定变量相匹配的路径，或是在没找到的时候抛出BuildError。如果找到了，URI会作为字符串返回：
```
/api/sensors/
/api/sensors/uo-donkeysensor-4451/
```
> ## 资源定位器
> **学习目标：** 学习如何返回response对象并自定义header。
> **开始之前：** 复制前一个练习的代码。现在你也需要为Product资源定义一个虚拟对象和一条路由。用以下资源类足够：
> ```py
> class ProductItem(Resource):
>    
>     def get(self, handle):
>         return Response(status=501)
> ```
> 你需要完成路由，路径为`"/api/products/<handle>/"`。
> **Response对象：**  
> 为了能够返回Response对象，你还需要从Flask中导入Response模块。
>```py
>from flask import Flask, Response, request
>```
> response对象可以在view函数（或HTTP方法）中返回。你可以在[这里](https://flask.palletsprojects.com/en/1.0.x/api/#response-objects)查看相关文档。最主要的参数如下：
> - status - 状态码
> - mimetype - response body的类型
> - headers - dictionary类型的HTTP headers
>
>创建一个response对象时，第一个参数就是response body（如果有的话）。你可以用data关键字作为替换。在这个练习中我们还需要headers参数 —— 由hearder-value键值对构成的dictionary。
> **修改资源：Product Collection**
> 在上个练习中为新创建的产品添加一个名为location的header。建议使用`api.url_for()`。
>
>你可以通过允许你的app进行测试
>> 答案：

# 生成超媒体
这个部分，我们学习如何用dictionary的子类创建超媒体control，以及如何在超媒体response中加入JSON 模式（schema）。
## 利用子类
在Mason中，超媒体response的跟类型是JSON对象 —— 相当于Python中的dictionary。如果你将每个资源方法中的整个response定义为字典，很可能会造成不兼容。另外，代码也会变得难以维护。对于任何返回JSON的应用，在开始时创建一个包含很多将JSON自动格式化方法的字典的子类会是一个较好的开发模式。 
  
综上所述，本课程中选择的超媒体类型为Mason。在Mason的JSON文件中有三种常用参数：`"@controls"`，`"@namespace"`，`"@error"`。

这就是我们需要的一个有namespace和control的dictionary（这个例子是Sensor资源的get方法的一部分）:
```py
body = {}
body["@namespaces"] = {
    "senhub": {
        "name": "/sensorhub/link-relations/#"
    }
}
body["@controls"] = {
    "senhub:measurements": {
        "href": api.url_for(MeasurementCollection, sensor=sensor_name)
    }
}
# add some data about the sensor etc 添加一些关于传感器的信息
```

若要如上的代码通常会很多很乱。我们更希望我们的代码像如下这样：  
```py
body = MasonBuilder()
body.add_namespace("senhub", "/sensorhub/link-relations/#")
body.add_control("senhub:measurements", api.url_for(MeasurementCollection, sensor=sensor_name))
```

毫无疑问的是这样看起来更整洁一些，这个MasonBuilder类将负责将namespace和control加入对象中。如果有需要对这个对象做出改变，只需要在这个类里面改就能应用到所有资源的方法上。这个MasonBuilder类像这样：
```py
class MasonBuilder(dict):

    def add_namespace(self, ns, uri):
        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }
    
    def add_control(self, ctrl_name, href, **kwargs):
        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href
```

请观察`MasonBuilder`是如何继承python的dict类的，所以创建一个`MasonBuilder`实例和用`dict`类创建一个dictionary一样。  

具体操作：在`MasonBuilder`中的`**kwargs`涉及到python中的打包和解包。它是在调用函数或方法时用来捕获参数的通配符 —— 所有的参数都会打包到kwargs的对象中。所以当我们在`method="POST"`时调用这个方法，kwargs最后会变成`{"method":"POST"}`。这个功能也会用在dict的初始化`__init__`方法中，你可以通过参数用一堆键将其初始化。 

因为每个对象只能有一个`"@controls"`和一个`"@namespaces"`属性，所以可以在第一个control/namespace添加的时候创建这个参数。我们也可以用类似方法添加`"@error"`属性。  
```py
    def add_error(self, title, details):
       self["@error"] = {
            "@message": title,
            "@messages": [details],
        }
```
你可以在下面下载带有注释的整个class文件，如果你使用更规整的文件结构，你可以将其放在`utils.py`文件中，然后在其他模块中导入它。```from sensorhub.utils import MasonBuilder```

> [mansonbuilder.py]()

因为在一个集合类的资源中需要control，所以需要用MasonBuilder实例而非dictionary。这样你就可以轻松的在根对象上添加control。让我们看个例子，如何将至关重要的“self”关系加入到每个传感器集合资源的表示中。
```py
body = MasonBuilder(items=[])
for sensor in Sensor.query.all():
    item = MasonBuilder(
        name=sensor.name,
        model=sensor.model
    )
    item.add_control("self", api.url_for(Sensor, sensor=sensor.name))
    body["items"].append(item)
```

# API的具体子类

像我们刚刚写的通用JSON构造器很好用，但是不能完全解决问题。 特别是因为add_control方法仅真正适用于GET方法，如果要添加DELETE方法，则需要在方法调用中加入相应代码以复用：

```py
body.add_control("senhub:delete", api.url_for(Sensor, sensor=sensor_name), method="DELETE")
```

这里不需要很多代码，但实际上正确的HTTP删除方法DELETE已经整合在关系定义`"senhub:delete"`中，所以这里我们是在这里第二次输入相同的信息：

```py
body.add_control_delete_sensor(sensor_name)
```

因为所有的用于删除的control看起来都很类似，我们把所有无聊的重复都写进方法，把不同control里的变量作为参数传入：这个control会删除对应sensor的识别器。构造URI的方法也会被封装起来，因为用法总是一样的。写这些类似方法我们需要定义一个作为MasonBuilder子类的新类 - 这样这个通用构造器就能保持不变。这个新类所包含的一个方法如下：

```py
class SensorhubBuilder(MasonBuilder):

    def add_control_delete_sensor(self, sensor):
        self.add_control(
            "senhub:delete",
            href=api.url_for(Sensor, sensor=sensor),
            method="DELETE",
            "title"="Delete this sensor"
        )
```

这样，我们现在确保删除sensor的每个control将始终相同。我们甚至能够添加可选的title属性，而不会给资源方法带来更多干扰。或者，如果您不想有一种删除每种不同类型资源的方法，则可以对更通用的删除控件进行如下操作：

```py
class SensorhubBuilder(MasonBuilder):

    def add_control_delete(self, href):
        self.add_control(
            "senhub:delete",
            href=href,
            method="DELETE",
            title="Delete this resource"
        )
```

# 动态模式，静态方法

<!-- In exercise 2 we sung the praises of adding JSON schemas to our hypermedia controls. Schemas do have a nasty drawback: they are awfully verbose. If a control with like three attributes was already deemed something we'd rather not repeat in our code unnecessarily, a schema that's easily over ten lines of code is definitely something that must be written in only one place. It's also worth recalling that we have two uses for them: serialize them as parts of controls, and also to use them for validating request bodies sent by the client. -->

“模式”在POST和PUT control，以及使用查询参数的方法中通常会用到。同一个模式在代码中会被反复利用，因此不会将其硬编码到某一个add_control方法中。实际上，也不应该将其放到任何常规的方法中，因为我们有时会在没有SensorhubBuilder实例的时候会用到这些模式。所以，模式应当由静态方法return，或内置在class属性中。只有在某些需要参数化的情况下才倾向于选择静态方法。那么这里将加入一个构造sensor模式并返回的静态方法：
```py
@staticmethod
    def sensor_schema():
        schema = {
            "type": "object",
            "required": ["name", "model"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Sensor's unique name",
            "type": "string"
        }
        props["model"] = {
            "description": "Name of the sensor's model",
            "type": "string"
        }
        return schema
```

补充：静态方法是可以在没有类实例的情况下调用的方法，并且它通常也不引用任何类属性（这是类中方法的作用）。换句话说，它实际上是一个函数，只是为了使它更规整而放在类上使用了。它可以像这样`self.sensor_schema()`作为一个普通的类中的方法调用。在类外部，像这样`SensorhubBuilder.sensor_schema()`调用。  

这个静态方法可以作为control用来添加新的sensor（类似的可以用来修改sensor）：

```py
def add_control_add_sensor():
        self.add_control(
            "senhub:add-sensor",
            "/api/sensors/",
            method="POST",
            encoding="json",
            title="Add a new sensor",
            schema=self.sensor_schema()
        )
```

> ## 库存生成器
>
> **学习目标：** 学习如何通过字典子类的简便方法来添加control并维护Mason超媒体文档。  
> **开始之前：** 下载之前的MasonBuilder类以作为该任务开始，然后自己写一个类作为MasonBuilder的子类。 
> 建议完成从前面的任务代码的基础上继续这个任务。 <!-- - these pieces must be in place for api.url_for to work. We also recommend that you change the model name of StorageItem to StorageEntry to avoid mixups later. Remember also that the MasonBuilder code should be included in the file you send. -->  
>
> **库存生成器类：InventoryBuilder**  
> 在这个任务中，你需要创建一个类，该类可用于添加与库存管理器的与产品资源对应的超媒体control。这个类需要有以下方法
> - `add_control_all_products`
>   - 参数：无
>   - rel: `"storage:products-all"`
>   - 指向所有产品的列表 (GET `/api/products/`)
> - add_control_delete_product
>   - 参数： product handle
>   - rel: "storage:delete"
>   - 删除该产品 (DELETE `/api/products/{handle}/`)
> - `add_control_add_product`
>   - paramaters: -
>   - rel: `"storage:add-product"`
>   - 创建新的产品 (POST `/api/products/`)
>   - 模式（需要，具体要求如下）
>     - handle: string
>     - weight: number
>     - price: number
> - `add_control_edit_product`
>   - parameters: product handle
>   - rel: `"edit"`
>   - 编辑一个产品 (PUT `/api/products/{handle}/`)
>   - 模式（需要，与上面一样）
> > 答案：

另一个可以用静态方法返回模式的地方就是相应的模型类。如果感兴趣你甚至可以让可以用这些模型来生成模式，[这里](https://github.com/podhmo/alchemyjsonschema)是一个你可以参考的例子。


# 响应与错误
我们先简要地讨论一下Flask的response对象。在资源定位器练习中，我们用了response来自定义header。现在我们将在所有的响应中用到它。主要因为我们需要声明响应的content type，并且会用到mimetype的关键字参数。由于我们使用Mason，我们需要将其设置为`"application/vnd.mason+json"`。因为这会在每个GET方法中使用到，所以最好将其设为常量（比如`MASON = "application/vnd.mason+json"`）。那么现在，一个标准的200响应如下：
```py
return Response(json.dumps(body), 200, mimetype=MASON)
```
我们又开始使用json.dumps，因为Response对象将response body视作字符串。在201和204的响应也需要这样的转换。我们之前已经学了如何发送带有Location header的201响应，204响应则更为简单：
```py
return Response(status=204)
```
现在我们已经解决了200等成功操作的响应。那么400的错误响应呢？Mason也定义了错误的情况。实际上，我们已经在MasonBuilder的子类中写过add_error方法了，但是尽管如此返回错误还是十分麻烦，因为那只是个样板并且resource方法通常在执行过程多个节点返回错误。我们需要一个方便的方法来生成error响应：
```py
def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
```
这个方法能生成一个带标题的Mason错误信息，并且在其详情中有更多对错误描述。它也把资源URL放在了资源的body中，以防在客户端忘记当前操作的对象。现在我们不需要在每次需要返回错误的时候写一遍这个代码，只需这样：
```py
return create_error_response(404, "Not found", "No sensor was found with the given name")
```

# 超媒体的静态部分

除了让资源生成超媒体的形式，一个功能齐全的超媒体API也需要提供静态内容，即，link relations 和resource profiles。并且，如果你有相当大的模式而且希望将他们区分于资源的表现形式，那就需要将其转换为静态内容。对于profiles 和link relations你有两种选择：将其存放至单独静态文件，或是重新定位到apiary。