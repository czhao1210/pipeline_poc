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

import os
import os.path
import sys
from importlib import __import__
from shutil import copyfile
from typing import Any
from imp import importlib

from dtaf_core.lib.dtaf_constants import DebuggerInterfaceTypes
from dtaf_core.lib.dtaf_constants import ProductFamilies
from dtaf_core.providers.silicon_reg_provider import SiliconRegProvider


class Pymodule(object):
    def __init__(self, mod_path, file_path):
        self._mod_path = mod_path
        self._file_path = file_path

    def __getattr__(self, name: str) -> Any:
        new_path = os.path.join(self._file_path, name)
        new_mod_path = ".".join([self._mod_path, name])
        py_path = "{}.py".format(new_path)
        if os.path.isfile(py_path):
            return __import__(new_mod_path, fromlist=[new_mod_path])
        elif os.path.isdir(new_path):
            return Pymodule(pymod=None, mod_path=new_mod_path, file_path=new_path)
        raise AttributeError(name)

class PythonsvSiliconRegProvider(SiliconRegProvider):
    """
    Class that communicates with the SUT's JTAG port using cscripts API (ITPII or OpenIPC).
    """

    SUPPORTED_PYTHONSV_INTERFACES = [DebuggerInterfaceTypes.ITP, DebuggerInterfaceTypes.OPENIPC]
    SUPPORTED_CPU_FAMILY = [ProductFamilies.BDX, ProductFamilies.CPX, ProductFamilies.CLX, ProductFamilies.ICX,
                            ProductFamilies.IVT, ProductFamilies.JKT, ProductFamilies.SKM, ProductFamilies.SKX,
                            ProductFamilies.SNR, ProductFamilies.SPR, ProductFamilies.ICXD]
    PKG_PATH_DICT = {ProductFamilies.ICX: "icelakex.upi",
                     ProductFamilies.SPR: "sapphirerapids.upi"}
    _scope_dict = {}
    _socket_count = 0

    def __init__(self, cfg_opts, log):
        """
        Create an instance of Silicon register debugger

        :param cfg_opts: Configuration Object of provider
        :param log: Log object
        :return: None
        :raises RuntimeError: If not-supported debugger interface or CPU specified in the config file.
        """
        super(PythonsvSiliconRegProvider, self).__init__(cfg_opts, log)
        self._debugger_type = self._config_model.driver_cfg.debugger_type
        if self._debugger_type not in self.SUPPORTED_PYTHONSV_INTERFACES:
            raise RuntimeError("Unsupported PythonSV interface {}! Choices "
                               "are {}.".format(self._debugger_type, self.SUPPORTED_PYTHONSV_INTERFACES))

        self.silicon_cpu_family = self._config_model.driver_cfg.silicon_cpu_family
        if self.silicon_cpu_family not in self.SUPPORTED_CPU_FAMILY:
            raise RuntimeError("Unsupported CPU family {}! Choices are {}.".format(self._debugger_type,
                                                                                   self.SUPPORTED_CPU_FAMILY))

        self.components_list = self._config_model.driver_cfg.components_list

        try:
            if self.components_list and self.silicon_cpu_family in [ProductFamilies.SPR, ProductFamilies.ICX]:
                import namednodes
                self._sv = namednodes.sv.get_manager(self.components_list)
            elif self.silicon_cpu_family in [ProductFamilies.SPR, ProductFamilies.ICX]:
                import namednodes
                self._sv = namednodes.sv.get_manager(["socket"])
            else:
                from components import ComponentManager
                self._sv = ComponentManager(["socket"])
            self.refresh()
        except ImportError:
            raise ImportError("PythonSV library is not available! Please check configuration.")
        # update sockets and sockets count
        self._sockets = self.get_sockets()
        self._socket_count = self.get_socket_count()
        if 'pch' in self.components_list:
            self._pch_count = self.get_pch_count()
        else:
            self._pch_count = 0

    def get_platform_modules(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_cscripts_utils(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_cscripts_ei_object(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_cscripts_nvd_object(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_xnm_memicals_utils_object(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_dimminfo_object(self):
        """
        This method is to get the dimm info object
        """
        if ProductFamilies.SPR == self.silicon_cpu_family:
            import sapphirerapids.mc.sprDimmInfo as sdm
            return sdm
        else:
            raise NotImplementedError("Not Supported in PythonSV yet for platform type- {}".format(
                self.silicon_cpu_family))

    def get_klaxon_object(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_ras_object(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_add_tran_obj(self):
        raise NotImplementedError("Not Supported in PythonSV yet")

    def get_bootscript_obj(self):
        """
        get bootscript object from platforms folder

        :return: bootscript object
        :raises ImportError: Pythonsv not configures properly
        """
        if self.silicon_cpu_family == ProductFamilies.SPR:
            try:
                from sapphirerapids.toolext.bootscript import boot as boot_script
                return boot_script
            except ImportError:
                raise ImportError("The boot_script object not found. Please check PythonSv configuration")
        else:
            raise NotImplementedError("This function not supported yet for the product "
                                      "family '{}'".format(self.silicon_cpu_family))

    def get_mc_utils_obj(self):
        """
        get mc utils object from platforms folder

        :return: mc_utils object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        if self.silicon_cpu_family == ProductFamilies.SPR:
            try:
                import sapphirerapids.mc.sprMcUtils as mc_utils
                return mc_utils
            except ImportError:
                raise ImportError("The mc_utils object not found. Please check PythonSv configuration")
        else:
            raise NotImplementedError("This function not supported yet for the product "
                                      "family '{}'".format(self.silicon_cpu_family))

    def __enter__(self):
        """
        Initializes Silicon register debugger by calling appropriate interface library functions

        :return: silicon reg provider object
        :raises RuntimeError: if CScript library not installed or PYTHON_PATH not set to CScripts library path
        """
        # start pythonsv main
        # populate arguments for startCScripts.main() function
        if self._debugger_type == DebuggerInterfaceTypes.ITP:
            sys.argv = ['', '-a', str(DebuggerInterfaceTypes.ITP).lower(), '-p', str(self.silicon_cpu_family).upper()]
        else:
            sys.argv = ['', '-a', str(DebuggerInterfaceTypes.OPENIPC).lower(), '-p',
                        str(self.silicon_cpu_family).upper(),
                        '--no-multi-instance']

        # Obtain and refresh the sv object for use
        try:
            
            if self.components_list and self.silicon_cpu_family in [ProductFamilies.SPR, ProductFamilies.ICX]:
                import namednodes
                self._sv = namednodes.sv.get_manager(self.components_list)
            elif self.silicon_cpu_family in [ProductFamilies.SPR, ProductFamilies.ICX]:
                import namednodes
                self._sv = namednodes.sv.get_manager(["socket"])
            else:
                from components import ComponentManager
                self._sv = ComponentManager(["socket"])
            self.refresh()
        except ImportError:
            raise ImportError("PythonSV library is not available! Please check configuration.")

        # update sockets and sockets count
        self._sockets = self.get_sockets()
        self._socket_count = self.get_socket_count()
        if 'pch' in self.components_list:
            self._pch_count = self.get_pch_count()
        else:
            self._pch_count = 0
        self._log.info("-----------Number of Sockets={}".format(self._socket_count))

        # populate scope_dict
        self.populate_scope_dict()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Terminate connection to the ITP master frame when exiting the test execution context

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        # Terminate connection to the ITP master frame when exiting the test execution context
        if exc_type is not None:
            try:
                # self._log.exception(exc_type, exc_val, exc_tb)
                # Ensure CScripts shell terminates
                sys.exit(1)
            except Exception as ex:
                # few cscripts command like klaxon.check_sys_errors throw exception when we
                # exit cscripts, we will catch the exception, so that test case will not fail
                log_error = "Exception occurred during cscripts exit: '{}'".format(ex)
                self._log.error(log_error)

    def refresh(self):
        """
        Force sockets discovery

        :return: None
        :raises RuntimeError: PythonSV raises RuntimeError exception if anything goes wrong
        """
        self._sv.refresh()

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
        resolved_scope = self.resolve_scope(scope, socket_index)
        #print("--------------------------------------------------------------------------")
        #print("Number of Sockets=".format(self._socket_count))
        #print(str(resolved_scope))
        #print("--------------------------------------------------------------------------")
        return self._scope_dict[resolved_scope].search(keyword, search_type)

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
        return self.search_by_type(scope, keyword, search_type="r", socket_index=socket_index)

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
        return self.search_by_type(scope, keyword, search_type="f", socket_index=socket_index)

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
        return self.search_by_type(scope, keyword, search_type="d", socket_index=socket_index)

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
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].getbypath(reg_path).getaddress()

    def get_default(self, scope, reg_path, socket_index=0):
        """
        Get default value of register and return

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param socket_index: CPU socket index
        :return: default value of registerimport()
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].getbypath(reg_path).getdefault()

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
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].getbypath(reg_path).get_spec()

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
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].getreg(reg_path).show()

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
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].showsearch(keyword)

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
        #print(f"!!!!!!!!!!!!! scope={scope}, reg={reg_path}")
        resolved_scope = self.resolve_scope(scope, socket_index)
        #print(f"!!!!!!!!!!!!! resolved_scope={resolved_scope}")
        return self._scope_dict[resolved_scope].getbypath(reg_path)

    def get_field_value(self, scope, reg_path, field, socket_index=0):
        """
        get register field value.

        :param scope: scope value, specify one of  UNCORE, UNCORES, SOCKET, SOCKETS
        :param reg_path: reg_path value
        :param field: field value
        :param socket_index: CPU socket index
        :return: register field value
        :raises KeyError: if specified in-correct scope value
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        resolved_scope = self.resolve_scope(scope, socket_index)
        return self._scope_dict[resolved_scope].getbypath(reg_path).getfieldobject(field).get_value()

    def get_sockets(self):
        """
        Obtain sockets for use in calling C-Scripts utils and C-Scripts platform modules. NOT to be used otherwise!

        :return: sockets object details of platform using cscripts
        :raises RuntimeError: PythonSV raises RuntimeError exception if anything goes wrong
        """
        return self._sv.sockets

    def get_pchs(self):
        """
        Obtain pchs for use in calling C-Scripts utils and C-Scripts platform modules. NOT to be used otherwise!

        :return: pchs object details of platform using cscripts
        :raises RuntimeError: PythonSV raises RuntimeError exception if anything goes wrong
        """
        return self._sv.pchs

    def get_socket_count(self):
        """
        Get number of socket counts using cscripts

        :return: number of sockets on platform
        """
        return len(self.get_sockets())

    def get_pch_count(self):
        """
        Get number of pch counts using cscripts

        :return: number of pchs on platform
        """
        return len(self.get_pchs())

    def populate_scope_dict(self):
        """
        Loop through sockets and populate dictionary with socket/uncore paths and associated objects
        Account for all sockets case
        update class member _scope_dict
        :return: none
        """
        #print(f"!!!!!!!!!!!!!!!!!!!!popuplate 1111")
        self._scope_dict[SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKETS] = self._sv.sockets
        #print(f"!!!!!!!!!!!!!!!!!!!!popuplate 22222: pch_count={self._pch_count}")
        for i in range(self._pch_count):
            curr_pch = self._sv.pchs[i]
            curr_sv_spch_str = SiliconRegProvider.SV + "." + SiliconRegProvider.SPCH + str(i)
            #print(f"!!!!!!!!!!!add pch={curr_sv_spch_str}")
            self._scope_dict[curr_sv_spch_str] = curr_pch

        for i in range(self._socket_count):
            curr_socket = self._sv.sockets[i]
            curr_sv_socket_str = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + str(i)
            self._scope_dict[curr_sv_socket_str] = curr_socket

            if hasattr(curr_socket, SiliconRegProvider.UNCORE):
                # Account for all sockets, uncore case
                all_sockets_uncore_key = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKETS + "." + \
                                         SiliconRegProvider.UNCORE
                if all_sockets_uncore_key not in self._scope_dict.keys():
                    self._scope_dict[all_sockets_uncore_key] = self._sv.sockets.uncore

                self._scope_dict[curr_sv_socket_str + "." + SiliconRegProvider.UNCORE] = self._sv.sockets[i].uncore
            elif hasattr(curr_socket, SiliconRegProvider.UNCORES):
                # Account for all sockets, all uncores case
                all_sockets_all_uncores_key = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKETS + "." + \
                                              SiliconRegProvider.UNCORES
                if all_sockets_all_uncores_key not in self._scope_dict.keys():
                    self._scope_dict[all_sockets_all_uncores_key] = self._sv.sockets.uncores

                # Account for ith socket, all uncores case
                self._scope_dict[curr_sv_socket_str + "." + SiliconRegProvider.UNCORES] = self._sv.sockets[i].uncores

                self.uncore_count = len(curr_socket.uncores)
                for j in range(self.uncore_count):
                    self._scope_dict[curr_sv_socket_str + "." + SiliconRegProvider.UNCORE + str(j)] = \
                        self._sv.sockets.uncores[j]

    def resolve_scope(self, scope, socket_index=0):
        """
        Attempt to resolve given scope to known scopes alongside given socket index where applicable

        :param scope: SOCKET, SOCKETS, UNCORE, or UNCORES
        :param socket_index: The given socket index
        :return: Resolved scope
        :raises KeyError: if specified in-correct scope value
        """
        # If passed generic socket scope, resolve to indexed socket (i.e. socket0 by default)
        if scope is SiliconRegProvider.SOCKET:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + \
                    str(socket_index)
        # If passed sockets scope, ignore socket index
        elif scope is SiliconRegProvider.SOCKETS:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKETS
        elif scope is SiliconRegProvider.SPCH:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SPCH + \
                    str(socket_index)
        # If passed sockets scope, ignore socket index
        elif scope is SiliconRegProvider.SPCHS:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SPCHS
        elif scope is SiliconRegProvider.UNCORE:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + \
                    str(socket_index) + "." + SiliconRegProvider.UNCORE
            # Attempt uncore/uncores swap due to platform variants
            if scope not in self._scope_dict.keys():
                scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + \
                        str(socket_index) + "." + SiliconRegProvider.UNCORES

        elif scope is SiliconRegProvider.UNCORES:
            scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + \
                    str(socket_index) + "." + SiliconRegProvider.UNCORES
            # Attempt uncore/uncores swap due to platform variants
            if scope not in self._scope_dict.keys():
                scope = SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKET + \
                        str(socket_index) + "." + SiliconRegProvider.UNCORE
        else:
            raise KeyError("Invalid scope: " + str(scope))
        return scope

    def unlock(self, unlock_type, creds, itp_path=""):
        """
        unlock ITP, DAL,OpenIPC, pythonsv

        :param unlock_type: (ipc, dal, ipc)
        :param creds:   <domain>/usid
        :param itp_path: itp path (optional)

        :return: True / False
        :raises RuntimeError: Fail to unlock
        """
        import subprocess
        unlocker = self._config_model.driver_cfg.unlocker
        cmd = "%s %s creds %s" % (unlock_type, creds)
        if "itp" == unlock_type:
            proc = subprocess.Popen(cmd)
            return proc.wait(60) == 0
        elif "dal" == unlock_type:
            pass
        elif "ipc" == unlock_type:
            cmd = "%s %s path \"%s\" creds %s" % (unlock_type, itp_path, creds)
            proc = subprocess.Popen(cmd)
            proc.wait(60)
            return True
        else:
            auth_file = os.path.join(os.path.dirname(unlocker), "Push", "Authorization.xml")
            auth_xds = os.path.join(os.path.dirname(unlocker), "Push", "Authorization.xsd")
            ipc_auth = "C:\\Intel\\OpenIPC\\Config\\Authorization.xml"
            auth_lines = list()
            with open(auth_file, "r") as template:
                lines = template.readlines()
                for ln in lines:
                    if ln.find("__CREDENTIALS-PLACEHOLDER__") != -1:
                        ln = ln.replace("__CREDENTIALS-PLACEHOLDER__", "<Credentials Username=\"%s\"/>" % creds)
                    auth_lines.append(ln)
            with open(ipc_auth, "w") as ipc_xml:
                ipc_xml.writelines(auth_lines)
            copyfile(auth_xds, "C:\\Intel\\OpenIPC\\Config\\Authorization.xsd")
            return True
        raise NotImplementedError

    def get_upi_obj(self):
        """
        This method is to get the upi obj.
        :return upi object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                from sapphirerapids import upi as u
            else:
                import upi as u
            return Pymodule(mod_path=u.__name__, file_path=u.__path__[0])
        except ImportError as e:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_mca_dump_object(self):
        """
        This method is to get the mca dump obj.
        :return mca dump object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                import core.debug as cd
                return cd
        except ImportError:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_mcu_dump_object(self):
        """
        This method is to get the mcu dump obj.
        :return mcu dump object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                import mc.sprMcUtils as mcu
                return mcu
        except ImportError:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_upi_status_obj(self):
        """
        This method is to get the upi status obj.
        :return upi status object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                import sapphirerapids.upi.upiStatus as us
                return us
        except ImportError:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_s3m_obj(self):
        """
        This method is to get the s3m obj.

        :return s3m object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                import s3m.debugger.ad as ad
                return ad
        except ImportError:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_s3m_object(self):
        """
        This method is to get the s3m obj.

        :return s3m object
        :raise ImportError: If pythonsv not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SPR:
                import sapphirerapids.s3m.debugger.ad as ad
                return ad
        except ImportError:
            raise ImportError("Pythonsv library is not available! Please check configuration.")

    def get_status_scope_obj(self):
        # type: () -> None
        """
        get status_scope object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if cscripts/pythonsv not configured correctly
        """
        if self.silicon_cpu_family == ProductFamilies.SPR:
            try:
                import sapphirerapids.toolext.status_scope as status_scope_obj
                return status_scope_obj
            except ImportError:
                raise ImportError("The boot_script object not found. Please check PythonSv configuration")
        else:
            raise NotImplementedError("This function not supported yet for the product "
                                      "family '{}'".format(self.silicon_cpu_family))

    def get_ltssm_object(self):
        # type: () -> None
        """
        get ltssm object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if pythonsv not configured correctly
        """

        if self.silicon_cpu_family == ProductFamilies.SPR:
            try:
                import pysvtools.pciedebug.ltssm as ltssm_obj
                return ltssm_obj
            except ImportError:
                raise ImportError("The boot_script object not found. Please check PythonSv configuration")
        else:
            raise NotImplementedError("This function not supported yet for the product "
                                      "family '{}'".format(self.silicon_cpu_family))

    def get_err_injection_obj(self):
        """
        get error injection object from platforms folder

        :return: err_inj object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        if self.silicon_cpu_family == ProductFamilies.SPR:
            try:
                import sapphirerapids.mc.sprErrInjection as err_inj
                return err_inj
            except ImportError:
                raise ImportError("The err_inj object not found. Please check PythonSv configuration")
        else:
            raise NotImplementedError("This function not supported yet for the product "
                                      "family '{}'".format(self.silicon_cpu_family))
