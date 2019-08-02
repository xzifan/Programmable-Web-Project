# 学习目标
在本练习中，你将学习如何通过Python或通过在网站中嵌入客户端来实现一个RESTful风格客户端。

# 实现超媒体客户端
在这个最后的练习中，我们将探讨关于API的另一个难题：客户端。在之前的练习中，我们一直在讨论超媒体的优势以及给客户端开发人员带来的帮助。现在是时候展示如何实现这些神话般的客户端了。本练习材料提供两个示例：一个全自动机器客户端（Python脚本）和一个为人类用户生成用户界面的浏览器客户端（带有jQuery的Javascript）。我们将向您展示如何使客户端拥有抗API变化的强大功能。

我们在本练习中使用了MusicMeta API。原因之一是我们对这个API的超媒体表达形式更为熟悉。同时在练习2中，我们已经设想了一些客户，所以我们不需要从头开始创建一个新的想法。

## 使用Python的API客户端
我们第一个客户端将通过提交脚本来管理其本地MP3文件，并可以将其元数据与存储在API中的元数据进行比较。如果API中没有包含这个本地文件中的数据，该数据会被自动添加。如果其中存在冲突，它会通知用户并询问他们的意见 - 毕竟这不是一门人工智能课程。

**学习目标**：使用Python的请求库来制定HTTP请求。HTTP请求是客户端使用HTTP协议向服务器发出的全部请求。它包括请求URL，请求方法（GET，POST等），标头和请求正文。在Python Web框架中，HTTP请求通常被转换为请求对象。[HTTP请求规范](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html)

### 准备
这个练习中我们需要用到Python中的另一个模块，我们将通过[Requests](https://2.python-requests.org//en/master/)来调用API. 像往常一样在虚拟环境中安装好该模块：
```python
pip install requests
```
为了提高趣味性并展示更多的API开发工具，我们在此不提供服务器代码; 相反，我们要求您使用[Apiary](https://apiary.io/)中的模拟服务器来测试客户端。为此，我们将为您提供您在[练习2结束时](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/README.md#练习四api-blueprint---artist)完成的API Blueprint的更新版本 - 添加了记录tracks group资源的文档，您可以将其粘贴到现有文档中。该版本还修复了在模拟服务器测试客户端过程中发现的一些错误，因此请务必同时更新您文档中的相册资源部分(album)。同时，我们还将入口点(entry point)添加成为了一项资源，以便被客户端获取。

为了能正常工作，**您需要将您在[练习2最后一个任务](https://github.com/XCifer/Programmable-Web-Project/blob/master/Exercise_2_APIDesign/README.md#练习四api-blueprint---artist)中完成的Artist资源与下面我们提供的文档结合起来**. (请确保您在练习2中最后一个任务中完成的文档是正确的)

[musicmeta.md]()

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

[Some example requests sent while compiling this material]()

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
>**正确答案**：`requests.delete(SERVER_URL + "/api/>artists/evoken/albums/Hypnagogia/")`

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
我们即将看到的客户端代码对API做了一些相对合理的假设。首先，假设中的链接关系与API资源状态图中的一致。此外，它相信API不会发送损坏的超媒体控制或JSON模式。同时，如果POST和PUT请求中更新添加了新的必填字段，它也会报错。

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