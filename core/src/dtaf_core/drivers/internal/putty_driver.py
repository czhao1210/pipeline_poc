#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietarygit
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
"""
Putty Driver wrapper
"""
import time
import psutil
from dtaf_core.drivers.base_driver import BaseDriver
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.private.driver_config.putty_driver_config import PuttyDriverConfig
import subprocess

class PuttyDriver(BaseDriver):
    def __init__(self, cfg_opts, log):
        super().__init__(cfg_opts, log)
        self._driver_cfg_model = None # type: PuttyDriverConfig


    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def __cleanup(self):
        for proc in psutil.process_iter():
            try:
                if proc.name().find("putty") != -1:
                    proc.kill()
            except psutil.PermissionError as perm_error:
                self._log.error("{}".format(perm_error))
            except Exception as ex:
                self._log.error("unexpected exception: {}".format(ex))

    def stop_logging(self):
        self.__cleanup()

    def start_logging(self, logfile):
        self.__cleanup()
        __cmd = "{} -serial -sessionlog {} \"{},8,n,1,N\" {}".format(
            self._driver_cfg_model.app,
            logfile,
            self._driver_cfg_model.baudrate,
            self._driver_cfg_model.port
        )
        subprocess.Popen(__cmd, shell=True).wait(timeout=60)