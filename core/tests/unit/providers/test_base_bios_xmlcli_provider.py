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

import pytest
from argparse import Namespace

from dtaf_core.providers.internal.base_bios_xmlcli_provider import BaseBiosXmlCliProvider


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
    mock_ssh_driver_config = Namespace(ip="0.0.0.0", port="mock", user="mock", password="mock", sutospath="mock",
                                       bios_cfgfilepath="dtaf_core/tests/unit/data/",
                                       bios_cfgfilename="test_xmlcli.txt", root_privilege="mock", python_path="mock")
    mock_config = Namespace(driver_cfg=mock_ssh_driver_config)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,output,path,execute_return',
                             [('', '', False, "verification for Bios Knob set Failed", None, 'None'),
                              ('', '', False, "verification for Bios Knob set Failed", 'test/', 'None'),
                              ('', '', True, "verification for Bios Knob set Failed", 'test/',
                               'Path Is Set Properly'), ])
    def test_path_setter(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections,
                         execute_ret, return_v,
                         output, path, execute_return):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        obj = BaseBiosXmlCliProvider(cfg_opts, log)
        BaseBiosXmlCliProvider.execute = return_mock(execute_return)
        ret = obj.path_setter(path=path)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,root_privellage,execute_return',
                             [('', '', False, True, "None"),
                              ('', '', False, False, "None"),
                              ('', '', False, True, 'Bios Knob "Driver Strength" does not currently exist'),
                              ('', '', False, False, "Verify Fail: Knob = Driver Strength")
                              ])
    def test_write_bios_knob_value(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections,
                                   execute_ret, return_v, root_privellage, execute_return):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        obj = BaseBiosXmlCliProvider(cfg_opts, log)
        obj._root_privellage = root_privellage
        BaseBiosXmlCliProvider.execute = return_mock(execute_return)
        ret = obj.write_bios_knob_value(None)
        ret = obj.write_bios_knob_value("Driver Strength", None)
        assert ret[0] == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,root_privellage,execute_return',
                             [('', '', False, True, "None"),
                              ('', '', False, False, "None"),
                              ('', '', False, True, 'Bios Knob "Driver Strength" does not currently exist'),
                              ('', '', False, False, "Verify Fail: Knob = Driver Strength")
                              ])
    def test_set_bios_knobs_overloop(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections,
                                     execute_ret, return_v, root_privellage, execute_return):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        obj = BaseBiosXmlCliProvider(cfg_opts, log)
        obj._root_privellage = root_privellage
        BaseBiosXmlCliProvider.execute = return_mock(execute_return)
        ret = obj.set_bios_knobs("Driver Strength", "aaaa", overlap=True)
        assert ret[0] == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_write_bios_knob_value_exception(mock_pcf, mock_exc, mock_get, mock_sections, mock_read):
        with pytest.raises(Exception):
            ret = BaseBiosXmlCliProvider(cfg_opts, log).write_bios_knob_value('Driver Strength', '2')
            assert ret == (False, "Please give the proper input")

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,output', [('', '', False, "Given less number of inputs")])
    def test_set_bios_knobs_less_input(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections, execute_ret,
                                       return_v,
                                       output):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_knobs('')
        assert ret == (return_v, output)

    # set_bios_knobs
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,output',
                             [('Driver Strength', '', False, "Check Target Key Option Values Properly")])
    def test_set_bios_knobs_target_key_value(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections,
                                             execute_ret, return_v,
                                             output):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_knobs("Driver Strength", 2)
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,output',
                             [('', '', False, "Match Not Found In Any Sections")])
    def test_set_bios_knobs_match_not_found(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections,
                                            execute_ret, return_v,
                                            output):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_knobs("Driver Strength", None)
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('sections,execute_ret,return_v,output', [('Driver Strength',
                                                                       'The Knob Driver Strength was not changed to '
                                                                       'the value Drivename & verification failed',
                                                                       False, None)])
    def test_set_bios_knobs_verify_failed(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, sections, execute_ret,
                                          return_v,
                                          output):
        mock_sections.return_value = sections
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_knobs("Driver Strength", 0)
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_set_bios_knob_exception(mock_pcf, mock_exc, mock_get, mock_sections, mock_read):
        with pytest.raises(Exception):
            ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_knobs('Driver Strength', '2')
            assert ret == (False, "Please give the proper input")

    @staticmethod
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('inp,return_v,output',
                             [("Driver Strength','FPK Port 2'", None, ['passed'])])
    def test_execute(mock_pcf, inp, return_v, output):
        ret = BaseBiosXmlCliProvider(cfg_opts, log).execute(inp)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('inp,execute_ret,return_v,output',
                             [("Driver Strength','FPK Port 2'", 'Knob passed\n', True, ['passed'])])
    def test_read_bios_knobs(mock_pcf, mock_exc, inp, execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).read_bios_knobs(inp)
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('inp,execute_ret,return_v,output',
                             [("Driver Strength','FPK Port 2'", 'Knob failed\n', False, ['failed']),
                              ('', None, False, [])])
    def test_read_bios_knobs_false(mock_pcf, mock_exc, inp, execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).read_bios_knobs(inp)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute',
                return_value=None)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_read_bios_knobs_exception(mock_pcf, mock_exc):
        with pytest.raises(Exception):
            ret = BaseBiosXmlCliProvider(cfg_opts, log).read_bios_knobs("Driver Strength','FPK Port 2'")
            raise

    # get_knob_options
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.re.findall')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('inp,execute_ret,re_findall,return_v,output', [("Driver Strength','FPK Port 2'",
                                                                             "Current available values for the knob is 33 ohm,40 Ohm",
                                                                             [
                                                                                 "Current available values for the knob is 33 ohm,40 Ohm"],
                                                                             True,
                                                                             "Current available values for the knob is 33 ohm,40 Ohm"),
                                                                            ("Driver Strength','FPK Port 2'",
                                                                             'No output present', [], False, []),
                                                                            ("Driver Strength','FPK Port 2'",
                                                                             'No output present', [
                                                                                 "Current available values for the knob is 33 ohm,40 Ohm\n"],
                                                                             False, "Knob options not available")])
    def test_get_knob_options(mock_pcf, mock_findall, mock_exc, inp, execute_ret, re_findall, return_v, output):
        mock_exc.return_value = execute_ret
        mock_findall.return_value = re_findall
        obj = BaseBiosXmlCliProvider(cfg_opts, log)
        obj._root_privellage = True
        ret = obj.get_knob_options(inp)
        obj._root_privellage = False
        ret = obj.get_knob_options(inp)
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute',
                return_value=None)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_get_knob_options_exception(mock_pcf, mock_exc):
        with pytest.raises(Exception):
            ret = BaseBiosXmlCliProvider(cfg_opts, log).get_knob_options("Driver Strength','FPK Port 2'")
            raise AttributeError

    # default_bios_settings
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('execute_ret,return_v,output',
                             [("The Knob values were set to default", True, 'The Knob values were set to default'),
                              (None, False, 'Failure')])
    def test_default_bios_settings(mock_pcf, mock_exc, execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        ret = BaseBiosXmlCliProvider(cfg_opts, log).default_bios_settings()
        assert ret == (return_v, output)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute',
                return_value=None)
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    def test_get_bios_bootorder_exception(mock_pcf, mock_exc):
        with pytest.raises(Exception):
            ret = BaseBiosXmlCliProvider(cfg_opts, log).get_bios_bootorder()
            assert ret == False, Exception

    # set_bios_bootorder
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('target,index,section,execute_ret,return_v,output', [('linux', 1, '',
                                                                                   "BootOrder section is not present in the configuration file",
                                                                                   False,
                                                                                   "BootOrder section is not present in the configuration file"),
                                                                                  ('', 1, ['BootOrder'],
                                                                                   "Target linux or windows is not present in the configuration file",
                                                                                   False,
                                                                                   "Target linux or windows is not present in the configuration file")])
    def test_set_bios_bootorder_kwargs(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, target, index, section,
                                       execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_bootorder(Target=target, index=index)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('target,index,section,execute_ret,return_v,output', [('linux', 0, ['BootOrder'],
                                                                                   'Bios boot order not changed & failed',
                                                                                   False,
                                                                                   'Bios boot order not changed & failed'),
                                                                                  ('linux', 0, '',
                                                                                   "BootOrder section is not present in the configuration file",
                                                                                   False,
                                                                                   "BootOrder section is not present in the configuration file"),
                                                                                  ('', 0, ['BootOrder'],
                                                                                   "Target linux or windows is not present in the configuration file",
                                                                                   False,
                                                                                   "Target linux or windows is not present in the configuration file")])
    def test_set_bios_bootorder(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, target, index, section,
                                execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_bios_bootorder(target, index)
        assert ret == return_v

    # EFI_set_bios_bootorder
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('target,index,efi_command,section,execute_ret,return_v,output', [('linux', 0, 'reset',
                                                                                               ['BootOrder'],
                                                                                               'failure Bios boot order not changed & failed',
                                                                                               False,
                                                                                               'failure Bios boot order not changed & failed'),
                                                                                              ('linux', 0, 'reset', '',
                                                                                               "BootOrder section is not present in the configuration file",
                                                                                               False,
                                                                                               "BootOrder section is not present in the configuration file"),
                                                                                              ('', 0, 'reset',
                                                                                               ['BootOrder'],
                                                                                               "Target linux or windows is not present in the configuration file",
                                                                                               False,
                                                                                               "Target linux or windows is not present in the configuration file")])
    def test_EFI_set_bios_bootorder(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, target, index, efi_command,
                                    section, execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        ret = BaseBiosXmlCliProvider(cfg_opts, log).EFI_set_bios_bootorder(target, index, efi_command)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Drivename')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @pytest.mark.parametrize('target,index,efi_command,section,execute_ret,return_v,output', [('linux', 0, 'reset',
                                                                                               ['BootOrder'],
                                                                                               'Bios boot order got changed to something',
                                                                                               True,
                                                                                               'Bios boot order got changed to something')])
    def test_EFI_set_bios_bootorder_true(mock_pcf, mock_exc, mock_get, mock_sections, mock_read, target, index,
                                         efi_command, section, execute_ret, return_v, output):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        ret = BaseBiosXmlCliProvider(cfg_opts, log).EFI_set_bios_bootorder(target, index, efi_command)
        assert ret == (return_v, output)

    # set_auto_knobpath_knoboptions
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='mocking')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.get_knob_options')
    @pytest.mark.parametrize('modify_existingpath,knobnames,section,execute_ret,return_v',
                             [(False, '', '', '', True), (False, 'bios', 'bios', 'path is TPM Configuration', True)])
    def test_set_auto_knobpath_knoboptions(mock_get_knob, mock_pcf, mock_exc, mock_get, mock_sections, mock_read,
                                           modify_existingpath, knobnames, section, execute_ret, return_v):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        mock_get_knob.return_value = (False, 'Knob options not available')
        ret = BaseBiosXmlCliProvider(cfg_opts, log).set_auto_knobpath_knoboptions(modify_existingpath, knobnames)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Boot Manager')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.get_knob_options')
    @pytest.mark.parametrize('modify_existingpath,knobnames,section,execute_ret,return_v',
                             [(True, "Intel Advanced Menu", "Intel Advanced Menu", 'path is TPM Configuration', True)])
    def test_set_auto_knobpath_knoboptions_file_open_read(mock_get_knob, mock_pcf, mock_exc, mock_get, mock_sections,
                                                          mock_read, modify_existingpath, knobnames, section,
                                                          execute_ret, return_v):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        mock_get_knob.return_value = (True, "available values for the knob :Intel Advanced Menu")
        TEST_DATA = '[Intel Advanced Menu]\nBios_Path = "TPM Configuration"\nTarget = "Enable"\n"empty"'
        if six.PY2:
            with mock.patch('__builtin__.open', mock.mock_open(read_data=TEST_DATA)) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.set_auto_knobpath_knoboptions(modify_existingpath, knobnames)
        if six.PY3 or six.PY34:
            with mock.patch('builtins.open', mock.mock_open(read_data=TEST_DATA)) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.set_auto_knobpath_knoboptions(modify_existingpath, knobnames)
        assert ret == return_v

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='Boot Manager')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.get_knob_options')
    @pytest.mark.parametrize('modify_existingpath,knobnames,section,execute_ret,return_v',
                             [(False, 'Intel Advanced Menu', 'Boot Manager', 'path is mock', True)])
    def test_set_auto_knobpath_knoboptions_file_open_write(mock_get_knob, mock_pcf, mock_exc, mock_get, mock_sections,
                                                           mock_read, modify_existingpath, knobnames, section,
                                                           execute_ret, return_v):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        mock_get_knob.return_value = (True, "available values for the knob :/configuration")
        fake_file_path = "dtaf_core/tests/unit/data/test_xmlcli.txt"
        knobname = 'Intel Advanced Menu'
        path = 'path is mock'
        options = 'configuration'
        if six.PY2:
            with mock.patch('__builtin__.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                data.set_auto_knobpath_knoboptions(modify_existingpath, knobnames)
        if six.PY3 or six.PY34:
            with mock.patch('builtins.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                data.set_auto_knobpath_knoboptions(modify_existingpath, knobnames)

        m.assert_called_once_with("dtaf_core/tests/unit/data/test_xmlcli.txt", 'a')
        handle = m()
        handle.write.assert_any_call(r"[Intel Advanced Menu]")
        handle.write.assert_any_call('\n')
        handle.write.assert_any_call("Bios_Path = mock")
        handle.write.assert_any_call('\n')
        handle.write.assert_any_call('Target = /configuration')
        handle.write.assert_any_call("\n\n")

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.read',
                return_value=[''])
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.sections')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.ConfigParser.SafeConfigParser.get',
                return_value='mocking')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.get_knob_options')
    @pytest.mark.parametrize('modify_existingpath,knobnames,section,execute_ret,return_v',
                             [('test', '', '', '', False),
                              ('test', 'bios', 'bios', 'path is TPM Configuration', False)])
    def test_flash_ifwi_image(mock_get_knob, mock_pcf, mock_exc, mock_get, mock_sections, mock_read,
                              modify_existingpath, knobnames, section, execute_ret, return_v):
        mock_exc.return_value = execute_ret
        mock_sections.return_value = section
        mock_get_knob.return_value = (False, 'Knob options not available')
        ret = BaseBiosXmlCliProvider(cfg_opts, log).flash_ifwi_image(modify_existingpath, knobnames)
        assert ret == return_v

    # getall_knobspath_options
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.os.path.exists')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.os.remove', return_value=True)
    @pytest.mark.parametrize('ret_os_path,output', [(True, True)])
    def test_getall_knobspath_options_true(mock_remove, mock_os_path, mock_pcf, mock_exc, ret_os_path, output):
        mock_os_path.return_value = ret_os_path
        mock_exc.side_effect = [(0, ''), (
            '[WDT Enable]\nBios_Path = Intel Advance Menu,Overclocking Performance Menu, WDT Enable\nTarget = Disabled,Enabled'),
                                0]
        if six.PY2:
            with mock.patch('__builtin__.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.getall_knobspath_options()
        if six.PY3 or six.PY34:
            with mock.patch('builtins.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.getall_knobspath_options()

        m.assert_called_once_with("dtaf_core/tests/unit/data/test_xmlcli.txt", 'a+')
        handle = m()
        handle.write.assert_any_call(r'[WDT Enable]')
        handle.write.assert_any_call('\n')
        handle.write.assert_any_call("Bios_Path = Intel Advance Menu,Overclocking Performance Menu, WDT Enable")
        handle.write.assert_any_call('\n')
        handle.write.assert_any_call('Target = Disabled,Enabled')
        handle.write.assert_any_call("\n\n")
        assert ret == output

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.BaseBiosXmlCliProvider.execute')
    @mock.patch('dtaf_core.providers.base_provider.ProviderCfgFactory.create', return_value=mock_config)
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.os.path.exists')
    @mock.patch('dtaf_core.providers.internal.base_bios_xmlcli_provider.os.remove', return_value=True)
    @pytest.mark.parametrize('ret_os_path,output', [(False, False)])
    def test_getall_knobspath_options_false(mock_remove, mock_os_path, mock_pcf, mock_exc, ret_os_path, output):
        mock_os_path.return_value = ret_os_path
        mock_exc.side_effect = [(0, ''), (
            '[WDT Enable]\nBios_Path = Intel Advance Menu,Overclocking Performance Menu, WDT Enable\nTarget = Disabled,Enabled',
            1)]
        if six.PY2:
            with mock.patch('__builtin__.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.getall_knobspath_options()
        if six.PY3 or six.PY34:
            with mock.patch('builtins.open', mock.mock_open()) as m:
                data = BaseBiosXmlCliProvider(cfg_opts, log)
                ret = data.getall_knobspath_options()
        assert ret == output
