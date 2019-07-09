# header
header是包含在HTTP请求和响应中的附加信息字段。
header的典型例子是内容类型和内容长度，它们通知接收者应该如何解释内容以及应该解释多长时间。
在Flask headers中，header包含在request.headers属性中，该属性的工作方式类似于字典。
你可以查看header中[所有字段列表](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields)