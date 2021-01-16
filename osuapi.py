import re
import requests, os, logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger(__name__)

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

def toen_isactive(Token):
    url = 'https://osu.ppy.sh/api/v2/me'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {Token}'}
    
    if requests.get(url, headers=headers).status_code == 200:
        return True
    else:
        return False

def clientToken():	
    url = 'https://osu.ppy.sh/oauth/token'	
    token = open('access_token','w+')
    if not toen_isactive(token.read()):
        payload = {'username': os.getenv('osu_username'),	
            'password': os.getenv('osu_password'),	
            'grant_type': 'password',	
            'client_id': '5',	
            'client_secret': 'FGc9GAtyHzeQDshWP5Ah7dega8hJACAJpQtw6OXk',	
            'scope': '*'}
        headers = {	
            'Accept': 'application/json',	
            'User-Agent': 'osu!',	
            'Accept-Encoding': 'gzip, deflate'	
        }	

        response = requests.request('POST', url, headers=headers, data = payload)
        access_token = response.json()['access_token']
        token.write(access_token)
        token.close()
        log.info('透過 clientToken() 取得 Token')
    else:
        log.info('透過 File 取得 Token')

    return token

v2Token = None if None else clientToken()
v2Headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {v2Token}'}

def get(path:V1Path, **args):
    args['k'] = API_KEY
    req = requests.get(
        url = 'https://osu.ppy.sh/api/' + path,
        params = args
        )

    return req.json()

def get2(**kargs):
    path = ''
    a = []
    for p in kargs.items():
        for q in p:
            a.append(str(q))
    path = '/'.join(a)
    req = requests.get(f'https://osu.ppy.sh/api/v2/{path}', headers=v2Headers)
    return req.json()
