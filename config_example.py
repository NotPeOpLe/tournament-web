class BaseConfig(object):
    ENV = 'production'
    DEBUG = False  # 是否開啟Debug模式
    TESTING = False  # 是否開啟測試模式
    # 異常傳播(是否在控制檯列印LOG) 當Debug或者testing開啟後,自動為True
    PROPAGATE_EXCEPTIONS = None
    PRESERVE_CONTEXT_ON_EXCEPTION = None  # 一兩句話說不清楚,一般不用它
    SECRET_KEY = None  # 之前遇到過,在啟用Session的時候,一定要有它
    PERMANENT_SESSION_LIFETIME = 31  # days , Session的生命週期(天)預設31天
    USE_X_SENDFILE = False  # 是否棄用 x_sendfile
    LOGGER_NAME = None  # 日誌記錄器的名稱
    LOGGER_HANDLER_POLICY = 'always'
    SERVER_NAME = None  # 服務訪問域名
    APPLICATION_ROOT = None  # 專案的完整路徑
    SESSION_COOKIE_NAME = 'session'  # 在cookies中存放session加密字串的名字
    SESSION_COOKIE_DOMAIN = None  # 在哪個域名下會產生session記錄在cookies中
    SESSION_COOKIE_PATH = None  # cookies的路徑
    SESSION_COOKIE_HTTPONLY = True # 控制 cookie 是否應被設定 httponly 的標誌，
    SESSION_COOKIE_SECURE = False  # 控制 cookie 是否應被設定安全標誌
    SESSION_REFRESH_EACH_REQUEST = True  # 這個標誌控制永久會話如何重新整理
    MAX_CONTENT_LENGTH = None  # 如果設定為位元組數， Flask 會拒絕內容長度大於此值的請求進入，並返回一個 413 狀態碼
    SEND_FILE_MAX_AGE_DEFAULT = 12, # hours 預設快取控制的最大期限
    TRAP_BAD_REQUEST_ERRORS = False
    # 如果這個值被設定為 True ，Flask不會執行 HTTP 異常的錯誤處理，而是像對待其它異常一樣，
    # 通過異常棧讓它冒泡地丟擲。這對於需要找出 HTTP 異常源頭的可怕除錯情形是有用的。
    TRAP_HTTP_EXCEPTIONS = False
    # Werkzeug 處理請求中的特定資料的內部資料結構會丟擲同樣也是“錯誤的請求”異常的特殊的 key errors 。
    # 同樣地，為了保持一致，許多操作可以顯式地丟擲 BadRequest 異常。
    # 因為在除錯中，你希望準確地找出異常的原因，這個設定用於在這些情形下除錯。
    # 如果這個值被設定為 True ，你只會得到常規的回溯。
    EXPLAIN_TEMPLATE_LOADING = False
    PREFERRED_URL_SCHEME = 'http'  # 生成URL的時候如果沒有可用的 URL 模式話將使用這個值
    JSON_AS_ASCII = True
    # 預設情況下 Flask 使用 ascii 編碼來序列化物件。如果這個值被設定為 False ，
    # Flask不會將其編碼為 ASCII，並且按原樣輸出，返回它的 unicode 字串。
    # 比如 jsonfiy 會自動地採用 utf-8 來編碼它然後才進行傳輸。
    JSON_SORT_KEYS = False
    # 預設情況下 Flask 按照 JSON 物件的鍵的順序來序來序列化它。
    # 這樣做是為了確保鍵的順序不會受到字典的雜湊種子的影響，從而返回的值每次都是一致的，不會造成無用的額外 HTTP 快取。
    # 你可以通過修改這個配置的值來覆蓋預設的操作。但這是不被推薦的做法因為這個預設的行為可能會給你在效能的代價上帶來改善。
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSONIFY_MIMETYPE = 'application/json'
    TEMPLATES_AUTO_RELOAD = None

    # 自訂
    MYSQL_HOST = None
    MYSQL_PORT = None
    MYSQL_USER = None
    MYSQL_PASSWORD = None
    MYSQL_DB = None
    
    OSU_USERNAME = None
    OSU_PASSWORD = None
    OSU_API_KEY = None
    OSU_CLIENT_ID = None
    OSU_CLIENT_SCERET = None
    OSU_REDIRECT_URL = None
    
class DebugConfig(BaseConfig):
    DEBUG = True