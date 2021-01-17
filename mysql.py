import pymysql, os, json
from pymysql.cursors import DictCursor


class DB(object):
    """
    初始化数据库
    """
    # 也可以继承 Connection 这里没有选择继承
    def __init__(self):
        self.connect = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT')),
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

    def get_mappool(self, round_id, ingore_pool_publish = False):
        """
        取得圖池: round_id = 階段ID
        """
        # 初始化 mappool
        mappool = {}
        # 從資料庫取得階段資訊
        round = self.query_one(f"SELECT * FROM round WHERE id = {round_id}")
        # 檢查此階段的圖池是否已公布
        if round['pool_publish'] and not ingore_pool_publish: 
            # 從資料庫取得圖池
            pooldata = self.query_all(f"SELECT `id`, `beatmap_id`, `group`, `code`, `mods`, `info` FROM mappool WHERE round_id = {round_id} ORDER BY FIELD(`group`, 'NM', 'HD', 'HR', 'DT', 'FM', 'Roll', 'EZ', 'TB'), code")
        
            # map['info'] 轉化為 dict 類型
            for map in pooldata:
                map['info'] = json.loads(map['info'])

            # 將 map 以 group 分類
            for map in pooldata:
                # 如果這 map 的 group 沒有在 mappool.keys() 裡面，則創建它
                if map['group'] not in mappool.keys():
                    mappool[map['group']] = []

                # 將 map 添加到 mappool 的 group 裡
                mappool[map['group']].append(map)
            
        return {
            'round_id': int(round_id),
            'mappool': mappool
        }

    @property
    def active_rounds(self):
        """
        取得目前已開始的階段
        """
        rounds = self.query_all("SELECT * FROM round WHERE start_date < NOW()")
        return rounds

    def get_teams(self, id=None):
        query_team_text = "SELECT * FROM team"
        if id: query_team_text += " WHERE id = %d" % id

        teams = self.query_all(query_team_text)
        for t in teams:
            t['players'] = []
            players = self.query_all("SELECT * FROM player WHERE team = %s", (t['id'],))
            for p in players:
                p['info'] = json.loads(p['info'])
                p['bp1'] = json.loads(p['bp1'])
                t['players'].append(p)
        return teams

    def get_players(self, id=None):
        query_text = "SELECT * FROM player"
        if id: query_text += " WHERE id = %d" % id
        players = self.query_all(query_text)
        for p in players:
                p['info'] = json.loads(p['info'])
                p['bp1'] = json.loads(p['bp1'])
        return players