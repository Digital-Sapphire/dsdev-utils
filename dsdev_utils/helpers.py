# --------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014-2016 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# --------------------------------------------------------------------------
import io
import gzip
import logging
import re
import sys
from pathlib2 import Path
from collections import OrderedDict

log = logging.getLogger(__name__)

channels = OrderedDict()
channels['daily'] = 0
channels['alpha'] = 1
channels['beta'] = 2
channels['patch'] = 3
channels['feature'] = 4
channels['mandatory'] = 5
channels['stable'] = 9
channel_id = {x[:1]: x for x in channels.keys()}


class Version(object):

    def __init__(self, version=None):
        self.pgm_name = None
        self.major = None
        self.minor = None
        self.patch = None
        self.channel_name = None
        self.SHA = None
        if version:
            self.version = version
        return

    @property
    def version(self):
        _version = '{}'.format(self.major)
        if self.patch:
            _version = '{}.{}.{}{}'.format(_version, self.minor, self.patch, self.channel[:1])
        elif self.minor:
            _version = '{}.{}{}'.format(_version, self.minor, self.channel[:1])
        return _version

    @version.setter
    def version(self, value):
        if value is None:
            self.major = 0
            self.minor = 0
            self.patch = None
            self.channel_name = 'daily'
            return
        self._parse_string(value)
        return

    @property
    def version_tuple(self):
        return (self.major, self.minor, self.patch, channels[self.channel])

    @property
    def build_id(self):
        if self.SHA is not None:
            return '{}+{}'.format(self.version, self.SHA)
        return self.version

    @property
    def channel(self):
        return self.channel_name or 'stable'

    @channel.setter
    def channel(self, value):
        if value is None:
            self.channel_name = None
            return
        if value[:1].lower() in channel_id:
            self.channel_name = channel_id[value[:1].lower()]
        else:
            self.channel_name = 'stable'
        return

    @property
    def channel_id(self):
        return self.channel[:1]

    @channel_id.setter
    def channel_id(self, value):
        self.channel = value
        return

    @property
    def channel_number(self):
        if not self.channel_name:
            return channels['stable']
        return channels[self.channel_name]

    def _parse_string(self, version):
        version = Path(version).stem
        try:
            _data = self._parse_version(version)
            self.major = int(_data.get('MAJOR', 0) or 0)
            self.minor = _data.get('MINOR', None)
            self.patch = _data.get('PATCH', None)
            self.channel = _data.get('CHANNEL', None)
            self.pgm_name = _data.get('NAME', None)
            self.SHA = _data.get('SHA', None)
            if self.minor is not None:
                self.minor = int(self.minor)
            if self.patch is not None:
                self.patch = int(self.patch)
        except AssertionError:
            log.error('Version: Cannot parse version string: {}'.format(version))
            self.major = 0
            self.minor = 0
            self.patch = None
            self.channel_name = 'daily'
        return

    def _parse_version(self, version):
        v_re = re.compile(r"((?P<NAME>jetPy|jetRun)-win-)?"
                          r"(?:[1-9]\.)?"
                          r"(?:[1-9]\.)?"
                          r"(?:(?P<MAJOR>(?:[0-9][0-9]\d\d)))"
                          r"(?:[.|-](?P<MINOR>0|(?:[1-9]\d*)))?"
                          r"(?:.(?P<PATCH>(?:0|(?:[1-9][0-9]*))))?"
                          r"(?P<CHANNEL>(?:0|(?:[A-Za-z-]*)))?"
                          r"(?:\+(?P<SHA>(?:0|(?:[1-9A-Za-z-][0-9A-Za-z-]*.*))))?",
                          re.IGNORECASE | re.VERBOSE)
        r = v_re.search(version)
        assert r is not None
        return r.groupdict()

    def longname(self):
        return "Monthly Release: {major} Minor: {minor} Patch: {patch} Channel: {channel_name}".format(**self.__dict__)

    def __str__(self):
        return self.version

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.version)

    def __hash__(self):
        return hash(self.version_tuple)

    def __eq__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) == str(obj)
        return self.version_tuple == obj.version_tuple

    def __ne__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) != str(obj)
        return self.version_tuple != obj.version_tuple

    def __lt__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) < str(obj)
        return self.version_tuple < obj.version_tuple

    def __gt__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) > str(obj)
        return self.version_tuple > obj.version_tuple

    def __le__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) <= str(obj)
        return self.version_tuple <= obj.version_tuple

    def __ge__(self, obj):
        if not hasattr(obj, 'version_tuple'):
            return str(self) >= str(obj)
        return self.version_tuple >= obj.version_tuple


