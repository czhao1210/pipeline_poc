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

from dtaf_core.providers.internal.xmlcli_bios_provider import XmlcliBiosProvider
from xml.etree import ElementTree as ET

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
cfg_opts = ET.fromstring("""
<bios>
					<driver>
						<xmlcli>
							<sutospath>"/opt/APP/xmlcli/"</sutospath>
							<bios_cfgfilepath>C:\Automation\</bios_cfgfilepath>
							<bios_cfgfilename>neoncity.cfg</bios_cfgfilename>
							<ip>10.190.249.213</ip>
							<user>root</user>
							<password>password</password>
						</xmlcli>
					</driver>
                </bios>
""")


class o():
    def __init__(self,*args,**kwargs):
        pass


class TestXmlcliBiosProvider(object):
    @staticmethod
    def test_xmlcli_bios_provider():
        with XmlcliBiosProvider(log=log, cfg_opts=cfg_opts):
            pass
