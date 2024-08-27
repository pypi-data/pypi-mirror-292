import sys
import time

PY2 = sys.version_info[0] == 2
IS_PY2 = PY2
IS_PY3 = sys.version_info[0] >= 3

##; Scope the session to the current greenlet if greenlet is available,
##; otherwise fall back to the current thread.
if IS_PY3:
    try:
        from greenlet import getcurrent as _ident_func
    except ImportError:
        from threading import get_ident as _ident_func
else:
    ##; Python2
    from thread import get_ident as _ident_func


##; the best timer function for the platform
if sys.platform == 'win32':
    if sys.version_info >= (3, 3):
        _timer = time.perf_counter
    else:
        _timer = time.clock
else:
    _timer = time.time

##; iterfuncs    
if PY2:
    def iteritems(d):
        return d.iteritems()


    def itervalues(d):
        return d.itervalues()


    xrange = xrange

    string_types = (unicode, bytes)


    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, unicode):
            return x.encode(charset, errors)

        return str(x)

else:
    def iteritems(d):
        return iter(d.items())


    def itervalues(d):
        return iter(d.values())


    xrange = range

    string_types = (str,)


    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, bytes):
            return x.decode(charset, errors)

        return str(x)


