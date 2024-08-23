"""
基本工具库
"""

import sys
import time
import datetime
import os
import random
import re
import urllib.parse as url
from loguru import logger
from .richx import print_exception, track, print


__all__ = [
    "base64_decode",
    "base64_encode",
    "clear",
    "date_next",
    "ddddocr",
    "faker",
    "filedir",
    "filepath",
    "fromtimestamp",
    "get_proxies",
    "getlock",
    "getpid",
    "gettid",
    "get_ip",
    "get_real_ip",
    "get_2fa_secret",
    "get_2fa_token",
    "listdir",
    "logger",
    "log",
    "ipython_extension",
    "md5",
    "now",
    "os",
    "pdf2text",
    "python",
    "randint",
    "random",
    "re",
    "read_json",
    "read_excel",
    "retry",
    "run_nohup",
    "run_process",
    "send_bot",
    "sha1",
    "sha256",
    "sha512",
    "sleep",
    "sleep_progress",
    "sys",
    "time_next",
    "timeit",
    "timeparse",
    "timeparse2",
    "timestamp",
    "to_df",
    "to_excel",
    "to_gzip",
    "to_html",
    "to_json",
    "today",
    "tongji_content",
    "ua",
    "url",
    "wait",
    "win11toast",
]

getpid = os.getpid
python = sys.executable
randint = random.randint
log = logger


def timeparse(
    timestr: str,
    parserinfo: bool | None = None,
    dayfirst: bool | None = None,
    yearfirst: bool | None = None,
    ignoretz: bool = True,
    fuzzy: bool = False,
    fuzzy_with_tokens: bool = False,
    default: None = None,
    tzinfos: None = None,
):
    """
    ## 基于 dateutil.parser 封装

    timestr: 时间字符串
    parserinfo: 解析器信息
    dayfirst: 无法判断时, 第一个数字是否为日
    yearfirst: 无法判断时, 第一个数字是否为年份
    ignoretz: 是否忽略时区信息, 默认忽略时区信息
    fuzzy: 是否启用模糊匹配, 启动后可以从字符串中提取出时间字符串中的日期和时间信息
    fuzzy_with_tokens: 是否返回模糊匹配的结果
    default: 当解析失败时返回的默认值
    tzinfos: 时区信息
    """
    from dateutil.parser import parse

    return parse(
        timestr,
        parserinfo=parserinfo,
        dayfirst=dayfirst,
        yearfirst=yearfirst,
        ignoretz=ignoretz,
        fuzzy=fuzzy,
        fuzzy_with_tokens=fuzzy_with_tokens,
        default=default,
        tzinfos=tzinfos,
    )


def timeparse2(
    date_string,
    date_formats=None,
    languages=None,
    locales=None,
    region=None,
    settings=None,
    detect_languages_function=None,
):
    """
    ## dateparser 封装

    date_string: 时间字符串
    date_formats: 时间格式列表, 例如 ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
    languages: 语言列表, 例如 ["zh", "en"]
    locales: 地区列表, 例如 ["zh", "en"]
    region: 地区
    settings: 设置
    detect_languages_function: 检测语言函数
    """
    try:
        from dateparser import parse
    except ImportError:
        raise ImportError("请先安装 dateparser 模块")

    return parse(
        date_string,
        date_formats=date_formats,
        languages=languages,
        locales=locales,
        region=region,
        settings=settings,
        detect_languages_function=detect_languages_function,
    )


def filedir():
    """
    文件目录
    """
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def filepath():
    """
    文件绝对路径
    """
    return os.path.abspath(sys.argv[0])


