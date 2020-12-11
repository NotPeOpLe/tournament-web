import pymysql, os
from pymysql.cursors import DictCursor


class DB(object):
    """
    初始化数据库
    """
    # 也可以继承 Connection 这里没有选择继承
    def __init__(self):
        self.connect = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            cursorclass=DictCursor,
            autocommit=True
        )
        # 创建游标对象  **主要**
        self.cursor = self.connect.cursor()

    def query_one(self, query, args=None):
        """
        查询数据库一条数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        """
        self.connect.ping(reconnect=True)
        self.cursor.execute(query, args)
        # 将更改提交到数据库
        self.connect.commit()
        return self.cursor.fetchone()

    def query_all(self, query, args=None):
        """
        查询数据库所有数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        """
        self.connect.ping(reconnect=True)
        self.cursor.execute(query, args)
        # 将更改提交到数据库
        self.connect.commit()
        return self.cursor.fetchall()

    def query(self, query, args=None, one=True):
        """
        主体查询数据
        :param query: 执行MySQL语句
        :param args: 与查询语句一起传递的参数(给语句传参) 元组、列表和字典
        :param one: one是True 时候执行query_one, 否则执行query_all
        """
        
        if one:
            return self.query_one(query, args)
        return self.query_all(query, args)

    def close(self):
        """
        关闭
        :return:
        """
        # 关闭游标
        self.cursor.close()
        # 断开数据库连接
        self.connect.close()