class VersionError(Exception):
    """Raised when an Invalid Version Number is supplied
    """
    pass



# Decompress gzip data
#
#   Args:
#
#       data (str): Gzip data
#
#
#   Returns:
#
#       (data): Decompressed data
def gzip_decompress(data):
    # if isinstance(data, six.binary_type):
    #     data = data.decode()
    compressed_file = io.BytesIO()
    compressed_file.write(data)
    #
    # Set the file's current position to the beginning
    # of the file so that gzip.GzipFile can read
    # its contents from the top.
    #
    compressed_file.seek(0)
    decompressed_file = gzip.GzipFile(fileobj=compressed_file, mode='rb')
    data = decompressed_file.read()
    compressed_file.close()
    decompressed_file.close()
    return data


def lazy_import(func):
    """Decorator for declaring a lazy import.

    This decorator turns a function into an object that will act as a lazy
    importer.  Whenever the object's attributes are accessed, the function
    is called and its return value used in place of the object.  So you
    can declare lazy imports like this:

        @lazy_import
        def socket():
            import socket
            return socket

    The name "socket" will then be bound to a transparent object proxy which
    will import the socket module upon first use.

    The syntax here is slightly more verbose than other lazy import recipes,
    but it's designed not to hide the actual "import" statements from tools
    like pyinstaller or grep.
    """
    try:
        f = sys._getframe(1)
    except Exception:  # pragma: no cover
        namespace = None
    else:
        namespace = f.f_locals
    return _LazyImport(func.__name__, func, namespace)


class _LazyImport(object):
    """Class representing a lazy import."""

    def __init__(self, name, loader, namespace=None):
        self._dsdev_lazy_target = _LazyImport
        self._dsdev_lazy_name = name
        self._dsdev_lazy_loader = loader
        self._dsdev_lazy_namespace = namespace

    def _dsdev_lazy_load(self):
        if self._dsdev_lazy_target is _LazyImport:
            self._dsdev_lazy_target = self._dsdev_lazy_loader()
            ns = self._dsdev_lazy_namespace
            if ns is not None:
                try:
                    if ns[self._dsdev_lazy_name] is self:
                        ns[self._dsdev_lazy_name] = self._dsdev_lazy_target
                except KeyError:  # pragma: no cover
                    pass

    def __getattribute__(self, attr):  # pragma: no cover
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if self._dsdev_lazy_target is _LazyImport:
                self._dsdev_lazy_load()
            return getattr(self._dsdev_lazy_target, attr)

    def __nonzero__(self):  # pragma: no cover
        if self._dsdev_lazy_target is _LazyImport:
            self._dsdev_lazy_load()
        return bool(self._dsdev_lazy_target)

    def __str__(self):  # pragma: no cover
        return '_LazyImport: {}'.format(self._dsdev_lazy_name)


# Provides access to dict by pass a specially made key to
# the get method. Default key sep is "*". Example key would be
# updates*mac*1.7.0 would access {"updates":{"mac":{"1.7.0": "hi there"}}}
# and return "hi there"
#
# Kwargs:
#
#     dict_ (dict): Dict you would like easy asses to.
#
#     sep (str): Used as a delimiter between keys
class EasyAccessDict(object):

    def __init__(self, dict_=None, sep='*'):
        self.sep = sep
        if not isinstance(dict_, dict):
            self.dict = {}
        else:
            self.dict = dict_

    # Retrive value from internal dict.
    #
    # args:
    #
    #     key (str): Key to access value
    #
    # Returns:
    #
    #     (object): Value of key if found or None
    def get(self, key):
        try:
            layers = key.split(self.sep)
            value = self.dict
            for key in layers:
                value = value[key]
            return value
        except KeyError:
            return None
        except Exception:  # pragma: no cover
            return None

    # Because I always forget call the get method
    def __call__(self, key):
        return self.get(key)

    def __str__(self):
        return str(self.dict)