def get_2fa_secret():
    """
    2FA(双因素身份验证)密钥生成
    """
    secret = "".join(random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", 32))
    return secret


def get_2fa_token(secret):
    """
    2FA(双因素身份验证)通过密钥获取实时 token

    secret = get_2fa_secret()
    """
    import base64
    import hmac
    import time

    secret_bytes = base64.b32decode(secret)
    time_interval = int(time.time()) // 30
    hmac_value = hmac.new(secret_bytes, time_interval.to_bytes(8), "sha1").digest()
    offset = hmac_value[-1] & 0x0F
    dynamic_code = (
        (hmac_value[offset] & 0x7F) << 24
        | (hmac_value[offset + 1] & 0xFF) << 16
        | (hmac_value[offset + 2] & 0xFF) << 8
        | (hmac_value[offset + 3] & 0xFF)
    )
    return f"{dynamic_code % 10**6:06d}"


def sha1(string: str | bytes) -> str:
    """
     hashlib.sha1 封装

    string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha1(string).hexdigest()


def sha256(string: str | bytes) -> str:
    """
     hashlib.sha256 封装

    string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha256(string).hexdigest()


def sha512(string: str | bytes) -> str:
    """
     hashlib.sha512 封装

    string: 字符串或字节
    """
    import hashlib

    if not isinstance(string, bytes):
        string = f"{string}".encode()
    return hashlib.sha512(string).hexdigest()


def md5(string: bytes | str):
    """
    md5 加密
    """
    import hashlib

    if isinstance(string, str):
        string = string.encode()
    result = hashlib.md5(string).hexdigest()
    return result


def gettid():
    """
    获取线程ID
    """
    import threading

    return threading.get_ident()


def getlock():
    """
    获取线程锁
    """
    import threading

    return threading.Lock()


def ipython_extension():
    """
    ipython 插件, 全局 pretty print, 全局 traceback
    """
    from rich.pretty import install
    from rich.traceback import install as tr_install

    install()
    tr_install()


def faker():
    """
    faker 封装，增加faker().zh 为中文
    """
    if "fake" in faker.__dict__:
        return faker.fake

    from faker import Faker

    fake = Faker()
    fake.zh = Faker("zh")
    faker.fake = fake
    return fake


def base64_encode(string: bytes | str):
    """
    base64编码
    """
    import base64

    if isinstance(string, str):
        string = string.encode()
    return base64.b64encode(string).decode()


def base64_decode(string: bytes | str):
    """
    base64解码
    """
    import base64

    if isinstance(string, str):
        string = string.encode()
    return base64.b64decode(string).decode()


def clear():
    """
    清屏
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_proxies(
    n: int = 1,
    httpx: bool = False,
    proxies_dict: dict | None = None,
):
    """
    ## 随机返回代理

    如果未设置 proxies_dict，则检测环境变量 HTTP_PROXY_DICT,  配置环境变量请使用 to_json 将 HTTP_PROXY_DICT 转换成 json

    n: 代理选择，数字或对应的字符串
    proxies_dict: 代理字典，{'1':['https://localhost:7890'], '2': ['https://localhost:7891']}
    """
    if not proxies_dict:
        http_proxy_dict_str = os.getenv("HTTP_PROXY_DICT", "")
        if not http_proxy_dict_str:
            print("[red]未配置 HTTP_PROXY_DICT[/]")
            raise Exception()
        proxies_dict = read_json(http_proxy_dict_str)
    proxyurl = random.choice(proxies_dict.get(str(n)))
    if httpx:
        proxies = {
            "http://": proxyurl,
            "https://": proxyurl,
        }
    else:
        proxies = {
            "http": proxyurl,
            "https": proxyurl,
        }
    return proxies


def listdir(
    path=None,
    key=None,
    reverse: bool = False,
):
    """
    help(os.listdir)

    path: 目录路径
    key: 排序方式
    reverse: 指定是否反转, 默认否。
    """
    return sorted(
        os.listdir(path),
        key=key,
        reverse=reverse,
    )


def now(
    fmt_type: int | None = None,
    fmt: str | None = None,
):
    """
    默认返回当前时间, 精度到秒。

    fmt_type: 格式化类型。
    fmt: 通过 strformat 格式化。

    - fmt=None -> datetime.datetime(2024, 1, 18, 11, 44, 57)
    - fmt_type=1 -> "2024-01-18 11:44:57"
    - fmt_type=2 -> 1705549497 # 10位时间戳
    - fmt_type=3 -> 1705555472772 # 13位时间戳
    - fmt_type=4 -> datetime.date(2024, 1, 18)
    - fmt_type=5 -> "2024-01-18"
    - fmt_type=6 -> "2024/01/18"
    - fmt_type=7 -> "20240118"
    """
    if fmt:
        return datetime.datetime.now().strftime(fmt)
    if fmt_type == 1:
        return f"{datetime.datetime.now().replace(microsecond=0)}"
    elif fmt_type == 2:
        return int(time.time())
    elif fmt_type == 3:
        return int(time.time() * 1000)
    elif fmt_type == 4:
        return datetime.date.today()
    elif fmt_type == 5:
        return f"{datetime.date.today()}"
    elif fmt_type == 6:
        return f"{datetime.date.today():%Y/%m/%d}"
    elif fmt_type == 7:
        return f"{datetime.date.today():%Y%m%d}"
    else:
        return datetime.datetime.now().replace(microsecond=0)


def timestamp(n: int = 10):
    """
    返回时间戳

    n 可选 10位和13位。
    """
    if n == 13:
        return int(time.time() * 1000)
    return int(time.time())


def today(fmt_type=None):
    """
    返回今天日期

    - fmt=1 -> "2024-01-18"
    - fmt=2 -> "2024/01/18"
    - fmt=3 -> "20240118"
    """
    if not fmt_type:
        return datetime.date.today()
    if fmt_type == 1:
        return f"{datetime.date.today()}"
    elif fmt_type == 2:
        return f"{datetime.date.today():%Y/%m/%d}"
    elif fmt_type == 3:
        return f"{datetime.date.today():%Y%m%d}"


def tongji_content(
    content: str,
    keywords: list[str],
    strict=False,
    to_dict=False,
):
    """
    统计每篇文章中关键词出现次数

    - content: 需要统计的文本。
    - keywords: 需要统计的关键词。
    - strict: 是否严格模式，默认False 忽略大小写, True 不忽略。
    - to_dict: 是否导出为字典格式。
    """
    keyword_tongji_list = []
    for keyword in set(keywords):
        if not strict:
            p1 = content.upper().count(keyword.upper())
        else:
            p1 = content.count(keyword)
        if p1 > 0:
            keyword_tongji_list.append([keyword, p1])
    if to_dict:
        return dict(keyword_tongji_list)
    return [
        f"{k[0]}({k[1]})"
        for k in sorted(
            keyword_tongji_list,
            key=lambda x: x[-1],
            reverse=True,
        )
    ]


def date_next(
    days: int = 0,
    weeks: int = 0,
    date: datetime.date | None = None,
):
    """
    返回下一个的日期, 默认为0, 负数为过去, 正数为未来。
    """
    if not date:
        date = datetime.date.today()
    return date + datetime.timedelta(days=days, weeks=weeks)


def time_next(
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    weeks: int = 0,
    months: int = 0,
    years: int = 0,
    start: tuple | datetime.datetime | None = None,
    fmt: str | None = None,
):
    """
    返回下一个的时间, 默认为0, 负数为过去, 正数为未来。先算月份再算年, 然后依次计算。

    - days: 偏移天数
    - hours: 偏移小时数
    - minutes: 偏移分钟数
    - seconds: 偏移秒数
    - weeks: 偏移周数
    - months: 偏移月数
    - years: 偏移年数
    - start: 开始时间, (2024, 1, 20, 10, 12, 23) 或者 datetime.datetime(2024, 1, 20, 10, 12, 23)
    - fmt: 指定输出格式。
    """
    import calendar

    if start:
        if not isinstance(start, datetime.datetime):
            start = datetime.datetime(*start)
    else:
        start = datetime.datetime.now().replace(microsecond=0)
    if months:
        # 获取下个时间的年份和月份
        next_year = start.year + (start.month == 12)
        next_month = start.month + months
        if next_month > 12:
            next_year += next_month // 12
            next_month = next_month % 12
        if next_month < 1:
            next_year -= abs(next_month) // 12 + 1
            next_month = 12 - abs(next_month) % 12

        # 获取下个时间的最大天数
        next_month_max_day = calendar.monthrange(next_year, next_month)[1]
        start = start.replace(
            year=next_year, month=next_month, day=min(start.day, next_month_max_day)
        )
    if years:
        real_next_year = start.year + 1
        next_month_max_day = calendar.monthrange(real_next_year, start.month)[1]
        start = start.replace(
            year=real_next_year,
            month=start.month,
            day=min(start.day, next_month_max_day),
        )
    results = start + datetime.timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        weeks=weeks,
    )
    if fmt:
        return results.strftime(fmt)
    else:
        return results


def sleep(n: int):
    """
    等待n秒, 模拟阻塞
    """
    return time.sleep(n)


def sleep_progress(n: int = 1, info=None, transient=False):
    """
    等待n秒, 模拟阻塞, 进度条。

    n: 等待秒数
    info: 定制输出信息
    transient: 运行完是否隐藏
    """
    if not info:
        info = f"等待{n}秒"
    for _ in track(range(int(n // 0.02)), info, transient=transient):
        time.sleep(0.02)


def fromtimestamp(t: int | str):
    """
    从时间戳返回 datetime 格式, 自动判断字符串和数字, 不符合格式要求会原样返回。
    """
    _t = t
    if isinstance(t, str) and t.isdigit():
        t = int(t[:10])
    if isinstance(t, (int, float)):
        return datetime.datetime.fromtimestamp(int(str(t)[:10]))
    return _t


def read_json(filepath, encoding="utf-8"):
    """
    JSON 反序列化, 读取 JSON 文件

    path_string: JSON 文件路径或字符串
    """
    import json

    if not os.path.isfile(filepath):
        return json.loads(filepath)
    with open(filepath, "r", encoding=encoding) as f:
        q = json.load(f)
    return q


def read_excel(
    io,
    sheet_name: str | int | list | None = 0,
    **kwargs,
):
    """
    读取 Excel 文件

    io: 文件路径或文件对象
    sheet_name: 工作表名称
    ---
    其他参数
        header: 表头所在行
        names: 列名
        index_col: 索引列
        usecols: 列选择
        dtype: 数据类型
        engine: 引擎
        converters: 转换器
        true_values: 真值
        false_values: 假值
        skiprows: 跳过行数
        nrows: 读取行数
        na_values: 空值
        keep_default_na: 默认空值
        na_filter: 空值过滤
        verbose: 详细信息
        parse_dates: 解析日期
        date_format: 日期格式
        thousands: 千位分隔符
        decimal: 小数点分隔符
        comment: 注释
        skipfooter: 跳过尾部行数
        storage_options: 存储选项
        dtype_backend: "pyarrow" | "numpy_nullable"
        engine_kwargs: 引擎参数
    """
    import pandas as pd

    return pd.read_excel(
        io,
        sheet_name=sheet_name,
        **kwargs,
    )


def to_json(
    obj,
    filename=None,
    encoding="utf-8",
    ensure_ascii: bool = False,
    indent: int | None = None,
    separators: tuple | None = None,
    default_dict: dict | None = None,
):
    """
    JSON 序列化, 将Python 对象写入文件或转换为字符串。

    filename: JSON 文件路径
    indent: 缩进
    ensure_ascii: 默认不转为unicode
    separators: 分隔符, 默认为 (", ", ": ")
    default_dict: 自定义转换类型, 启用后默认会转换成字符串。例如: {numpy.ndarray: lambda x: x.tolist()}
    """
    import json

    def default_tool(obj):
        for i in default_dict:
            if isinstance(obj, i):
                return default_dict[i](obj)
        else:
            return str(obj)

    default = default_tool if default_dict else None

    if not filename:
        return json.dumps(
            obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
            separators=separators,
            default=default,
        )
    else:
        with open(filename, "w", encoding=encoding) as f:
            json.dump(
                obj,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                separators=separators,
                default=default,
            )


def get_ip():
    """
    获取本机 IP
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_real_ip():
    """
    获取本机真实 IP
    """
    import httpx

    ip = httpx.get("https://httpbin.org/ip").json()
    return ip


def to_df(
    data,
    index: list | None = None,
    columns: list | None = None,
    dtype: dict | None = None,
    copy: bool = False,
):
    """
    转换为 DataFrame
    """
    import pandas as pd

    return pd.DataFrame(
        data,
        index=index,
        columns=columns,
        dtype=dtype,
        copy=copy,
    )


def to_html(text: str, **kwargs):
    """
    将 markdown 转换为 html

    text: markdown 字符串
    """
    import markdown

    return markdown.markdown(text, **kwargs)


def to_excel(
    df,
    path: str,
    mode: str = "w",
    index: bool = False,
    engine: str = "xlsxwriter",
):
    """
    ## 导出 excel

    - df: dataframe 对象, 多个sheet可以通过字典传入, 键为sheet名称。`{"sheet_name1": df1, "sheet_name2": df2}`
    - path: 文件保存路径
    - mode: 默认 `w` 为全新写入; 如果为 `a` 则为插入, 引擎会改为 openpyxl。
    - strings_to_urls: 默认不转换url
    - index: 默认不导出索引
    - engine: 默认引擎使用xlsxwriter, 其他选项有 'auto'、'openpyxl'、'odf'
    """
    import pandas as pd

    df: dict[str, pd.DataFrame] | pd.DataFrame

    if engine == "xlsxwriter":
        engine_kwargs = {"options": {"strings_to_urls": False}}

    if mode == "a":
        engine = "openpyxl"
        engine_kwargs = None

    with pd.ExcelWriter(
        path,
        engine=engine,  # type: ignore
        mode=mode,  # type: ignore
        engine_kwargs=engine_kwargs,
    ) as writer:
        if isinstance(df, dict):
            for sheet in df:
                df.get(sheet).to_excel(
                    writer,
                    index=index,
                    sheet_name=sheet,
                )
        else:
            df.to_excel(writer, index=index)


def retry(
    nums: int = 3,
    log: bool = False,
    exception: bool = False,
    show_error: bool = False,
):
    """
    ## 重试

    - nums: 默认重试 3 次。
    - log: 日志, 开启后会打印详细的错误日志。
    - exception: print_exception 错误信息, 比 log 更直观, 默认不使用。
    - show_error: 抛出错误, 线程池建议打开该选项, 可以更好的统计运行情况。

    ```python
    import jsz

    @jsz.retry(5, log=True)
    def craw():
        url = "https://www.google.com"
        res = jsz.httpx.get(url, timeout=2)
        print(res)

    craw()
    ```
    """
    from functools import wraps

    def wrap(f):
        @wraps(f)
        def func(*args, **kwargs):
            for num in range(nums):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if log:
                        logger.exception(
                            f"函数 {f.__name__} | 第 {num + 1}/{nums} 次运行失败: {e}"
                        )
                    if exception:
                        print_exception()
                    if show_error:
                        raise e

        return func

    return wrap


def send_bot(
    content: str = "测试",
    bot_key: str = "",
    msgtype: str = "markdown",
    filepath: str | None = None,
    mentioned_list: list = [],
):
    """
    企业微信群机器人, 基础的 Mardkown 语法。

    <font color="info">绿色</font>
    <font color="comment">灰色</font>
    <font color="warning">橙红色</font>

    content: 文本
    bot_key: 微信机器人key, 也可以设置环境变量 BOT_KEY 自动读取, 参数权重高于环境变量。
    msgtype: 类型, 包括 markdown, text, file, voice, image
    filepath: 文件路径，非文本类型使用。
    mentioned_list: 提醒用户列表, 填入手机号或 "@all", 仅支持 text 类型。
    """
    import httpx

    if msgtype not in ["markdown", "text", "file", "voice", "image"]:
        raise NameError('类型仅支持 "markdown", "text", "file", "voice", "image"')
    if not bot_key:
        bot_key = os.getenv("BOT_KEY", "")
        if not bot_key:
            print("[red]未全局配置 BOT_KEY，也未填写参数 bot_key[/]")
            raise Exception("请填写 bot_key")
    if "key=" in bot_key:
        raise Exception("bot_key 只需要填入 `key=` 后面的部分")
    if mentioned_list:
        msgtype = "text"
    if msgtype == "file" or msgtype == "voice":
        file_upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={bot_key}&type=file"
        files = {filepath.rsplit(".", 1)[0]: open(filepath, "rb")}  # type: ignore
        resp = httpx.post(file_upload_url, files=files)
        msg = {"media_id": resp.json().get("media_id")}
    elif msgtype == "image":
        content = open(filepath, "rb").read()  # type: ignore
        msg = {"base64": base64_encode(content), "md5": md5(content)}
    elif msgtype == "text":
        msg = {"content": content, "mentioned_mobile_list": mentioned_list}
    else:
        msg = {"content": content}
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"
    json_data = {
        "msgtype": msgtype,
        msgtype: msg,
    }
    response = httpx.post(url, json=json_data)
    return response


def pdf2text(filepath):
    """
    从 pdf 提取文本内容

    filepath: 文件路径
    """
    from pypdf import PdfReader

    reader = PdfReader(filepath)
    content = "".join([i.extract_text() for i in reader.pages])
    return content


def timeit(function):
    """
    计时器

    ```
    @timeit
    def hello():
        time.sleep(5)
    ```
    """
    from functools import wraps

    @wraps(function)
    def func(*args, **kwargs):
        t0 = time.time() * 1000
        result = function(*args, **kwargs)
        print(f"运行 {function.__name__} 耗时: {time.time() * 1000 - t0:.2f} ms")
        return result

    return func


def ua(version_from=101, version_to=129):
    """
    随机ua

    chrome 版本大于101
    """
    ua_list = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(version_from, version_to)}.0) Gecko/20100101 Firefox/{random.randint(version_from, version_to)}.0",
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(version_from, version_to)}.0.0.0 Safari/537.36 Edg/{random.randint(version_from, version_to)}.0.0.0",
    ]

    return {
        "connection": "close",
        "user-agent": random.choice(ua_list),
    }


