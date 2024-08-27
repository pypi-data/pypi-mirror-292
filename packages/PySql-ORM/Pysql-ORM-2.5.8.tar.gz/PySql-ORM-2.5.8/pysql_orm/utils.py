import json
import uuid
import time
import random
import string
from pprint import pformat
from datetime import datetime, timedelta, timezone

# from dateutil.parser import parse as parse_datestr
TZ_UTC = timezone.utc
TZ_LOCAL = timezone(timedelta(seconds=-time.timezone))

AutoStringMapping = {
    "true": True,
    "True": True,
    "False": False,
    "false": False,
    "null": None,
    "None": None,
    "Nan": None,
    "undefined": None,
    "0.0": 0,
    "0.00": 0,
    "-1": -1,
}

safe_lowercase = 'abcdefghjkmnpqrstuvwxyz'  ##; noqa! ignore "iol"
safe_uppercase = safe_lowercase.upper()     ##; noqa! better readable
safe_quote_chars = string.ascii_letters + string.digits + "-_.~"
SafeQuoteCharSet = set(safe_quote_chars + "%")


def now(tz=None, use_utc=False):
    """
    ##;@ZH: 使用datetime.now, 使得到的日期, 不管时间区是多少, 时间戳都是一致的.
    @return: <datetime> with timezone
    ;return.timestamp() 
    ;    == datetime.utcnow().replace(tz_info=TZ_UTC).timestamp() 
    ;    == datetime.now(tz_info=TZ_LOCAL).timestamp()
    """
    if not tz:
        if use_utc:
            tz = TZ_UTC
        else:
            tz = TZ_LOCAL
    return datetime.now(tz=tz)


NowStr = lambda fmt="%Y-%m-%d_%H%M", use_utc=False: now(use_utc=use_utc).strftime(fmt)


def ts_rnd_key(size=4, fmt="%-y%m%d%H%M%S"):
    ts = datetime.now().strftime(fmt)
    rnd = ''.join(random.choice(safe_uppercase) for i in range(size))
    return f'{ts}{rnd}'
