import re

try:
    # Python 3
    from urllib.parse import quote
except ImportError:
    # Python 2
    from urllib import quote


def normalize_host(host):
    host = host[:-1] if host[-1:] == "/" else host
    return re.sub(r"/(^\w+:|^)\/\//", "", host)


def sanitize_tableau_string(str_data):
    str_data = re.sub(r"&quot;", "", str_data)
    return re.sub(r'/[\'"]+/g', "", str_data)


def sanitize_string(fqdn):
    return quote(fqdn)


def sanitize_fully_qualified_object_name(fqn):
    return str(sanitize_string(fqn if isinstance(fqn, str) else "")).lower()
