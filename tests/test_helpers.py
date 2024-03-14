# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014-2021 Digital Sapphire
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
# ------------------------------------------------------------------------------
import logging

from dsdev_utils.exceptions import VersionError
from dsdev_utils.helpers import EasyAccessDict, Version
import pytest

log = logging.getLogger()


class TestVersion(object):
    def test_depreciated(self):
        with pytest.warns(DeprecationWarning) as record:
            v = Version('1.2.3')
            v.v_re.search('1.2.3')
        assert len(record) == 1
        message = "Call to deprecated function (or staticmethod) v_re"
        assert record[0].message.args[0][0:len(message)] == message

        with pytest.warns(DeprecationWarning) as record:
            v = Version('1.2.3')
            v.v_re_big.search('1.2.3')
        assert len(record) == 1
        message = "Call to deprecated function (or staticmethod) v_re_big"
        assert record[0].message.args[0][0:len(message)] == message

    def test_version_short(self):
        assert Version("1.1") > Version("1.1beta1")
        assert Version("1.2.1beta1") < Version("1.2.1")
        assert Version("1.2.1alpha1") < Version("1.2.1alpha2")

    def test_version_full(self):
        assert Version("1.1") > Version("1.1b1")
        assert Version("1.2.1b1") < Version("1.2.1")
        assert Version("1.2.1a1") < Version("1.2.1a2")

    def test_version(self):
        assert Version("5.0") == Version("5.0")
        assert Version("4.5") != Version("5.1")

    def test_pep440(self):
        assert Version('0.1.1.dev5+a1b2c3d') > Version('0.1.1.dev4+a1b2c3d')
        assert Version('0.1.1.dev5+a1b2c3d') < Version('0.1.2.dev4+a1b2c3d')

    def test_version_original(self):
        assert Version('5.0').original_version == '5.0'

    def test_version_release(self):
        assert Version('5.0').release == 2
        assert Version('5.0.0a').release == 0
        assert Version('5.0.0b').release == 1
        assert Version('5.1.2.dev4+a1b2c3d').release == 3

    def test_version_major(self):
        assert Version('5.0').major == 5
        assert Version('5.0').major != 1
        assert Version('5.0').major != '5'
        assert Version('9999.5234.123').major == 9999
        assert Version('7.1.2.dev4+a1b2c3d').major == 7

    def test_version_minor(self):
        assert Version('5.3').minor == 3
        assert Version('5.3').minor != '3'
        assert Version('5.3').minor != 0
        assert Version('2021.987654321.123').minor == 987654321
        assert Version('2.8.2.alpha4+a1b2c3d').minor == 8

    def test_version_tuple(self):
        assert Version('1.2').version_tuple == (1,2,0,2,0)
        assert Version('1.2.0a').version_tuple == (1,2,0,0,0)
        assert Version('1.2.0b').version_tuple == (1,2,0,1,0)
        assert Version('1.2.1').version_tuple == (1,2,1,2,0)
        assert Version('1.2.1-9').version_tuple == (1,2,1,2,9)
        assert Version('1.2.1-a7').version_tuple == (1,2,1,0,7)
        assert Version('5.4.3.dev4+a1b2c3d').version_tuple == (5,4,3,3,4)

    def test_version_channel(self):
        assert Version('2.2').channel == 'stable'
        assert Version('2.2.1').channel == 'stable'
        assert Version('3.2.1a').channel == 'alpha'
        assert Version('3.2.1alpha').channel == 'alpha'
        assert Version('3.2.1b').channel == 'beta'
        assert Version('4.3.2beta').channel == 'beta'
        assert Version('4.3.2-b1').channel == 'beta'
        assert Version('5.1.2.dev4+a1b2c3d').channel == 'dev'

    def test_version_micro(self):
        assert Version('6.5.4').patch == 4
        assert Version('6.5.4').patch != '4'
        assert Version('6.5.0').patch == 0
        assert Version('6.5.0').patch != None
        assert Version('6.5.1a').patch == 1
        assert Version('6.5.0').patch != '1'
        assert Version('2021.5234.123').patch == 123
        assert Version('7.8.9.dev4+a1b2c3d').patch == 9

    def test_version_release_version(self):
        assert Version('2021.02.22').release_version == 0
        assert Version('2021.02.22').release_version != None
        assert Version('10.0.1-b1').release_version == 1
        assert Version('10.0.1-1').release_version != '1'
        assert Version('10.0.1-b123').release_version == 123
        assert Version('5.1.2.dev999+a1b2c3d').release_version == 999

    def test_version_string(self):
        assert Version('1.2.3').version_str == '(1, 2, 3, 2, 0)'


class TestEasyAccessDict(object):
    def test_easy_access(self):
        key = "carson*da*park"
        data = {"carson": {"da": {"park": "mills"}}}
        easy_data = EasyAccessDict(data)
        assert "mills" == easy_data.get(key)
