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

# 简单的flask应用

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

<a href="Programmable-Web-Project\Exercise 1. Introduction to Web Development/app.py" target="_blank">app.py</a>  

```python
from flask import Flask
app = Flask("hello")

@app.route("/")
def index():
    return "You expected this to say hello, but it says \"donkey swings\" instead. Who would have guessed?"
```
