import requests, os
from logger import log

CLIENT_ID = 647
CLIENT_SCERET = 'DRAgvrg7F3rRlaKc26BHGaRbyR5r5R372cIAchNF'
REDIRECT_URL = 'https://840.tw/manager/callback'
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

def authorize(state, scope):
    return f"https://osu.ppy.sh/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}&state={state}&scope={scope}"

def toen_isactive(Token):
    url = 'https://osu.ppy.sh/api/v2/me'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {Token}'}
    
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        return True
    else:
        return False

def clientToken():	
    url = 'https://osu.ppy.sh/oauth/token'	
    tokenr = open('access_token','r+')
    toekn_read = tokenr.read().strip()
    tokenr.close()
    if not toen_isactive(toekn_read):
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
        tokenw = open('access_token','w+')
        tokenw.write(access_token)
        tokenw.close()
        log.info('透過 clientToken() 取得 Token')
        return access_token
    else:
        log.info('透過 File 取得 Token')
        return toekn_read

v2Token = None
v2Headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {v2Token}'}

def get_token(code):
    url = "https://osu.ppy.sh/oauth/token"

    payload = f'grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SCERET}&redirect_uri={REDIRECT_URL}&code={code}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 400:
        return None
    return r.json()

def get(path:V1Path, **args):
    args['k'] = API_KEY
    req = requests.get(
        url = 'https://osu.ppy.sh/api/' + path,
        params = args
        )

    return req.json()

def get2(token=None, **kargs):
    if not v2Token: clientToken()
    headers = v2Headers
    if token:
        headers['Authorization'] = f'Bearer {token}'
    path = ''
    a = []
    for p in kargs.items():
        for q in p:
            a.append(str(q))
    path = '/'.join(a)
    req = requests.get(f'https://osu.ppy.sh/api/v2/{path}', headers=headers)
    return req.json()
