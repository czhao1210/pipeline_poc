#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
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
from abc import ABCMeta, abstractmethod

import six
from dtaf_core.providers.base_provider import BaseProvider


@six.add_metaclass(ABCMeta)
class SiliconRegProvider(BaseProvider):
    """
        Interfaces with the SUT's JTAG debug port to abstract the various debug APIs (DAL, OpenIPC, etc).

        This class is for more sophisticated DFx access
    """

    SV = "sv"

    # below are scope to search/find any registers
    UNCORE = "uncore"
    UNCORES = "uncores"
    SOCKET = "socket"
    SOCKETS = "sockets"
    SPCH = "spch"
    SPCHS = "spchs"

    # x-path for silicon reg provider in configuration file
    DEFAULT_CONFIG_PATH = "suts/sut/providers/silicon_reg"

    def __init__(self, cfg_opts, log):
        """
        Create an instance of Silicon register debugger

        :param cfg_opts: Configuration Object of provider
        :param log: Log object
        :return: None
        :raises RuntimeError: If not-supported debugger interface or CPU specified in the config file.
        """
        super(SiliconRegProvider, self).__init__(cfg_opts, log)

    def __enter__(self):
        """
        Initializes Silicon register debugger by calling appropriate interface library functions

        :return: silicon reg provider object
        :raises RuntimeError: if CScript library not installed or PYTHON_PATH not set to CScripts library path
        """
        return super(SiliconRegProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Terminate connection to the ITP master frame when exiting the test execution context

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        super(SiliconRegProvider, self).__exit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    def refresh(self):
        # type: () -> None
        """
        Force sockets discovery

        :return: None
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_platform_modules(self):
        # type: () -> None
        """
        Obtain CScripts platform modules

        :return: platform modules object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_cscripts_utils(self):
        # type: () -> None
        """
        Get the common lib utils object from cscripts

        :return: common lib utils interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_cscripts_ei_object(self):
        # type: () -> None
        """
        Get the error injection object from cscripts

        :return: error injection interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_cscripts_nvd_object(self):
        # type: () -> None
        """
        Get the nvd nvdimm object from cscripts

        :return: nvd interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_socket_count(self):
        # type: () -> None
        """
        Get number of socket counts using cscripts

        :return: number of sockets on platform
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_sockets(self):
        # type: () -> None
        """
        Obtain sockets for use in calling C-Scripts utils and C-Scripts platform modules. NOT to be used otherwise!

        :return: sockets object details of platform using cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def search_by_type(self, scope, keyword, search_type, socket_index=0):
        """
        Search given a specified search type and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param keyword: keyword value to limit search results
        :param search_type: search type to limit search results
        :param socket_index: CPU socket index
        :return: search results
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def search_reg(self, scope, keyword, socket_index=0):
        """
        Search for register names and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param keyword: keyword value to limit search results
        :param socket_index: CPU socket index
        :return: search register results
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong

        """
        raise NotImplementedError

    @abstractmethod
    def search_reg_bitfield(self, scope, keyword, socket_index=0):
        """
        Search a register bitfield name and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param keyword: keyword value to limit search results
        :param socket_index: CPU socket index
        :return: bitfield register search results
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong

        """
        raise NotImplementedError

    @abstractmethod
    def search_reg_descr(self, scope, keyword, socket_index=0):
        """
        Search register description and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param keyword: keyword value to limit search results
        :param socket_index: CPU socket index
        :return: register search results
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong

        """
        raise NotImplementedError

    @abstractmethod
    def get_addr(self, scope, reg_path, socket_index=0):
        """
        Get address of register and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: register address results
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_default(self, scope, reg_path, socket_index=0):
        """
        Get default value of register and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: default value of register
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_spec(self, scope, reg_path, socket_index=0):
        """
        Get spec of register- VOID output

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: register spec value
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def show(self, scope, reg_path, socket_index=0):
        """
        Show register values by bitfield- VOID output

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: register values by bitfield
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def show_search(self, scope, keyword, socket_index=0):
        """
        Search and show register- VOID output

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param keyword: keyword value
        :param socket_index: CPU socket index
        :return: search and show register value
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_path(self, scope, reg_path, socket_index=0):
        """
        get register value by path

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: register value by path
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_field_value(self, scope, reg_path, field, socket_index=0):
        """
        get register field value.

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param field: register field value
        :param socket_index: CPU socket index
        :return: register field value
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_xnm_memicals_utils_object(self):
        # type: () -> None
        """
        get xnmMemicalsUtils object from commlibs

        :return: xnmMemicalsUtils object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_dimminfo_object(self):
        # type: () -> None
        """
        get dimminfo object from commlibs or platforms folder

        :return: dimminfo object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_klaxon_object(self):
        # type: () -> None
        """
        get klaxon object from commlibs or platforms folder

        :return: klaxon object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_ras_object(self):
        # type: () -> None
        """
        get get_ras_object object from commlibs or platforms folder

        :return: get_ras_object object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_add_tran_obj(self):
        # type: () -> None
        """
        get get_add_tran_obj object from commlibs or platforms folder

        :return: get_add_tran_obj object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def unlock(self, unlock_type, creds, itp_path=""):
        """
        unlock ITP, DAL,OpenIPC, pythonsv

        :param unlock_type: (ipc, dal, ipc)
        :param creds:   <domain>/usid
        :param itp_path: itp path (optional)

        :return: True / False
        :raises RuntimeError: Fail to unlock
        """
        raise NotImplementedError

    def get_bootscript_obj(self):
        # type: () -> None
        """
        get bootscript object from platforms folder

        :return: bootscript object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_mc_utils_obj(self):
        # type: () -> None
        """
        get mc utils object from platforms folder

        :return: mc_utils object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError

    @abstractmethod
    def get_upi_obj(self):
        # type: () -> None
        """
        get Upi object from commlibs or platforms folder.

        :return: upi_obj
        raise: ImportError: if cscripts/pythonsv not configured correctly
        """
        raise NotImplementedError

    @abstractmethod
    def get_status_scope_obj(self):
        # type: () -> None
        """
        get status_scope object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if cscripts/pythonsv not configured correctly
        """
        raise NotImplementedError

    @abstractmethod
    def get_ltssm_object(self):
        # type: () -> None
        """
        get status_scope object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if pythonsv not configured correctly
        """
        raise NotImplementedError

    @abstractmethod
    def get_err_injection_obj(self):
        # type: () -> None
        """
        get error injection object from platforms folder

        :return: err_inj object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError
