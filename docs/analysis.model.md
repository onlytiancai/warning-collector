### 用例分析

1. 产生一条报警：分类，主机，应用名，级别，标题，内容，时间
1. 查看最近一周的报警
1. 查看某条报警的详情
1. 查看某个分类的报警
1. 查看某个级别的报警
1. 报警通过邮件和微信发送给用户
1. 查看最近的每天报警趋势
1. 添加一个分类
1. 删除一个分类


### 数据库设计

users表

1. user_id: key
1. app_id
1. sina_user_id
1. user_name
1. created_on

warnings表

1. user_id: key
1. cate:
1. host:
1. appname
1. level
1. title
1. content
1. created_on: key

warning_cates表

1. user_id: key
1. cate

### API设计

1. POST /send_warning/{user_id} : 产生一条报警
    1. app_id
    1. cate
    1. host
    1. appname
    1. level
    1. title
    1. content
    1. created_on
1. GET /warnings/{cate}/{begin_time}/{end_time}: 查看报警列表
    1. cate默认为None
    1. begin_time默认为本周一
    1. end_time默认为今天


SQLAlchemy error MySQL server has gone away
http://stackoverflow.com/questions/16341911/sqlalchemy-error-mysql-server-has-gone-away
Python SQLAlchemy - “MySQL server has gone away”
http://stackoverflow.com/questions/18054224/python-sqlalchemy-mysql-server-has-gone-away
SQLAlchemy proper session handling in multi-thread applications
http://stackoverflow.com/questions/9619789/sqlalchemy-proper-session-handling-in-multi-thread-applications
Web.py中Sqlalchemy scoped_session的使用
http://blog.csdn.net/d_yang/article/details/2937214
