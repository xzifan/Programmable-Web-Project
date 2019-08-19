# 描述
该描述中包含有关设置和运行Flask应用程序的基本说明。请参考下面的术语“创建数据库”和“启动应用程序”。对于所有的操作，您需要在包含您的应用程序的文件夹中完成。

## 创建数据库
在你第一次运行之前，你需要先创建数据库：
```python
your/app/folder$ ipython
[1]: from yourapp import db
[2]: db.create_all()
```

## 启动应用程序
在Linux中：
```python
your/app/folder$ export FLASK_APP=yourapp.py
your/app/folder$ export FLASK_ENV=development
flask run
```
在Windows中：
```python
C:\your\app\folder> set FLASK_APP=yourapp.py
C:\your\app\folder> set FLASK_ENV=development
flask run
```