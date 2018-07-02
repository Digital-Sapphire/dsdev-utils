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
import os
import re
import sys

from dsdev_utils.exceptions import VersionError

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


# -*- coding: UTF-8 -*-
"""
Purpose:


"""
import os, re
from jetCore.exceptions import VersionError

# Normalizes version strings of different types. Examples
# include 1.2, 1.2.1, 1.2b and 1.1.1b
#
# Args:
#
#     version (str): Version number to normalizes
class Version(object):
    channels = {'d': ('daily', 0), 'a': ('alpha', 1), 'b': ('beta', 2),
                 'p': ('patch', 3), 'm': ('mandatory', 4), 'f': ('feature', 4),
                 None: ('stable', 9), '': ('stable', 9)}

    def __init__(self, version):
<<<<<<< HEAD
        self._version = None
        self._channelID = None
        self.major = None
        self.minor = None
        self.release = None
        self.preRelease = None
        self.build = None
        self.revision = None
        self.version = version
        self.version_tuple = (self.major, self.minor, self.release, self.revision, self.channelNum)

    @property
    def version(self):
        return self._version
    @version.setter
    def version(self, value):
        if value is None:
            self.major = 0
            self.minor = 0
            self.release = 0
            self.revision = 0
        else:
            self._parse_version_str(value)
        self._version = '{}.{}.{}'.format(self.major, self.minor, self.release)
        if self.preRelease:
            self._version = '{}-{}'.format(self._version, self.preRelease)
        if self.build:
            self._version = '{}-{}'.format(self._version, self.build)
        return

    @property
    def channelNum(self):
        if not self._channelID or self._channelID not in self.channels:
            return self.channels[None][1]
        return self.channels[self._channelID][1]

    @property
    def channel(self):
        if not self._channelID or self._channelID not in self.channels:
            return self.channels[None][0]
        return self.channels[self._channelID][0]
    @channel.setter
    def channel(self, value):
        if value is None:
            self._channelID = None
            return
        self._channelID = value[:1]
        return
=======
        self.original_version = version
        self._parse_version_str(version)
        self.version_str = None
>>>>>>> f94e7d27e0ace6f4b48ef053d7705ff5bdc10d40

    def _parse_version_str(self, version):

        ext = os.path.splitext(version)[1]
        if ext == '.zip':
            version = version[:-4]
        elif ext == '.gz':
            version = version[:-7]

        try:
            _version_data = self._parse_version(version)
            self.major = int(_version_data.get('MAJOR', 0))
            self.minor = int(_version_data.get('MINOR', 0))
            self.release = int(_version_data.get('RELEASE', 0) or 0)
            self.preRelease = _version_data.get('prerelease')
            self.build = _version_data.get('build', None)

            if self.preRelease:
                _pre_data = self._parse_prerelease(self.preRelease)
                self.revision = int(_pre_data.get('revision', 0) or 0)
                if _pre_data.get('subrevision'):
                    self.revision = float('.'.join([str(self.revision), _pre_data.get('subrevision')]))
                self.channel = _pre_data.get('channel') or _pre_data.get('name', None)
            else:
                self.revision = 0
                self.channel = None
        except AssertionError:
            raise VersionError('Cannot parse version')

<<<<<<< HEAD
=======
        self.major = int(version_data.get('major', 0))
        self.minor = int(version_data.get('minor', 0))
        patch = version_data.get('patch')
        if patch is None:
            self.patch = 0
        else:
            self.patch = int(patch)
        release = version_data.get('release')
        self.channel = 'stable'
        if release is None:
            self.release = 2
        # Convert to number for easy comparison and sorting
        elif release in ['b', 'beta', '1']:
            self.release = 1
            self.channel = 'beta'
        elif release in ['a', 'alpha', '0']:
            self.release = 0
            self.channel = 'alpha'
        else:
            log.debug('Setting release as stable. '
                      'Disregard if not prerelease')
            # Marking release as stable
            self.release = 2

        release_version = version_data.get('releaseversion')
        if release_version is None:
            self.release_version = 0
        else:
            self.release_version = int(release_version)
        self.version_tuple = (self.major, self.minor, self.patch,
                              self.release, self.release_version)
        self.version_str = str(self.version_tuple)

>>>>>>> f94e7d27e0ace6f4b48ef053d7705ff5bdc10d40
    def _parse_version(self, version):
        v_re = re.compile(r"(?P<MAJOR>0|(?:[1-9]\d*))"
                          r"\.(?P<MINOR>0|(?:[1-9]\d*))"
                          r"(?:\.(?P<RELEASE>0|(?:[1-9]\d*)))?"
                          r"(?:-?(?P<prerelease>(?:0|(?:[1-9A-Za-z-][0-9A-Za-z-]*))(?:\.(?:0|(?:[1-9A-Za-z-][0-9A-Za-z-]*)))*))?"
                          r"(?:\+(?P<build>(?:0|(?:[1-9A-Za-z-][0-9A-Za-z-]*))(?:\.(?:0|(?:[1-9A-Za-z-][0-9A-Za-z-]*)))*))?",
                          re.IGNORECASE | re.VERBOSE)

        r = v_re.search(version)
        assert r is not None
        return r.groupdict()

    def _parse_prerelease(self, prerelease):
        pre_re = re.compile(r"^(?P<name>[a-zA-Z]+)?\.?(?P<revision>\d+)?(?:\.(?P<subrevision>\d+(?:\.?\d)*))?(?:\.?(?P<channel>[a-z]+))?$",
                          re.IGNORECASE | re.VERBOSE)

        r = pre_re.match(prerelease)
        assert r is not None
        return r.groupdict()

    def longname(self):
        return "Major: {major} Minor: {minor} Release: {release} Revision: {revision} Channel: {channelName} Build {build}".format(**self.__dict__)

    def __str__(self):
        return self._version

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self._version)

    def __hash__(self):
        return hash(self.version_tuple)

    def __eq__(self, obj):
        return self.version_tuple == obj.version_tuple

    def __ne__(self, obj):
        return self.version_tuple != obj.version_tuple

    def __lt__(self, obj):
        return self.version_tuple < obj.version_tuple

    def __gt__(self, obj):
        return self.version_tuple > obj.version_tuple

    def __le__(self, obj):
        return self.version_tuple <= obj.version_tuple

    def __ge__(self, obj):
        return self.version_tuple >= obj.version_tuple

if __name__ == '__main__':
    ver = Version('0.0.1710a')
    print ver.longname()
    print Version('0.0.1710-50a').longname()
    print Version('0.0.1710-50.1a').longname()
    print Version('0.0.1710-50a+abcdef').longname()
    print Version('0.0.1710-50.2a+abcdef').longname()
    print Version('0.0.1710a+abcdef').longname()


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
