import sys

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.bios_provider import BiosProvider
from dtaf_core.providers.provider_factory import ProviderFactory


class RedfishProviderExample(BaseTestCase):
    def __init__(self, test_log, arguments, cfg_opts):
        super(RedfishProviderExample, self).__init__(test_log, arguments, cfg_opts)
        xmlcli_cfg = cfg_opts.find(BiosProvider.DEFAULT_CONFIG_PATH)
        self._bios = ProviderFactory.create(xmlcli_cfg, test_log)

    def test_get_bios_bootorder(self):
        ret = self._bios.get_bios_bootorder()
        if (ret[0] == True):
            self._log.info("System Testing Passed For Get Bios Boot Order")
            self._log.info(ret[1])
        else:
            self._log.error("Ssytem Testing FAILED For Get Bios Boot Order")

    def test_set_bios_bootorder(self):
        '''
        #using config file method
        ret=self._bios.set_bios_bootorder('efi',0)
        if(ret[0] == True):
            self._log.info("System Testing Passed For set Bios Boot Order")
            self._log.info(ret[1])
        else:
            self._log.error("System Testing FAILED For set Bios Boot Order")
        '''
        ret = self._bios.set_bios_bootorder('BiosSetup')
        if (ret == True):
            self._log.info("System Testing Passed For set Bios Boot Order")
        else:
            self._log.error("System Testing FAILED For set Bios Boot Order")

    def execute(self):
        #self.test_set_bios_bootorder()
        self.test_get_bios_bootorder()
        return True


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if RedfishProviderExample.main() else Framework.TEST_RESULT_FAIL)
