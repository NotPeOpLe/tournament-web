import osuapi
import mysql
import json
from rich import print

sql = mysql.DB()

'''1v1 註冊
user_info: dict = osuapi.get2(users=user_id)
user_info.pop('page')

user_bp = osuapi.get2(users=user_id,scores='best')[0]

sql.query('INSERT INTO team (tourney_id, full_name, flag_name, acronym) VALUES (%s,%s,%s,%s)',
    (1,user_info['username'], f'avatar.{user_info["id"]}', user_info['username']))

teams = sql.query('SELECT * FROM team WHERE tourney_id = 1 AND full_name = %s', user_info['username'], one=True)

sql.query('INSERT INTO player (tourney_id, team_id, user_id, username, info, bp1) VALUES (%s,%s,%s,%s,%s,%s)',
    (1, 1, user_info['id'], user_info['username'], json.dumps(user_info), json.dumps(user_bp)))
'''

# mappool = []

# for m in mappool:
#     info = osuapi.get2(beatmaps=m[0])

#     sql.query('INSERT INTO mappool (tourney_id, round_id, beatmap_id, map_code, mods, info) VALUES (%s,%s,%s,%s,%s,%s)',
#     (1, 2, m[0], m[1], m[2], json.dumps(info)))

# players = sql.query_all('SELECT id, user_id, username FROM player')
# for p in players:
#     info = osuapi.get(osuapi.V1Path.get_user, u=p['user_id'], m=0)[0]
#     info.pop('events')
#     bp1 = osuapi.get(osuapi.V1Path.get_user_best, u=p['user_id'], m=0)[0]

#     for k in info:
#         info[k] = osuapi.todata(info[k])
#     for k in bp1:
#         bp1[k] = osuapi.todata(bp1[k])
#     sql.query('UPDATE player SET info = %s ,bp1 = %s WHERE id = %s', (json.dumps(info), json.dumps(bp1), p['id']))

mappool = sql.query_all("SELECT * FROM mappool")
for map in mappool:
    data = osuapi.get(osuapi.V1Path.get_beatmaps, b=map['beatmap_id'], m=0)[0]
    for k in data:
        data[k] = osuapi.todata(data[k])
    sql.query('UPDATE mappool SET info = %s WHERE id = %s', (json.dumps(data), map['id']))