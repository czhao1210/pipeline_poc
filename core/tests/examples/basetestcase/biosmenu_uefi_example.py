import os
import sys

from dtaf_core.providers.provider_factory import ProviderFactory

from dtaf_core.lib.base_test_case import BaseTestCase
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.lib.dtaf_constants import Framework
from dtaf_core.providers.ac_power import AcPowerControlProvider
from dtaf_core.providers.dc_power import DcPowerControlProvider
from dtaf_core.providers.bios_menu import BiosSetupMenuProvider, BiosBootMenuProvider
from dtaf_core.providers.uefi_shell import UefiShellProvider
import time


class BiosmenuUefiExample(BaseTestCase):
    """
    Remote Mode Command Reference:
    python3 biosmenu_uefi_example.py --cfg_file tests/system/data/biosmenu_uefi_example_simics_remote.xml
    Native Mode Command Reference:
    python3 biosmenu_uefi_example.py --cfg_file tests/system/data/biosmenu_uefi_example_simics_native.xml
    """

    def __init__(self, test_log, arguments, cfg_opts):
        super().__init__(test_log, arguments, cfg_opts)
        suf_config = ConfigurationHelper.get_sut_config(
            cfg_opts)  # parse the sut configuration from the configuration file
        self._log = test_log  # save the logger object
        self._ac_cfg = ConfigurationHelper.get_provider_config(provider_name="ac",
                                                               sut=suf_config)  # parse AC Provider Configuration
        self._dc_cfg = ConfigurationHelper.get_provider_config(provider_name="dc",
                                                               sut=suf_config)  # parse DC Provider Configuration
        self._boot_cfg = ConfigurationHelper.get_provider_config(provider_name="bios_bootmenu",
                                                                 sut=suf_config)  # parse Bootmenu Provider Configuration
        self._setup_cfg = ConfigurationHelper.get_provider_config(provider_name="bios_setupmenu",
                                                                  sut=suf_config)  # parse Bootmenu Provider Configuration
        self._uefi_cfg = ConfigurationHelper.get_provider_config(provider_name="uefi_shell",
                                                                 sut=suf_config)  # parse UEFI Shell Provider Configuration

    def prepare(self):
        super().prepare()
        self._ac = ProviderFactory.create(cfg_opts=self._ac_cfg, logger=self._log)  # type: AcPowerControlProvider
        self._dc = ProviderFactory.create(cfg_opts=self._dc_cfg, logger=self._log)  # type: DcPowerControlProvider
        self._boot = ProviderFactory.create(cfg_opts=self._boot_cfg, logger=self._log)  # type: BiosBootMenuProvider
        self._setup = ProviderFactory.create(cfg_opts=self._setup_cfg, logger=self._log)  # type: BiosSetupMenuProvider
        self._uefi = ProviderFactory.create(cfg_opts=self._uefi_cfg, logger=self._log)  # type: UefiShellProvider

    def execute(self):
        assert self._ac.ac_power_off()
        assert not self._ac.get_ac_power_state()
        assert self._ac.ac_power_on(timeout=30)
        assert self._ac.get_ac_power_state()
        time.sleep(10)
        self._dc.dc_power_reset()
        # configure timeout, assume the entry menu timeout is 0
        # this step is not necessary, if the default value of timeout in your platform is not 0 (e.g. Lognaville)
        # change timeout to 10
        for i in range(0, 60):
            self._boot.press(input_key="F2")
            time.sleep(0.3)
        # change timeout in setupmenu
        assert self._setup.wait_for_bios_setup_menu(timeout=600)
        self._setup.select(item_name="Boot Maintenance Manager", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Set Time Out Value", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Auto Boot Time-out", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.input_text("10")
        self._setup.enter_selected_item(ignore=False, timeout=5)
        self._setup.select(item_name="Commit Changes and Exit", item_type=None, use_regex=False, timeout=10)
        self._setup.enter_selected_item(ignore=False, timeout=5)
        # reset after change the timeout
        assert self._dc.dc_power_reset()
        if self._boot.wait_for_entry_menu(timeout=600):
            for i in range(0, 2):
                self._boot.press(input_key="F7")
                time.sleep(0.3)
        assert self._boot.wait_for_bios_boot_menu(timeout=120)
        self._boot.select(item_name="UEFI Internal Shell", item_type="", timeout=3, use_regex=False)
        self._boot.enter_selected_item(ignore_output=True, timeout=5)
        assert self._uefi.wait_for_uefi(60)
        assert self._uefi.in_uefi()
        smbiosview_ret = self._uefi.execute("smbiosview -t 17", timeout=150)
        assert smbiosview_ret
        print("*************************output of smbiosview***************************")
        print(smbiosview_ret)
        print("****************************************************")
        pci_ret = self._uefi.execute("pci", timeout=150)
        assert pci_ret
        print("*************************output of pci***************************")
        print(pci_ret)
        print("****************************************************")
        drivers_ret = self._uefi.execute("drivers", timeout=150)
        assert drivers_ret
        print("*************************output of drivers***************************")
        print(drivers_ret)
        print("****************************************************")
        self._ac.ac_power_off()
        return True

    def cleanup(self, return_status):
        super().cleanup(return_status)
        self._uefi.close()
        self._setup.close()
        self._boot.close()
        self._dc.close()
        self._ac.close()


if __name__ == "__main__":
    sys.exit(Framework.TEST_RESULT_PASS if BiosmenuUefiExample.main() else Framework.TEST_RESULT_FAIL)
