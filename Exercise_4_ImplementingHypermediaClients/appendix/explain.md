# DOM
文档对象模型（DOM）是Javascript代码可以通过其与HTML文档交互的接口。它是遵循HTML层次结构的树结构，每个HTML标记都有自己的节点。通过DOM操作，Javascript代码可以将新HTML插入任何地方，修改其内容或将其删除。对DOM的任何修改都会实时更新到网页中。请注意，由于这是一个渲染操作，因此很可能是您的代码可以执行的最耗费资源的操作之一。因此，一次更改元素的整个内容比改变它（例如一次一行）要好。

# Ajax
Ajax是一种常见的Web技术。它曾经被称为AJAX，Asynchronous Javascript And XML的首字母缩写，但是很大程度上用JSON取代了XML，所以它变成了Ajax。在网页中使用Ajax向服务器发出请求，不会触发页面重新加载的请求。这些请求是异步的 - 页面脚本不会停止等待响应。而是设置回调以在收到响应时处理响应。Ajax可用于使用任何HTTP方法发出请求。

# CORS
跨源资源共享（CORS）是同源策略（SOP）的放松机制。通过CORS标头，服务器可以允许来自外部源的请求，其中包括可以请求的内容以及这些请求中可以包含的标头。如果服务器不提供CORS标头，浏览器将应用SOP并拒绝发出请求，除非源是相同的。请注意，CORS的主要目的是仅允许某些受信任的来源。示例：具有可疑脚本的站点不能仅从其他站点的cookie中窃取用户的API并使用它们发出请求，因为API中的CORS配置不允许来自站点源的请求。注意：这不是保护API的机制，它是为了防止浏览器用户无意中访问您的API。

* [更多信息](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
* [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/)

# Resources
在RESTful API术语中，资源是客户端可能想要访问的有趣的任何信息。资源是存储在API中的数据的表达，虽然它们通常表示数据库表中的数据，但重要的是要了解它们并没有与数据库表一对一映射。资源可以组合来自多个表的数据，单个表中也可以存在多个资源表示。搜索等内容也被视为资源（毕竟，它会返回过滤后的数据表示）。

# Routing
**描述**：Web框架中的URL路由是框架将URL从HTTP请求转换为Python函数调用的过程。在定义路由时，URL要与Web应用程序定义的一系列URL模板匹配。请求会被路由到为第一个匹配的URL模板注册的函数中。模板中定义的任何变量都作为参数传递给函数。

**Flask中的路由**：Flask使用`app.route`装饰器结合视图函数定义路由。装饰器将路径的URL模板作为其参数，URL模板中的变量与函数的参数匹配。例如
```python
@app.route("/hello/<name>/")
def hello(name):
    return "hello {}".format(name)
```

**反向路由**：当要根据注册到应用程序的路由生成URL时，可以使用反向路由。这对于在不破坏代码的情况下管理路由非常有用 - 尤其当路由更改时，如果使用反向路由生成路由，则所有URL将自动匹配新路由。使用`url_for`功能完成反向路由，它可以从Flask导入。它将端点名称作为其第一个参数。它可以使用端点关键字参数进行设置，并且默认为视图函数的名称。其余参数必须与URL模板变量匹配。
```python
from flask import Flask, url_for

href = url_for("hello", name="donkey")
```
**Flask-RESTful路由**：使用Flask-RESTful资源类的路由是通过Api对象的`add_resource`方法完成的。这会将所有不同的HTTP方法路由到其对应的资源类方法。
```python
api.add_resource(SensorItem, "/api/sensors/<sensor>/")
```
反向路由可以通过两种方式完成：使用上述“反向路由”中描述的方法（默认端点名称是类名）或使用Api对象的url_for方法，该方法将资源类作为其第一个参数，其他的工作方式都相同。
```python
api.url_for(SensorItem, sensor=handle)
```
对于单个文件应用程序，此方法更清晰，但如果将资源拆分为多个模块，则可能导致循环导入问题。

# Callback
回调是一个被传递给程序的另一部分的函数，通常作为参数，在满足某些条件时被调用。例如，在发出Ajax请求时，通常会至少为成功和错误这两个情况注册回调。回调的一个典型特征是这个函数不能决定自己的参数，而必须使用调用它的程序部分提供的参数。回调也称为处理程序。一次性回调通常被定义为匿名函数。

# Anonymous functions
匿名函数通常用作就地函数来定义回调。它们的名称是因为它们的定义与函数类似，但没有名称。在JavaScript中，函数定义将函数作为对象返回，以便它可以作为参数传递给另一个函数。通常，当它使代码更具可读性时，它们被用作一次性回调，以便在需要回调的地方定义函数而不是其他地方。一个典型的例子是数组的forEach方法。它将回调作为其参数，并为其每个成员调用该函数。匿名函数的一个缺点是它们的函数每次都被重新定义，如果不断执行，这会导致很大的开销。

**举例**：
匿名函数也常见于Ajax调用：
```python
{{{highlight=javascript
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
在这种情况下，函数作为可调用属性存储在设置对象中。调用它们时，将执行函数中包含的代码。

# Response Body
响应体是http响应的一部分，它包含服务器发送的实际数据。响应正文是文本或二进制的，带有附加类型指令（例如JSON）的信息由响应的内容类型头定义。在成功请求的情况下，只有GET请求方法才会返回响应正文。

# 请求参数
查询参数是URL中包含的其他参数。您通常可以在网络搜索中看到这些内容。它们是通过HTTP请求传递任意参数的主要机制。它们与实际的URL地址之间用`?`分隔。每个参数都按照`key=value`成对写入，并且每对查询参数中间都用`&`分隔。在Flask应用程序中，可以找到`request.args`它们，就像字典一样。