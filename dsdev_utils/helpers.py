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
import sys

from jetCore.version import Version
from jetCore.exceptions import VersionError

log = logging.getLogger(__name__)


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