def wait(n: int = 0, log: bool = False):
    """
    后台运行, 异步不阻塞。

    n: 等待秒数
    log: 启动后打印日志。

    @wait(2)
    def hello():
        print('运行完毕')
    """
    from threading import Timer
    from functools import wraps

    def wrap(f):
        @wraps(f)
        def func(*args, **kwargs):
            if log:
                logger.info(f"{f.__name__} 函数将于 {n} 秒后运行")
            t = Timer(n, f, args=args, kwargs=kwargs)
            t.start()

        return func

    return wrap


def ddddocr(
    img,
    png_fix: bool = False,
    old: bool = False,
    new: bool = False,
    use_gpu: bool = False,
    onnx_path: str = "",
    charsets_path: str = "",
):
    """
    ## 使用ddddocr识别验证码

    img: 图片对象，支持传入文件路径
    png_fix: 是否修复图片，修复后支持黑色透明图片
    old: 老模型
    new: 新模型
    use_gpu: 使用GPU
    onnx_path: onnx 模型路径
    charsets_path: 字符集路径
    """
    try:
        import ddddocr
    except Exception:
        print("[red]请先安装 ddddocr, 否则无法使用[/]")
        return

    if os.path.exists(img):
        img = open(img, "rb").read()
    d = ddddocr.DdddOcr(
        show_ad=0,
        old=old,
        beta=new,
        use_gpu=use_gpu,
        import_onnx_path=onnx_path,
        charsets_path=charsets_path,
    )
    return d.classification(img=img, png_fix=png_fix)


