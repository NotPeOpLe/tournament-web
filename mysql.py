import pymysql, os, json
from datetime import datetime
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

    def get_mappool(self, round_id, ingore_pool_publish=False, format=True):
        """
        取得圖池: round_id = 階段ID
        """
        # 初始化 mappool
        mappool = {}
        # 從資料庫取得階段資訊
        round = self.query_one(f"SELECT * FROM round WHERE id = {round_id}")
        # 從資料庫取得圖池
        pooldata = self.query_all(f"SELECT m.*, mg.color, s.user_id, s.username FROM mappool AS m LEFT JOIN staff AS s ON s.id=m.nominator LEFT JOIN map_group AS mg ON mg.name=m.group WHERE round_id = {round_id} ORDER BY FIELD(`group`, 'FM', 'NM', 'HD', 'HR', 'DT', 'Roll', 'EZ', 'TB'), code")
        # 檢查此階段的圖池是否已公布
        if round['pool_publish'] or ingore_pool_publish:
            if format:
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
            else:
                for map in pooldata:
                    map['info'] = json.loads(map['info'])
                return pooldata
       

    @property
    def active_rounds(self):
        """
        取得目前已開始的階段
        """
        rounds = self.query_all("SELECT * FROM round WHERE start_date < NOW()")
        return rounds

    @property
    def current_round(self):
        """
        取得當前進行的階段
        """
        return self.query_one("SELECT * FROM round WHERE start_date < NOW() ORDER BY start_date DESC")

    @property
    def tourney(self):
        return self.query_one("SELECT * FROM tourney WHERE id = 1")

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

    def get_matchs(self, round_id=None, id=None):
        query_text = """SELECT JSON_OBJECT(
            'id', m.id,
            'code', m.code,
            'date', DATE_FORMAT(m.date, '%Y-%m-%d %H:%i'),
            'round', JSON_OBJECT('id', r.id, 'name', r.name, 'description', r.description, 'best_of', r.best_of, 'start_date', DATE_FORMAT(r.start_date, '%Y-%m-%d %H:%i')),
            'team1', JSON_OBJECT('id', t1.id, 'full_name', t1.full_name, 'flag_name', t1.flag_name, 'acronym', t1.acronym, 'score', m.team1_score),
            'team2', JSON_OBJECT('id', t2.id, 'full_name', t2.full_name, 'flag_name', t2.flag_name, 'acronym', t2.acronym, 'score', m.team2_score),
            'referee', JSON_OBJECT('id', ref.id, 'group_id', ref.group_id, 'user_id', ref.user_id, 'username', ref.username),
            'streamer', JSON_OBJECT('id', str.id, 'group_id', str.group_id, 'user_id', str.user_id, 'username', str.username),
            'commentator', JSON_OBJECT('id', com.id, 'group_id', com.group_id, 'user_id', com.user_id, 'username', com.username),
            'commentator2', JSON_OBJECT('id', com2.id, 'group_id', com2.group_id, 'user_id', com2.user_id, 'username', com2.username),
            'mp_link', m.mp_link,
            'video_link', m.video_link,
            'live', (m.date < NOW()),
            'loser', (m.loser = 1),
            'stats', m.stats,
            'note', m.note,
            'winpoint', CEIL(r.best_of/2+1)
            ) AS `json`
            FROM `match` m
            LEFT JOIN `round` r ON r.id = m.round_id
            LEFT JOIN team t1 ON t1.id = m.team1
            LEFT JOIN team t2 ON t2.id = m.team2
            LEFT JOIN staff ref ON ref.id = m.referee
            LEFT JOIN staff str ON str.id = m.streamer
            LEFT JOIN staff com ON com.id = m.commentator
            LEFT JOIN staff com2 ON com2.id = m.commentator2
            """
        if round_id or id:
            query_text += " WHERE "
            if round_id: query_text += "m.round_id = %s " % round_id
            if id: query_text += "m.id = %d " % id
        matchs = []
        query = self.query_all(query_text)
        for m in query:
            matchs.append(json.loads(m['json']))

        return matchs

    def get_staff(self, staff_id=None, user_id=None, format=True, viewall=False):
        if user_id:
            query = self.query_one('select * from staff where user_id = %s and active = 1', (user_id,))
            return query

        if staff_id:
            query = self.query_one('select * from staff where id = %s and active = 1', (staff_id,))
            return query

        va = 'WHERE s.active = 1 ORDER BY s.active, s.id' if not viewall else 'ORDER BY s.id'

        query = self.query_all('SELECT s.id, s.user_id, s.username, s.privileges, s.active, g.* FROM staff s INNER JOIN `group` g ON g.id = s.group_id ' + va)
        if format:
            staff = {}
            for s in query:
                if s['ch_name'] not in staff.keys():
                    staff[s['ch_name']] = []
                staff[s['ch_name']].append(s)
            return staff
        else:
            return query