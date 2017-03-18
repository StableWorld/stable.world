import platform
__all__ = ['JSONDecodeError', 'platform_uname', 'ConfigParser', 'ConfigParserError', 'urlparse']

PY3 = platform.python_version_tuple()[0] == '3'
PY2 = not PY3

if PY3:
    from json.decoder import JSONDecodeError
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError
    from urllib.parse import urlparse
else:  # PY2
    from collections import namedtuple
    JSONDecodeError = ValueError
    uname_result = namedtuple(
        'uname_result',
        ['system', 'node', 'release', 'version', 'machine', 'processor']
    )

    from ConfigParser import ConfigParser
    from ConfigParser import Error as ConfigParserError
    ConfigParser.read_file = ConfigParser.readfp
    from urlparse import urlparse


def platform_uname():
    if PY3:
        return platform.uname()
    else:  # PY2
        return uname_result(*platform.uname())
