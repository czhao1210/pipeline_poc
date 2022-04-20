# coding:utf-8
# !/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""
import time
from xml.etree import ElementTree as ET

from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.providers.provider_factory import ProviderFactory


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


def test():
    tree = ET.ElementTree()
    tree.parse(r'C:\Python27\Lib\site-packages\dtaf_core\tests\system\data\com_simics_configuration.xml')
    root = tree.getroot()
    sut_dict = dict(
        platform=dict(
            attrib=dict(type='commercial')
        ),
        silicon=dict()
    )

    # TODO: CHANGE THE IP WHEN DO TESTING
    sut = ConfigurationHelper.filter_sut_config(root, 'localhost', sut_filter=sut_dict)[0]
    simics_prov = ConfigurationHelper.get_provider_config(sut=sut, provider_name='simics')

    simics = ProviderFactory.create(simics_prov, log)
    log.info('Start lanuch testing')
    config = {
        r'$bios': r'C:\LocalPackage\bios\unzip\PurleyRefresh\PLYXCRB.PFT.BR.64.2020.23.3.08.0324_0605.D30_P02f01_LBG_SPS.bin',
        r'$disk_image': r'C:\FwEval\img\10nm-ICX\sut-skylakex-efi.amd64-12ago.craff',
        r'$SSC_FLAG': 'TRUE',
    }
    simics_script = r'C:\LocalPackage\bios\unzip\PurleyRefresh\Purley\GoldScripts\Bios\EP_DDR4_LBG_MIN.simics'
    simics.launch_simics(config, simics_script)
    time.sleep(30)
    simics.run_simics_command('$system.mb.sb.pmc->PM_state_S_state', 20)


if __name__ == '__main__':
    test()
