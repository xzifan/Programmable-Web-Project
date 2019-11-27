# 学习目标
在本练习中，你将学习如何使用Python或通过在网站中嵌入客户端来实现一个RESTful风格的客户端。

# 实现超媒体客户端
在这个最后的练习中，我们将探讨关于API的另一个难题：客户端。在之前的练习中，我们一直在讨论超媒体的优势以及给客户端开发人员带来的帮助。现在是时候展示如何实现这些神话般的客户端了。本练习材料提供两个示例：一个全自动机器客户端（Python脚本）和一个为人类用户生成用户界面的浏览器客户端（带有jQuery的Javascript）。我们将向您展示如何使客户端拥有抗API变化的强大功能。

我们在本练习中使用了MusicMeta API。原因之一是我们对这个API的超媒体表达形式更为熟悉。同时在练习2中，我们已经设想了一些客户，所以我们不需要从头开始创建一个新的想法。

## 使用Python的API客户端
我们第一个客户端将通过提交脚本来管理其本地MP3文件，并可以将其元数据与存储在API中的元数据进行比较。如果API中没有包含这个本地文件中的数据，该数据会被自动添加。如果其中存在冲突，它会通知用户并询问他们的意见 - 毕竟这不是一门人工智能课程。

**学习目标**：使用Python的Requests库来制定HTTP请求。HTTP请求是客户端使用HTTP协议向服务器发出的全部请求。它包括请求URL，请求方法（GET，POST等），标头和请求正文。在Python Web框架中，HTTP请求通常被转换为请求对象。[HTTP请求规范](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html)

