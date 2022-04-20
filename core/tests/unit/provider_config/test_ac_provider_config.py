import xmltodict
import mock

from dtaf_core.lib.private.ac_provider_config import AcProviderConfig

cfg = xmltodict.parse("""
<ac>
 <driver>
        <pi>
            <ip>10.190.155.176</ip>
            <port>80</port>
            <proxy>http://child-prc.intel.com:913</proxy>
        </pi>
   </driver>
   <timeout>
        <power_on>5</power_on>
        <power_off>10</power_off>
   </timeout>
</ac> 
""")




class TestAcProviderConfig:
    def test_init(self):
        with AcProviderConfig(cfg, mock.MagicMock()) as obj:
            assert isinstance(obj.poweroff_timeout, float)
            assert isinstance(obj.poweron_timeout, float)
