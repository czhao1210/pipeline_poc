# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import pytest

from dtaf_core.lib.artifactory_lib import upload, download


@pytest.mark.soundwave1
class TestSuites(object):

    def setup_class(self):
        self.username = 'sys_cluster'
        self.password = '0okm9ijn*UHB&YGV'

    def test_download(self):
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/AAAtest1/"
        dest = 'testdir'
        download(url=url, username=self.username, password=self.password, dest=dest)
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/sutagent/1.15.0/sutagent-1.15.0-py2.py3-none-any.whl"
        dest = 'testfile'
        download(url=url, username=self.username, password=self.password, dest=dest)
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/AAAtest1/"
        download(url=url, username=self.username, password=self.password)
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/sutagent/1.15.0/sutagent-1.15.0-py2.py3-none-any.whl"
        download(url=url, username=self.username, password=self.password)

    def test_upload(self):
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/AAAtest2/"
        source = './testdir'
        upload(source=source, url=url, username=self.username, password=self.password, props={'a': '1', 'b': '3333'})
        url = "https://af01p-png.devtools.intel.com/artifactory/dtaf-framework-release-png-local/logs/AAAtest2/"
        source = './testfile'
        upload(source=source, url=url, username=self.username, password=self.password, props={'a': '1', 'b': '4444'})
