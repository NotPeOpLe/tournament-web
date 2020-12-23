import re
import requests, os, logging
from rich import print

logging.basicConfig(level=logging.DEBUG)
API_KEY = os.getenv('OSU_API_KEY')

def todata(value):
    try:
        return eval(value)
    except:
        return value

class V1Path:
    get_beatmaps = 'get_beatmaps'
    get_user = 'get_user'
    get_user_best = 'get_user_best'
    get_user_recent = 'get_user_recent'
    get_scores = 'get_scores'
    get_match = 'get_match'
    get_replay = 'get_replay'

def get(path:V1Path, **args):
    args['k'] = API_KEY
    req = requests.get(
        url = 'https://osu.ppy.sh/api/' + path,
        params = args
        )

    return req.json()

def ouput_registeredlist() -> None:
    registers = [
        9868529,654296,2472609,5155973,3416783,2200982,
        9539163,2808144,7172340,12717375,1860489,5920715,
        3366658,4519494,5413624,3163649,4183988,1786610,
        3066316,1593180,2529213,2165650,9991663,9632700,
        3517706,8660293
        ]

    registeredlist = []
    for player in registers:
        player_data:dict = get(V1Path.get_user, u=player, m=0)[0]
        player_data.pop('events')

        bp1:dict = get(V1Path.get_user_best, u=player, m=0, limit=1)[0]

        for key in player_data:
            player_data[key] = todata(player_data[key])

        for key in bp1:
            bp1[key] = todata(bp1[key])

        newdata = player_data
        newdata['bp1'] = bp1
        
        registeredlist.append(newdata)

    with open('registered.list', 'w+', encoding='utf8') as output_file:
        print(registeredlist, file=output_file)
        output_file.close()

def output_staff() -> None:
    with open('staff.txt', 'r', encoding='utf8') as staff_file:
        staff_value = staff_file.read()
        staff_list = staff_value.split('\n')
        staff_file.close()

    staff = {}
    for s in staff_list:
        s = s.split(':')

        try:
            s_data:dict = get(V1Path.get_user, u=s[0], m=0)[0]
        except:
            pass
        
        if not staff.get(s[1]):
            staff[s[1]] = []

        staff[s[1]].append({
            'user_id': todata(s_data['user_id']),
            'username': todata(s_data['username']),
            'group': todata(s[1])
        })

    with open('staff.list', 'w+', encoding='utf-8') as output_file:
        print(staff, file=output_file)
        output_file.close()

def output_mappool() -> None:
    mappool = []
    mappool_files = []
    for file in os.listdir(os.getcwd()+"\\input"):
        if file.startswith('mappool-') and file.endswith('.txt'):
            mappool_files.append(file)
    
    for mappool_file in mappool_files:
        mappool_name = re.match(r'mappool-(.+).txt', mappool_file).group(1)
        with open(f'{os.getcwd()}\\input\\{mappool_file}', 'r', encoding='utf-8') as mf:
            maps = mf.read().split('\n')
            for m in maps:
                map = m.split(":") # 0=mapid; 1=mod(s); 2=num
                map_data = get(V1Path.get_beatmaps,b=map[0], m=0)[0]
                map_data['round_name'] = mappool_name
                map_data['use_mod'] = map[1]
                map_data['mapname'] = f"{map[1]}{map[2]}"
                mappool.append(map_data)

    with open('mappools.list', 'w+', encoding='utf-8') as output:
        print(mappool, file=output)
        output.close()