### 准备
这个练习中我们需要用到Python中的另一个模块，我们将通过[Requests](https://2.python-requests.org//en/master/)来调用API. 请像往常一样在虚拟环境中安装好该模块：
```python
pip install requests
```
为了提高趣味性并展示更多的API开发工具，我们在此不提供服务器代码; 相反，我们要求您使用[Apiary](https://apiary.io/)中的模拟服务器来测试客户端。为此，我们将为您提供您在[练习2结束时](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/README.md#练习四api-blueprint---artist)完成的API Blueprint的更新版本 - 添加了记录tracks group资源的文档，您可以将其粘贴到现有文档中。该版本还修复了在模拟服务器测试客户端过程中发现的一些错误，因此请务必同时更新您文档中的相册资源部分(album)。同时，我们还将入口点(entry point)添加成为了一项资源，以便被客户端获取。

为了能正常工作，**您需要将您在[练习2最后一个任务](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/README.md#练习四api-blueprint---artist)中完成的Artist资源文档与下面我们提供的文档结合起来**. (请确保您在练习2中最后一个任务中完成的文档是正确的)

[musicmeta.md](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/musicmeta.md)

查看Apiary文档时，可以在“检查器” (Inspector) 选项卡中找到模型服务器的地址。

请注意，从技术上讲，返回400状态代码的一些响应示例中仍然存在错误，因为我们错误地拆分了一些字符串，以使示例更具可读性（jsonschema生成的JSON验证错误）。这些对于测试无关紧要，但如果您希望一切都能完全运行，则应删除换行符。最后，关于模拟服务器：它使用请求的Accept标头来确定它将发送哪个响应。这意味着它会给PUT，POST和DELETE请求发送第一个错误响应，因为对于PUT，POST和DELETE来说，成功响应是没有响应主体的，因此也没有内容类型。您可以通过两种方式解决此问题：
1. 用`"application/vnd.mason+json"`作为201和204响应的内容类型，即使没有返回主体，例如`+ Response 204 (application/vnd.mason+json)`
2. 或者在测试中不使用Accept标头，或者将* / *添加到Accept标头值（用逗号分隔）。

请注意，由于模拟测试仅对其示例中包含的数据进行操作，因此您的请求必须与这些示例匹配才能成功。尤其是您无法测试创建一个新资源然后请求该资源。

### 使用请求
Requests的基本用法非常简单，与Flask的测试客户端的用法非常相似。但是一个最明显的区别是，现在我们正在做一个真实的HTTP请求。与测试客户端一样，Requests对每一个HTTP方法都提供一个函数接口。这些函数也采用类似的参数：URL是必需的第一个字段，然后是标头，参数和数据等关键字参数（分别是请求标头，查询参数和请求主体）。例如，下面的例子教您如何要获取艺术家集合资源 - artists collection（请将SERVER_URL替换成您自己的Apiary模拟URL）：
```python
In [1]: import requests
In [2]: SERVER_URL = "http://private-xxxxx-yourapiname.apiary-mock.com")
In [3]: resp = requests.get(SERVER_URL + "/api/artists/")
In [4]: body = resp.json()
```
发送POST请求实际上并不对模型服务器执行任何操作，并且无论您发送什么数据，它都将使用固定的Location标头进行回复。但它足以测试客户端：
```python
In [5]: import json
In [6]: data = {"name": "Mono", "location": "JP"}
In [7]: resp = reqests.post(SERVER_URL + "/api/artists/", data=json.dumps(data))
In [8]: resp.headers["Location"]
Out[8]: '/api/artists/mono/'
```
您可以从找到其地址的同一“检查器”选项卡中查看发送到模拟服务器的请求。请注意，它会将您发送到示例的内容进行比较，并会说（对于上述两个请求）它们都不正确（因为它们缺少标头 - headers，而Apiary认为请求中的四个字段都是必填字段）。

![Some example requests sent while compiling this material](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/MusicMetaAPI_client_example.png)

但是，从控制台可以看到，这些请求仍然得到了我们预期的响应，因此它足以进行客户端测试。但是如果您尝试将POST请求发送到具有内容类型验证的真实API服务器您将被拒绝（在服务器尝试使用`request.json`时发生）。所以您需要设置标头，例如下面的PUT示例：
```python
In [9]: resp = requests.post(SERVER_URL + "/api/artists/scandal/",
   ...:     data=json.dumps(data),
   ...:     headers={"Content-type": "application/json"}
   ...: )
```
>#### 练习一： 请求删除
>我们没有向您展示如何发送DELETE请求。您可能已经猜到了，这意味着我们会问你该怎么做。
>
>**学习目标**：如何使用requests编写HTTP请求，尤其是DELETE请求。
>假设我们需要用到的URL的主机部分(host part：指示服务器地址的URL部分。例如，lovelace.oulu.fi就是一个主机部分，此部分确定请求在万维网中的发送位置（即哪个IP地址）。)已经被存储在一个常量中：SERVER_URL，请写一行代码来删除Evoken的专辑 - Hypnagogia。如果您不记得如何请求，请查看>练习2中的MusicMeta apiary文档。
>请记住，代码中艺术家名称全为小写，而专辑名称则为首字母大>写。
>
>**正确答案**：`requests.delete(SERVER_URL + "/api/artists/evoken/albums/Hypnagogia/")`

通常使用超媒体控件发出请求时，客户端应该使用控件元素中包含的方法。执行此操作时，使用请求函数比使用特定的方法更方便。假设我们有一个名为crtl的字典类控件：

`In [10]: resp = requests.request(ctrl["method"], SERVER_URL + ctrl["href"])`

### 使用请求会话
我们假设客户会多次调用API，Requests提供的会话(session)可以通过反复利用TCP连接来帮助提高客户端的性能。它还可以设置持久性标头，这有助于发送Accept headers，以及对一些使用身份验证的API来说，拥有持久性身份验证令牌也会方便很多。会话应当像一个有声明的情景管理器一样被使用，确保会话的开启与关闭。
```python
In [1]: import requests
In [2]: SERVER_URL = "http://private-xxxxx-yourapiname.apiary-mock.com"
In [3]: with requests.Session() as s:
   ...:     s.headers.update({"Accept": "application/vnd.mason+json"})
   ...:     resp = s.get(SERVER_URL + "/api/artists/")
```
通过此设置，在使用会话对象发送时HTTP请求，所有会话标头都会被自动包含。任何在请求方法调用中定义的标头都会添加到会话标头之上（在发生冲突时有优先）。注意：如果要避免模拟服务器响应选择的问题，一种方法是可以使用`"application/vnd.mason+json, */*"`作为Accept header值。

## 基础客户端操作
我们即将看到的客户端代码对API做了一些相对合理的假设。首先，假设中的链接关系与API资源状态图中的一致。此外，它相信API不会发送损坏的超媒体控制或JSON架构。同时，如果POST和PUT请求中更新添加了新的必填字段，它也会报错。

我们不打算在这里显示完整的代码，只显示实际与API交互的部分。此外，虽然客户端需要使用实际的MP3文件进行测试，但您可能更容易通过创建具有必要属性的[数据类](https://docs.python.org/3/library/dataclasses.html)来伪造标记数据，例如（仅在Python 3.7或更新版本中）
```python
from dataclasses import dataclass

@dataclass
class Tag:
    title: str
    album: str
    track: int
    year: str
    disc: int
    disc_total: int
```
在旧版的Python中，您需要创建一个普通的类并自己编写__init__方法（数据类自动实现这种__init__）
```python
class Tag:

    def __init__(self, title, album, track, year, disc=1, disc_total=1):
        self.title = title
        self.album = album
        self.track = track
        self.disc = disc
        self.disc_total = disc_total
        self.year = year
```

**学习目标**：如何使用自动客户端导航API并发送请求。利用超媒体实现动态客户端。

### 客户端工作流程
提交脚本通过以下处理顺序遍历本地集合来工作：
1. 检查第一位艺术家
2. 检查第一位艺术家的第一张专辑
3. 检查第一张专辑中的每个曲目记录
4. 检查第一位艺术家的第二张专辑

依此类推，根据需要来创建新的艺术家，专辑和曲目记录。它还会比较数据并提交差异。相比起API，它更信任本地记录，总是将本地提交做为正确的版本。但是，当它没有某些字段的数据时，它会使用API​​边值。由于MP3文件没有关于艺术家的元数据，因此它使用“TBA”作为位置字段（因为它是必需的）。

### 获取需要的数据
使用超媒体API的关键原则是：
1. 从入口处(entry point)开始
2. 遵循正确的能导向到目标资源的链接关系

这样，只要资源状态图保持不变，即使API每天都任意更改它的URIs，您的客户端也不会出错。我们的提交脚本需要从艺术家集合资源开始。但是，我们不通过对`/api/artists/`使用GET方法来启动脚本，而是应该开始从入口点`/api/`出发，通过查看“mumeta：artists-all”控件中的“href”属性来找到它正在查找的集合的正确URI。

考虑到这一点，下面的例子就是客户端应该如何正确地开始与API的交互：
```python
with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json"})
        resp = s.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            artists_href = body["@controls"]["mumeta:artists-all"]["href"]
```

入口点只会在这个时候被访问一次。从现在开始，我们将使用资源表达中的链接关系在API中进行航行（从艺术家集合资源开始）。随着艺术家集合的资源，我们可以逐一检查本地收藏的艺术家。
```python
def check_artist(s, name, artists_href):
    resp = s.get(API_URL + artists_href)
    body = resp.json()
    artist_href = find_artist_href(name, body["items"])
    if artist_href is None:
        artist_href = create_artist(s, name, body["@controls"]["mumeta:add-artist"])

    resp = s.get(API_URL + artist_href)
    body = resp.json()
    albums_href = body["@controls"]["mumeta:albums-by"]["href"]
```

在遍历单个艺术家前，我们已经选择重新获取艺术家集合，因为在我们处理前一位艺术家时，我们正要检查的艺术家可能会被另一位客户添加。顺序是首先要通过“items”属性，查看我们要获取的艺术家是否存在于列表中。同时记住有艺术家姓名的非唯一性问题，我们的脚本可以返回来询问人类用户，根据用户选择来决定是否需要找多名重名艺术家。同时，我们推荐以小写的方式读写艺术家名字并进行比较，这样可避免大写不一致。
```python
def find_artist_href(name, collection):
    name = name.lower()
    hits = []
    for item in collection:
        if item["name"].lower() == name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]["@controls"]["self"]["href"]
    elif len(hits) >= 2:
        return prompt_artist_choice(hits)
    else:
        return None
```

假设我们找到了一个艺术家资源，我们现在可以使用该个体资源的“self”链接关系来进入单个艺术家资源。根据资源状态图，这个中间步骤一般用于找到该艺术家的“mumeta：albums-by”控件。该控件是为了检查一名艺术家的所有专辑资源。在此，我们已经跳过了异常处理，因为我们相信API会遵守自己的文档（同时也是为了简洁起见）。

>#### 练习二：迷宫中的老鼠
>超媒体也可以用于制作一个会使用链接关系来导航的东西，比如一个迷宫。用自动化客户端来解决这个问题是一个很好的练习，所以我们决定将一些奶酪藏在一个相当大的迷宫里......
>
>**学习目标**：制作一个超媒体客户端，它能通过链接关系来将一系列GET请求连接在一起，从而找到它需要的东西。
>
>**如何开始**:
>
>我们有一个API服务器运行在`https://pwpcourse.eu.pythonanywhere.com`。它的媒体类型是Mason。该API服务器中只有一个资源，并且只支持GET方法，当然它有一个入口点`/api/`。该资源是一个房间，它有两个属性：
>* `"handle"`：字符串, 每个房间的唯一标识符
>* `"content"`：字符串，可能的值：`""`和`"cheese"`
>
>此外，它最多可以有四个方向控制，代表从一个房间到另一个房间的过渡。角落的房间只有两个方向可以走，边沿的房间只有三个方向可以走。这些控件都有自己所属的命名空间。
>* `"maze:north"`：朝北面走
>* `"maze:south"`：朝南面走
>* `"maze:east"`：朝东面走
>* `"maze:west"`：朝西面走
>
>此外，入口点还有一个带有maze命名空间的控件：`"maze:entrance"`-它通向第一个房间。
>
>你的任务是寻找奶酪。练习中的“迷宫”只是一个方形网格，但它有很多房间。除非您想手动点击数千个链接，否则我们建议使用自动机器客户端来找到奶酪。当你找到奶酪时，记得打印出房间的‘handle’ - 这就是本练习的答案。
>
>您的客户需要一些最小的智能，以便它能以某种逻辑顺序（例如，每次一行）地通过房间。请确保您的客户端不会陷入无限循环中。实际上您的客户端正在发送真是的网络流量 - 所以警惕不要造成泛滥。
>
>**正确答案**：`h0pQeMSALy92DCYgceFX`

### POST的架构模式
当我们想创建某些不存在的资源时，显然需要通过提交脚本来将其发送给API。现在我们来看如何创建一些专辑和曲目。这两个数据都来自MP3标签（对于专辑，我们将第一首曲目的标签作为来源）。这两者的POST请求体都可以根据超媒体控件中JSON模式来以一种类似的方式组成。其基本思想是遍历架构中的每个属性，并且对每个属性做如下操作：
1. 找到相应的本地值（即MP3标签字段）
2. 使用属性的“type”和相关字段（如字符串的“pattern”和“format”）将值转换为正确的格式
3. 使用属性名称将值添加到正文中

如果未找到相应的值，客户端可以检查是否需要该属性。如果不需要，可以安全地跳过它。否则，客户端需要弄清楚（或询问人类用户）如何确定正确的值，在这个例子中，我们不讨论或实现这个部分。这仅当需要API向其资源添加新属性时才有意义。

在这里我们提供一个关于POST架构模式的例子，下面是关于专辑集合资源的“mumeta：add-album”控件：
```python
"mumeta:add-album": {
    "href": "/api/artists/scandal/albums/",
    "title": "Add a new album for this artist",
    "encoding": "json",
    "method": "POST",
    "schema": {
        "type": "object",
        "properties": {
            "title": {
                "description": "Album title",
                "type": "string"
            },
            "release": {
                "description": "Release date",
                "type": "string",
                "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
            },
            "genre": {
                "description": "Album's genre(s)",
                "type": "string"
            },
            "discs": {
                "description": "Number of discs",
                "type": "integer",
                "default": 1
            }
        },
        "required": ["title", "release"]
    }
}
```
事实上，我们只需要构建一个函数来同时完成对专辑和曲目的POST请求：
```python
def create_with_mapping(s, tag, ctrl, mapping):
    body = {}
    schema = ctrl["schema"]
    for name, props in schema["properties"].items():
        local_name = mapping[name]
        value = getattr(tag, local_name)
        if value is not None:
            value = convert_value(value, props)
            body[name] = value

    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)
```
在此函数中，tag是一个对象。实际上它是一个`tinytag.TinyTag`类的实例，但它也可以是我们之前展示的`Tag`类的实例。`ctrl`参数是从中资源控件中选取的一个字典（例如“mumeta：add-album”）。`mapping`参数也是一个字典，其中这个字典的‘键’是API中所提及的属性名称，‘值’则是相应的MP3标记字段。关于资源之间如何互通，您都可以通过阅读API文档来了解。为了功能的正常实现，我们还使用了`getattr`函数，这个函数说明了如何通过使用Python中的字符串来访问对象的属性（而不是像通常那样被访问，例如：`tag.album`）。

专辑资源的的映射字典如下所示，其中‘keys’是API中属性名称，‘values’是标记对象中使用的名称。
```python
API_TAG_ALBUM_MAPPING = {
    "title": "album",
    "discs": "disc_total",
    "genre": "genre",
    "release": "year",
}  
```
由于请求中的所有值都不一定是以相同类型或格式而存储的，因此我们需要用`convert_value`函数（如下所示）来负责转换：
```python
def convert_value(value, schema_props):
    if schema_props["type"] == "integer":
        value = int(value)
    elif schema_props["type"] == "string":
        if schema_props.get("format") == "date":
            value = make_iso_format_date(value)
        elif schema_props.get("format") == "time":
            value = make_iso_format_time(value)
    return value
```
最后，请注意我们如何将`submit_data`变为函数，这个函数的优点在于它适用于客户端中的所有POST和PUT请求，例子如下：
```python
def submit_data(s, ctrl, data):
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp
```
总体而言，这种解决方案非常灵活与动态，客户端几乎可以用过从API获得的信息来做出所有决策与操作。我们唯一需要硬编码的是将资源属性名称映射到MP3标记字段名称。关于如何构造请求的其他所有内容都将来自超媒体控件：要发送什么值; 以什么类型/格式发送; 发送请求的位置以及要使用的HTTP方法。这段代码不仅能够抵抗API的变化，而且重用率会非常高。

当然，如果控件中属性是“schemaUrl”而不是“schema”，则需要从提供的URL获取schema这一附加步骤，但是这种添加操作也非常简单。

### 是否使用PUT
在使用上面例子中的动态的代码时，使用PUT方法来编辑资源与使用POST来创建新资源的操作非常相似。对于‘编辑’这个操作来说，实际上一个很重要的一个部分是需要弄清楚它是否是需要的。同样的，在“编辑”操作中，核心也是“schema”。使用架构表达而不是资源表示中属性的一个原因是，属性中可能包含不应在PUT请求中提交的派生属性（例如，专辑资源中确实具有“artist”属性，但是该值是不能更改）。

为了确定是否应该发送PUT请求，客户端需要将其本地数据与从API获得的关于专辑和曲目记录的数据进行比较。为了使比较有意义，我们需要再次弄清楚相应的本地值是什么，并将它们转换为相应的类型或格式。这个过程与我们在`create_with_mapping`上面的函数中所做的非常类似，实际上它的大部分代码都可以放入一个名为`compare_with_mapping`的新函数中：
```python
def compare_with_mapping(s, tag, body, schema, mapping):
    edit = {}
    change = False
    for field, props in schema["properties"].items():
        api_value = body[field]
        local_name = mapping[field]
        tag_value = getattr(tag, local_name)
        if tag_value is not None:
            tag_value = convert_value(tag_value, props)
            if tag_value != api_value:
                change = True
                edit[field] = tag_value
                continue
        edit[field] = api_value

    if change:
        try:
            ctrl = body["@controls"]["edit"]
        except KeyError:
            resp = s.get(API_URL + body["@controls"]["self"]["href"])
            body = resp.json()
            ctrl = body["@controls"]["edit"]
        submit_data(s, ctrl, edit)
```
总的来说，这个过程非常相似。但是还有一个额外的步骤，即检查是否需要更新字段，并在第一次发现差异时将‘更改标记’标记为True。另请注意，在比较的过程中，对于专辑，我们是在对单个专辑资源进行此比较，但对于曲目记录来说，我们实际上是在对专辑资源中“items”列表中的track数据进行比较。这样的话，除非是需要更新单个数据，否则我们不需要去获取每个单独的曲目的数据。当需要编辑的时候，我们实际上需要先用GET来获取曲目记录数据，然后再从该资源出发，找到编辑的控件。这解释了为什么我们没有直接给PUT方法传递一个控件，以及为什么当编辑控件没有直接附加到我们正在比较的对象上时，我们在最后找到控件时有额外的步骤。

有趣的事实：如果之后API开发人员选择将“编辑”控件添加到专辑资源中的每个单个曲目记录资源中，则此代码会发现这一点，所以不再需要有额外的步骤。有时客户端可以通过逻辑来查找不能立即获得的控件。有时候，遵循一个集合资源中单个“item”的自链接关系，就可以很好地猜测到在哪里可以找到与该个体相关的其他控件。

关于PUT的最后提醒：记住它必须发送完整的表达，而不仅仅是那些要发送改变的字段。API要使用请求主体中的数据来完全替换之前的资源,这就是为什么当我们没有某个字段的新值时，我们总是将API边值添加到字段。

>#### 练习三：Schemanator - 终端版
>一般的超媒体客户端建立在这样的思想之上：通过使用超媒体控件提供的信息生成用户界面，可以实现与API的完全交互。其中一部分信息来自于API提供的模板或类似的架构与表单中包含的来自用户POST和PUT请求的值。在此任务中，您将执行通用数据函数的简单命令行版本。
>
>**学习目标**：如何根据JSON架构来完成数据提示和转换数据，从架构URL获取架构，提交POST / PUT请求。
>
>**在你开始之前：**
>你可以使用提交脚本示例中原样的`submit_data`函数。唯一的区别是任务中的检查器将提供完整的URLs作为控件中的“href”属性值。因此，你应该在提交答案之前删除API_URL常量或将其设置为`""`。
>
>同时您应该下载并[运行](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/exercixe3.md)最新版本的Sensorhub API，这将有助于您进行测试。
>
>[sensorhub.py](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/sensorhub.py)
>
>**实施功能：**`prompt_from_schema`
>* 参数：
>1. 请求会话对象 - 您必须通过此对象来发出任何请求
>2. 将Mason超媒体控件作为字典
>
>该函数应以下面两种方式中的其中一种来获取架构：
>1. 如果控件中具有“schema”属性，请直接使用该架构
>2. 否则将GET请求发送到“schemaUrl”属性中指定的URL，并从响应中读取架构 `.json()`
>
>一旦它有一个架构，它应该要求用户输入所有必需的值（使用description作为输入提示），并将它们转换为架构中指定的正确类型。本练习中使用到的类型是“number”，“integer”和“string”。一旦函数编译了请求的数据，它就应该通过超媒体控件的属性被发送到API服务器。你可以使用此`submit_data`功能。
>
>你不需要对用户的输入进行类型检查 - 检查器只会为你提供有效的输入。但是你需要提示让它们按照在“required”列表中的顺序出现，你可以使用内置输入功能来完成这些提示。
>
>**测试你的程序**
>
>您可以针对使用Mason作为其媒体类型的任何API测试此程序，你只需要检查API是使用了完整的URL还是省略了“host”部分。我们所有的例子都省略了“host”部分，这意味着你需要用API​​_URL常量作为“host”部分。但是请记住在提交答案之前将其更改为空字符串。最好的方法是在开头将其设置为空字符串，并在你自己的模块中将其值更改为主程序部分中的测试目标（如下所示）。
>
>下面的例子是一个主程序，你可以使用它来测试Sensorhub API，以创建传感器。
>```py
>if __name__ == "__main__":
>    API_URL = "http://localhost:5000"
>    with requests.Session() as s:
>        resp = s.get(API_URL + "/api/sensors/")
>        body = resp.json()
>        prompt_from_schema(s, body["@controls"]["senhub:add-sensor"])
>```
>**正确答案**：[answer_ex4_t3](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/answer_ex4_t3.py)

### 结束语和完整示例
虽然这是一个具体的例子，但它应该让你很好地了解在访问一个超媒体API时如何进行客户端开发：将假设最小化，并尽量让API资源表达来指导你的客户。当您需要进行硬编码时，请始终将逻辑基于来自文档中的信息。始终避免过于依赖API来工作​​ - 这种解决方法通常依赖于API未正式支持的功能，并且可能在API更新时随时停止工作。让客户端根据API调整自己也是一种尊重API开发人员的方式，当没有客户端要依赖古老/非预期的功能时，维护API的工作会得更加容易。

下面提供一个完整的例子。如果你想在没有修改的情况下运行它，你需要本地中存有MP3文件，并且其标签数据与你的Apiary文档的例子相符。提交脚本目前不支持VA专辑。

[mumeta_submit.py](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/mumeta_submit.py)

## 使用Javascript的API客户端
在本节中，我们将讨论如何使用Javascript和jQuery创建浏览器客户端。这种客户端的典型示例是一个与API交互的图形用户界面。在此我们只对代码的完成做出一些细节上的点评，如果你需要学习Javascript基础知识，可以参考其他[来源](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/pwp-course-material/#javascript)。如果你已经了解Python，那么Javascript就是一门比较容易学会的语言。浏览器端脚本的主要组件之一是DOM操作。因为jQuery能做的[DOM](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#dom)操作比JavaScript本身能做的更好，因此，尽管技术上来说jQuery只是一个外部库，但其实它是一个非常重要的组成部分。实际上，本材料中的示例几乎完全是使用jQuery编写的。

因为在本课程中，我们不要求你对Javascript像对Python那样熟悉，所以我们不会立即开始制作尽可能动态的代码。相反，我们将在不充分利用超媒体优点的情况下展示一些基本操作。

**学习目标**：了解面向人类用户的基于浏览器的API客户端的基础知识。使用jQuery制造[Ajax](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#ajax)请求，使用jQuery操作DOM。

### 关于Javascript样式
在我们的示例中，我们遵循此[样式指南](https://www.crockford.com/code.html)并期望您也这样做。我们也鼓励使用[JSLint](https://www.jslint.com/)。Javascript可以是一种非常狡猾的调试语言 —— 最好不要因为代码的质量差而让其变得更加困难。当对jQuery脚本使用JSLint时，记得要在底部的全局变量盒子中加`$`和`document`，这样能避免了一大堆`"undeclared '$'"`的错误。
![Globals look like thiss](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/jslint_options.png)

我们还建议你在严格模式下运行Javascript。这会引发出更多错误，但这使后期的整体调试和维护更容易。您可以在文件开头通过以下几行来条用严格模式运行脚本：
```python
"use strict"; 
```

### 服务器端准备
对于此示例，我们将用与API本身相同的服务器应用程序为客户端提供服务。它实际上只是一个提供静态HTML页面和几个脚本文件（jQuery和我们的代码）的视图。站在API角度来看，从同一台服务器上提供服务也可以满足[跨域资源共享（CORS）](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#cors)的需求定义。为了遵循此示例，请[下载jQuery](https://jquery.com/download/)并在项目的静态文件夹创建以下结构：
```python
静态
├──CSS 
├──HTML 
├──profiles
└──scripts
```
将`jquery.js`放到到脚本文件夹中，将所有的`HTML文件`都放到html文件夹中。关于HTML文件，其实并没有什么特别令人惊奇的，它只是定义了几个div元素，div用来放置从API端接收[资源](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#resources)表达。您还可以使用此简短的CSS文件来避免加载页面时的404报告。也可以命名您自己的脚本文件`admin.js`或适当更改HTML文件中的引用。

[admin.html](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/admin.html)

[admin.css](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/admin.css)

然后将下面这几行代码放入单个文件应用程序中的资源[路由](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#routing)后，如果你遵循更精细的项目结构指南，你可以将其放进`__init__.py`中的函数`create_app`内部。
```python
@app.route("/admin/")
def admin_site():
    return app.send_static_file("html/admin.html")
```
保存并启动服务器后，您应该能够访问本地的`/admin/`，并查看HTML文件的呈现内容（此时的内容并不多）。

这里是最新版本的Sensorhub API单文件版本：
[sensorhub.py](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/sensorhub_1.py)

### 调用Ajax
Ajax在历史上代表Asynchronous Javascript And Xml，拼写为AJAX。但是从XML被大量弃用那时起，Ajax就不再是首字母缩略词这么简单，而主要被用作于术语。然而，它的异步性质仍然存在。由于这种性质，Ajax是非阻塞的：在使用Ajax发送请求之后，客户端脚本将继续运行。如果没有这个性质，浏览使用了Ajax的网页就会受到持续冻结的困扰（由于现在的网页做了过多的Ajax调用，这种困扰将是有持续性的）。从编程的角度来看，它还意味着您的脚本在发出Ajax请求后无法获取及时的响应。

在上面的Python客户端中，API的调用总是会阻塞 - 这实际上是因为脚本在暂停等待响应，而当有一个响应时，它会被存储到resp变量中。在使用非阻塞调用时，由于在调用时响应尚未就绪，所以此时响应无法直接被存储到变量中。所以，代码必须注册一个[回调函数](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#callback)，这样它会在响应准备就绪时处理它。在大多数情况下，至少有一个回调函数会被注册用来处理错误。所有回调函数都需要以某种方式进行注册。通过jQuery，所有的回调函数都会被收集到一个给ajax函数的对象中。在实践中，需要获得如下入口点：
```python
$.ajax({
    url: "/api/",
    success: function (body, status, jqxhr) {
        console.log("RESPONSE (" + status + ")");
        console.log(body);
    },
    error: function (jqxhr, type, error) {
        console.log("ERROR (" + type + ") - " + error);
    }
});
```
`$`是一个用于所有jQuery函数的前缀（它也可以自行调用，但现在不用担心这个）。该`$.ajax`函数将设置对象作为其参数。[这里](https://api.jquery.com/jquery.ajax/#jQuery-ajax-settings)是一个所有在此设置对象中的可以包含的属性值列表。在这里我们不打算全部使用它们。在示例中，我们将回调定义为[匿名函数](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#anonymous-functions)。分配一个现有函数给回调函数是完全合法的。
```python
$.ajax({
    url: "/api/",
    success: handleEntry,
    error: handleError
});
```
另一件完全合法的事情是，如果您不需要功能参数，可以直接省略，只要将您不需要的功能参数放在最后。例如，我们可以省略jqxhr（jQuery XmlHttpRequest对象），因为它没有被使用（当你想访问标题时你才需要它）。同样合法的是在`$.ajax`中将url作为第一个参数，将其余设置作为第二个参数（函数重载的乐趣）。

无论它们是如何定义的，一旦服务器响应了我们的Ajax调用，其中一个函数就会被调用。如果成功，第一个参数将获得[响应主体](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#response-body
)作为已编译的Javascript对象。之后通常会发生的是[DOM](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#dom)操作，将来自响应的数据存入DOM以供用户查看。

还有另一种方法可以通过使用一个称为Promise的对象来注册回调。以下代码具有相同的功能：
```python
$.ajax("/api/")
    .done(function (body, status, jqxhr) {
        console.log("RESPONSE (" + status + ")");
        console.log(body);
    })
    .fail(function (jqxhr, type, error) {
        console.log("ERROR (" + type + ") - " + error);
    });
```
在本练习中，我们建议您使用第一种方法，即在设置对象中传递回调。下面所有示例也将使用这个方法。Promise对象是一个更新的技术，并引入了旧方法无法实现的新选项，例如它能够向同一事件添加多个回调。

### 基本的DOM操作
尽管jQuery使Ajax调用更简洁，但jQuery的主要目的是使DOM操作更加简洁清晰。文档对象模型是一个编程接口，它允许Javascript即时（即无需重新加载页面）修改文档（即网页）的内容。它将HTML呈现为树状结构，其中元素可以直接通过它们自己的属性（例如，类或id）或通过诸如父，子，下一个和上一个的关系来定位。在设置样式时，一下基本的jQuery选择使用与CSS语法相同：
```python
$("table")                      // selects all table elements
$(".resulttable")               // selects any elements where class="resulttable"
$("#sensorlist")                // selects the element where id="sensorlist"
$(".resulttable tbody tr")      // selects all rows from all tables where class="resulttable"
```
如您所见，jQuery本身可以被调用。这将返回一个查询对象，该对象中具有可用于对所有选定元素立即执行操作的方法。通常，在尝试选择一个特定元素时最好使用id，而在选择一组相关元素时最好使用class。如上例所示，元素类型会经常被使用，即在另一选择中选择一种类型的所有元素。这里有[很多选择器](https://api.jquery.com/category/selectors/)可供选择，但是建议您可以从最基本的开始。

通常，测试选择和操作的最佳方法是使用浏览器的Javascript控制台。在Chrome中，你可以用`Ctrl`+ `Shift`+ `j`打开，在Firefox中可通过 `Ctrl`+ `Shift`+ `k`打开（使用`j`也可以进入控制台，但是是在一个单独的窗口）。从现在开始，为了测试命令，您可以使用API​​服务器中的`"/admin/"`URL中提供的HTML页面。

选择之后，就[可以](https://api.jquery.com/category/manipulation/)进行操作了。一种基本的操纵方法是`html`，它可用于将所选元素内的HTML设置为争论中的内容（请注意：如果未提供参数，则此方法将返回元素内的HTML而不是对其进行设置）。这是在用户界面中设置错误消息区域（带有错误类的[HTML div](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div)元素）内容的一种方法：
```python
$("div.notification").html("<p class='error'>Guru meditation error</p>");
```
另一个简单的常见操作是清除一个元素内的所有内容，例如，当我们收到要显示的另一组数据时可以选择清除整张表。这是通过`empty`完成的。在处理表时，我们通常会选择`<tbody>`元素，除非您想更改表的标题。在这里，我们只清除数据行。
```python
$(".resulttable tbody").empty();
```
关于表，我们要做的最后一个非常常见的事情是将元素追加到另一个元素内-通常是表，表单或列表中（即`<ol>`或`<ul>`）。这是通过该`append`方法完成的。
```python
$(".resulttable tbody").append("<tr><td>placeholder-sensor</td><td>placeholder-model</td></tr>");
```
还有一些非常常见的操作例如通过`attr`改变元素的属性，或者用过`css`改变其外观，但我们在本材料中不再做过多的示例。这些与用户界面中的隐藏/显示和激活/停用元素有关，并且显然还有更多的操作。

### 渲染数据集合
我们已经知道了如何进行Ajax调用以及如何将数据插入HTML页面，现在，我们可以研究一些基本的客户端操作。首先是将收集的资源项目存放在表中来显示。首先，我们先来做的将数据填充到表中。

为此，我们需要对`"/api/sensors/"`调用一个Ajax，并将结果填写至成功结果的回调函数中的[HTML表格](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table)内。下例展示了一个使用命名函数作为处理器的情况。由于执行Ajax请求本身总是相同的，所以最好通过函数将获取的结果作为参数传递并呈现到HTML页面：
```python
function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function getResource(href, renderFunction) {
    $.ajax({
        url: href,
        success: renderFunction,
        error: renderError
    });
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/sensors/", renderSensors);
});
```
对于此客户端的第一次迭代，我们可以利用一个资源去确定数据渲染的函数。这意味着我们是在知道表头是什么及有哪些列数据的情况下对该函数进行编码的。在这种情况下，将整行的HTML值构造为字符串并将其填充到表的相关部分中是最简单的，标题使用`html`，利用`append`添加数据。通过这些决定，实现起来就非常简单，主要是以下这两个功能：
```python
function sensorRow(item) {
    return "<tr><td>" + item.name +
            "</td><td>" + item.model +
            "</td><td>" + item.location + "</td></tr>";
}

function renderSensors(body) {
    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Model</th><th>Location</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    body.items.forEach(function (item) {
        tbody.append(sensorRow(item));
    });
}
```

### 解析表单
在客户端显示数据是一回事-能够提交数据又是另一回事。提交数据一般是通过[HTML表单](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form)来调用Javascript函数来完成，而不是通过POST直接提交到服务器。在第一个迭代中，我们将再次提供指向特定资源的函数，这意味着表单字段是硬编码的。同时，我们使用图式标记哪些字段是必填字段，并检索字段说明。
```python
function renderSensorForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    let model = ctrl.schema.properties.model;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitSensor);
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    form.append("<label>" + model.description + "</label>");
    form.append("<input type='text' name='model'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}
```
在这里，我们用`attr`来设置表单的各种属性以及申明需要强制输入字段的必需属性。我们将通过`submit`来设置一个在提交表单时（即，当用户按下Submit按钮时）将要调用的函数。我们还将通过特定语法来通过调用属性（"element[attribute='value']"）去选择元素。剩下需要实现的就是将数据真实准确地发送到服务器的功能。首先让我们来看下面这个示例：
```python
function submitSensor(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    data.model = $("input[name='model']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedSensor);
}
```
上面的示例中，第一行是最重要的。通过调用`event.preventDefault`，使浏览器跳过此事件中通常会被执行的默认行为。在这种情况下，表单的内容将作为表单编码数据被发送到表单元素中`action`属性指定的地址。我们的API不采用形式编码的请求，因此这将导致415错误，将第一行代码放在所有函数中用来替换默认行为变得十分重要。另一个示例是[anchor元素](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a)，通常在单击该锚元素时，会有相关联的URL跟随。在本示例中，这种超链接元素也是我们不想要的东西，因为整个客户端都是基于一个我们不会离开页面的想法而建立的。如今，sendData函数已被通用化，可用于所有具有请求正文的请求：
```python
function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: "application/json",
        processData: false,
        success: postProcessor,
        error: renderError
    });
}
```
在这里，我们使用回调参数启用POST处理。在POST请求的情况下，成功的POST处理将会把传感器的数据附加到传感器表中。我们有以下选项可以做：
1. 使用本地数据：从表单中读取值并将其放入表格中
2. 重新获取传感器集合
3. 使用`location header`获取新传感器并将数据插入表中
当然这些选项或多或少都有一点问题需要解决。如果资源具有由API服务器自己生成的属性，并且本地数据中没有控件管理时，不建议直接使用本地数据。重新获取整个传感器集合可以避免数据不一致的情况，但这是一项非常繁琐的操作。最后一个选项也可能会出现问题，尤其是如果传感器附带了在这张视图中我们不需要一堆数据时。当然最后一个选项在这种情况下仍然是最好的，因此我们会迅速链接到一个Ajax调用：之前申明过的通用型`getResource`，再加上之前提到的在GET请求之后将传感器数据添加到表中的函数。
```python
function appendSensorRow(body) {
    $(".resulttable tbody").append(sensorRow(body));
}

function getSubmittedSensor(data, status, jqxhr) {
    let href = jqxhr.getResponseHeader("Location");
    getResource(href, appendSensorRow);
}
```
在这里，我们还看到了一个相当神秘的关于jqxhr对象的用法-用来获取Location header.

### 显示各个传感器
最后，我们需要导航链接才能在轻松的获取自己想要的资源。在此示例中，我们主要操作集中在传感器集合和各个传感器之间。首先要做的是通过每个传感器中的“self”链接关系来丰富其在表中的内容，使我们能够获取有关每个传感器的细节。这需要我们更改`sensorRow`功能：
```python
function sensorRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderSensor)'>show</a>";

    return "<tr><td>" + item.name +
            "</td><td>" + item.model +
            "</td><td>" + item.location +
            "</td><td>" + link + "</td></tr>";
}
```
关于锚标记<a>的定义看起来有些混乱，但我们应该清楚的是，我们从控件中获取了URL，我们还将通过标记`onClick`连接到一个将其正常行为覆盖的函数。这与之前的方法的区别：当我们使用jQuery中的方法（例如submit）设置事件处理程序时，我们仅需要写入函数的名称；但是当使用HTML属性时，整个调用函数都会被编写。当然这个函数也很简单：
```python
function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}
```
再次说明，最重要的一步是阻止默认行为。之后，我们将以自己的方式处理：通过获取传感器的资源，并使用新的渲染功能将其插入到DOM。当需要显示可编辑的资源时，将数据放入表单中展示将是一种比较好的方法。这种编辑方式非常简单。对于一些不允许以编辑方式提交修改的属性，我们可以将其放入只读字段中。由于我们已经有一个可以为创建传感器的渲染类似表单的功能，我们可以重用它，然后将更改应用于表单：
```python
function renderSensor(body) {
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderSensorForm(body["@controls"].edit);
    $("input[name='name']").val(body.name);
    $("input[name='model']").val(body.model);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
}
```
现在，我们使用`before`方法来将Location字段（该字段不在图式）作为只读字段在提交按钮之前就插入表单中。因为提交是以一种动态的方式进行的，所以我们实际上已经可以编辑传感器。但是，在处理结果时会出现错误，因为后处理功能会在提交后尝试遵循Location标头。但是由于这是一个编辑操作，所以Location不存在。我们可以采用一种更复杂的方式来处理此问题，但是现在，我们只向函数添加一个简单的if语句：
```python
function getSubmittedSensor(data, status, jqxhr) {
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendSensorRow);
    }
}
```
实际上，我们应该考虑再次获取资源或返回传感器集合。为什么？因为更改传感器的名称就会更改其URI。但我们不必太着重于此，我们只需要在导航div上添加一个导航控件即可完成本示例：“collection”链接关系。这意味着可以通过将以下代码片段放入`renderSensor`中来添加另一个看起来有点混乱的锚标记：
```python
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderSensors)'>collection</a>"
    );
```
然后再将以下这行放入`renderSensor`中，用来清除导航div：
```python
    $("div.navigation").empty();
```

### 完整示例
您可以从下面下载完整的示例：[admin.js](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/admin.js)

>#### 练习四：分页器 - 测量日
>分页通常用于大型数据集，而您无疑已经在网络上看到了很多类似的东西。这意味着数据将以一定大小的量被读取，同时会显示一些控件：“next”（“>”）和“prev”（“<”）（有时也包括“first”（“<<”）和“last”（“>>”））。这也与APIs一起结合起来使用。在本练习中，您将实现对测量数据的分页。
>
>**学习目标**：使用分页控件从API中提取数据。显示带有分页数据以及相关DOM操纵。
>
>**在你开始之前**：我们已经对Sensorhub API服务器进行了最终更新。此更新包含API方面对分页操作的支持，其中分页单位为50。您可以在下面进行下载。
>[app.py](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/app.py)
>请记住，您需要创建一个数据库并填充数据。我们在SensorHub API中包含了一些操作命令以简化此任务。[Flask API项目布局教程](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/flask-api-project-layout/#using-the-command-line-interface)中对它们进行了说明。如果您只想启动它并运行，请执行以下命令：
>```python
>flask init-db
>flask testgen
>flask run
>```
>除此之外，您应该接着从`admin.js`开始。获取在端口5000上运行的API，并将浏览器指向`"http://localhost:5000/admin/"`。在开发过程中，您可能需要进行多次重载。**重要提示**：在浏览器中进行测试时，必须强制重新加载页面-正常重新加载将使CSS和JS文件保持缓存状态，更改并不会生效。你可以使用`Shift`+`F5`进行强制重载。
>
>在您下载所得的代码中，请勿随意改动任何未得到指示的代码部分。
> 
>**函数修改**：`renderSensor`
>您需要在导航div元素中添加其他导航控件元件，并应该将其添加到末尾（即作为第二个元素）。像之前的其他链接一样，单击该链接时，`followLink`也会被调用，其中的最后一个参数是`renderMeasurements`函数。同时，可以从“senhub：measurements-first”控件中找到此链接的href属性。
>
>**新函数**：`renderMeasurements`
>当Ajax被调用并返回时，此函数应具有测量集合资源。该集合包含从[查询参数](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_4_ImplementingHypermediaClients/appendix/explain.md#请求参数)定义中起始索引开始的50个测量。每个测量资源都有两个属性：
>* 时间：完整的ISO时间戳记（字符串）
>* 值：测量值（浮点数）
>
>此外，该集合资源还具有以下控件：
>* `"up"`：返回到传感器资源（与该任务无关）
>* `"prev"`：向前检索50个测量值，第一个测量值出现时，则不再显示
>* `"next"`：向后检索50个测量值，最后一个测量值出现时，则不再显示
>
>这是在您函数中必须执行的操作列表：
>* 如果资源表示中存在tablecontrols div中的内容，则将其替换为“prev”和“next”链接
>    1. 检查HTML，确保其与导航div不同
>    2. 需要同时在tablecontrol div元素中top和bottom中显示
>    3. “prev”应始终位于左侧
>* 将表的标题设置为与测量属性名称相对应（时间放在左侧）
>* 在表格中显示50个测量值
>
>最后，您的用户界面应该具有三个不同的屏幕：一个显示传感器列表，一个显示有关特定传感器的信息，另一个显示传感器的测量值。下图为示例：
[理想示例：]()