def win11toast(
    message="",
    app_id="通知",
    duration="short",
    icon_path="",
):
    """
    Windows 通知

    message: 通知内容, 最多5行, 尽量精简内容
    app_id: 应用ID，可以作为标题
    duration: 通知时间长度, 可以设置 short 和 long
    icon_path: 文本左侧图片
    """
    if sys.platform != "win32":
        print("[red]win11toast 只支持 Windows 系统[/]")
        return
    import winsdk.windows.ui.notifications as notifications
    import winsdk.windows.data.xml.dom as dom

    toast_xml = f"""
    <toast activationType="protocol" launch="" scenario="default" duration="{duration}">
        <visual>
            <binding template="ToastGeneric">
                <image placement="appLogoOverride" src="{icon_path}" />
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
    """
    xml_doc = dom.XmlDocument()
    xml_doc.load_xml(toast_xml)
    toast = notifications.ToastNotification(xml_doc)
    notifier = notifications.ToastNotificationManager.create_toast_notifier(app_id)
    notifier.show(toast)


def run_process(
    command: str,
    n: int = 1,
    stdout: bool = False,
):
    """
    ## 多个进程运行程序
    脚本中可以使用 getpid() 获取进程号, gettid() 获取线程号, 使用 python 建议使用 sys.executable

    command: 命令, 字符串
    n: 并发运行的实例数量
    stdout: 默认不输出, True 输出
    """
    import subprocess

    if stdout:
        return subprocess.getoutput(command)

    processes = []

    for _ in range(n):
        process = subprocess.Popen(
            command,
            shell=True if isinstance(command, str) else False,
        )
        processes.append(process)

    # 等待所有进程完成
    for process in processes:
        process.wait()


def run_nohup(command: str, *args, **kwargs):
    """
    后台运行命令
    """
    import subprocess

    process = subprocess.Popen(
        command,
        shell=True if isinstance(command, str) else False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        *args,
        **kwargs,
    )
    return process


def to_gzip(input_path, dir_format="gztar"):
    """
    压缩文件和目录

    input_path: 输入路径，文件路径或目录
    dir_format: 压缩目录格式, 支持 "zip", "tar", "gztar", "bztar", or "xztar"
    """
    import os
    import gzip
    import shutil

    if os.path.isfile(input_path):
        with (
            open(input_path, "rb") as f_in,
            gzip.open(f"{input_path}.gz", "wb") as f_out,
        ):
            shutil.copyfileobj(f_in, f_out)
        print(f"文件 {input_path} 成功压缩为 {input_path}.gz")
    elif os.path.isdir(input_path):
        output_path = shutil.make_archive(
            f"{input_path.replace('/', '')}",
            dir_format,
            input_path,
        )
        print(f"目录 {input_path} 成功压缩为 {output_path}")
    else:
        print(f"提供的路径 ({input_path}) 无效.")
