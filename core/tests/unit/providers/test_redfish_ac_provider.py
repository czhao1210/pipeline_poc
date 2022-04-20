#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################

# Global imports
from __future__ import absolute_import

import six

if six.PY2:
    import mock
if six.PY3 or six.PY34:
    from unittest import mock

from argparse import Namespace

from dtaf_core.providers.internal.redfish_ac_provider import RedfishAcProvider


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


log = _Log()
cfg_opts = None


def return_mock(return_value):
    def return_func(*args, **kwargs):
        return return_value

    return return_func


class TestBaseBiosXmlCliProvider(object):
    mock_ssh_driver_config = Namespace(ip="0.0.0.0", user="mock", password="mock", sutospath="mock",
                                       bios_cfgfilepath="dtaf_core/tests/unit/data/",
                                       bios_cfgfilename="test_xmlcli.txt", root_privilege="mock")
    mock_config = Namespace(driver_cfg=mock_ssh_driver_config)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_ac_power_off(mock_pcf, mock_exc, mock_get, mock_sections, mock_read):
        from dtaf_core.providers.internal.redfish_ac_provider import ConfigurationHelper
        ConfigurationHelper = mock.Mock()
        obj = RedfishAcProvider(cfg_opts, log)
        try:
            obj.ac_power_off(10)
        except:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_get_ac_power_state(mock_pcf, mock_exc, mock_get, mock_sections, mock_read):
        from dtaf_core.providers.internal.redfish_ac_provider import ConfigurationHelper
        ConfigurationHelper = mock.Mock()
        obj = RedfishAcProvider(cfg_opts, log)
        try:
            obj.get_ac_power_state()
        except:
            return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_error(mock_pcf, mock_exc, mock_get, mock_sections, mock_read):
        obj = RedfishAcProvider(cfg_opts, log)
        try:
            obj.set_username_password()
        except NotImplementedError:
            pass
        try:
            obj.reset_username_password()
        except NotImplementedError:
            return
