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

import sys
from dtaf_core.lib.exceptions import DebuggerException, RegisterInconsistencyException, ReadBackException
from dtaf_core.providers.silicon_reg_provider import SiliconRegProvider
from dtaf_core.lib.dtaf_constants import DebuggerInterfaceTypes
from dtaf_core.lib.dtaf_constants import ProductFamilies


class CscriptsSiliconRegProvider(SiliconRegProvider):
    """
    Class that communicates with the SUT's JTAG port using cscripts API (ITPII or OpenIPC).
    """

    SUPPORTED_CSCRIPTS_INTERFACES = [DebuggerInterfaceTypes.ITP, DebuggerInterfaceTypes.OPENIPC,DebuggerInterfaceTypes.INBAND]
    SUPPORTED_CPU_FAMILY = [ProductFamilies.BDX, ProductFamilies.CPX, ProductFamilies.CLX, ProductFamilies.ICX,
                            ProductFamilies.IVT, ProductFamilies.JKT, ProductFamilies.SKM, ProductFamilies.SKX,
                            ProductFamilies.SNR, ProductFamilies.SPR, ProductFamilies.ICXD, ProductFamilies.RKL,ProductFamilies.SPRHBM]
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
        super(CscriptsSiliconRegProvider, self).__init__(cfg_opts, log)
        self._debugger_type = self._config_model.driver_cfg.debugger_type
        if self._debugger_type not in self.SUPPORTED_CSCRIPTS_INTERFACES:
            raise RuntimeError("Unsupported Cscripts interface {}! Choices "
                               "are {}.".format(self._debugger_type, self.SUPPORTED_CSCRIPTS_INTERFACES))

        self.silicon_cpu_family = self._config_model.driver_cfg.silicon_cpu_family
        if self.silicon_cpu_family not in self.SUPPORTED_CPU_FAMILY:
            raise RuntimeError("Unsupported CPU family {}! Choices are {}.".format(self._debugger_type,
                                                                                   self.SUPPORTED_CPU_FAMILY))

    def __enter__(self):
        """
        Initializes Silicon register debugger by calling appropriate interface library functions

        :return: silicon reg provider object
        :raises RuntimeError: if CScript library not installed or PYTHON_PATH not set to CScripts library path
        """
        # start CScripts main
        # populate arguments for startCScripts.main() function
        import commlibs.utils.version as version
        cscript_version = version.getVersion().split('.')[2]
        # ICX cscripts 110 and forward can not use the --no-multi-instance parameter
        if self._debugger_type == DebuggerInterfaceTypes.ITP:
            sys.argv = ['', '-a', str(DebuggerInterfaceTypes.ITP).lower(), '-p', str(self.silicon_cpu_family).upper()]
        else:
            if self.silicon_cpu_family in [ProductFamilies.SPR,ProductFamilies.CPX,ProductFamilies.SPRHBM,ProductFamilies.ICXD] or (self.silicon_cpu_family in [ProductFamilies.ICX]
                                                                    and int(cscript_version) >= 110):
                sys.argv = ['', '-a', str(DebuggerInterfaceTypes.OPENIPC).lower(), '-p',
                            str(self.silicon_cpu_family).upper()]
            else:
                sys.argv = ['', '-a', str(DebuggerInterfaceTypes.OPENIPC).lower(), '-p',
                            str(self.silicon_cpu_family).upper(), '--no-multi-instance']

        # try importing startCScripts
        try:
            import startCscripts as startCScripts
            self._cscripts = startCScripts
        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

        # call scripts main function with sys.argv
        self._cscripts.main()

        # Obtain and refresh the sv object for use
        try:
            import commlibs.utils.utils as utils
            self._utils = utils
            self._sv = self._utils.getSVComponent()
            self.refresh()
        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

        # update sockets and sockets count
        self._sockets = self.get_sockets()
        self._socket_count = self.get_socket_count()

        self._log.info("-----------Number of Sockets={}".format(self._socket_count))

        # obtain cscript interface pointer
        try:
            import commlibs.interfaces.cscriptsinterface as cscript_interface_ptr
            import common.baseaccess as _baseaccess
            self._cscript_interface_ptr = cscript_interface_ptr
        except ImportError:
            raise ImportError("ITPII PythonSv library is not available! Please check configuration.")

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
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        self._sv.refresh()

    def get_platform_modules(self):
        """
        Obtain CScripts platform modules

        :return: platform modules object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        platform = self._cscript_interface_ptr.get_platform()
        platform_modules = platform.get_plat_module()
        return platform_modules

    def get_cscripts_utils(self):
        """
        Get the common lib utils object from cscripts

        :return: common lib utils interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        return self._utils

    def get_cscripts_ei_object(self):
        """
        Get the error injection object from cscripts

        :return: error injection interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        return self._utils.get_error_obj()

    def get_cscripts_nvd_object(self):
        """
        Get the nvd nvdimm object from cscripts

        :return: nvd interface object from cscripts
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        return self._utils.get_nvd_obj()

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
        print("Number of Sockets=".format(self._socket_count))
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
        :return: default value of register
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
        resolved_scope = self.resolve_scope(scope, socket_index)
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
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        return self._sv.sockets

    def get_socket_count(self):
        """
        Get number of socket counts using cscripts

        :return: number of sockets on platform
        """
        return len(self.get_sockets())

    def get_xnm_memicals_utils_object(self):
        """
        get xnmMemicalsUtils object from commlibs

        :return: xnmMemicalsUtils object
        :raises ImportError: if CScripts not available
        """
        try:

            if self.silicon_cpu_family == ProductFamilies.CLX:
                import platforms.CLX.clxmc.clxMemicalsUtils as muObj
            elif self.silicon_cpu_family == ProductFamilies.SKX:
                import platforms.SKX.skxmc.skxMemicalsUtils as muObj
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxmc.cpxMemicalsUtils as muObj
            else:
                import commlibs.mc.xnmmc.xnmMemicalsUtils as muObj

            return muObj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_mc_utils_object(self):
        """
        get mcUtils object from platform specific folder

        :return: mcUtils object
        :raises ImportError: if CScripts not available
        """
        try:

            if self.silicon_cpu_family == ProductFamilies.CLX:
                import platforms.CLX.clxmc.clxMcUtils as muUtilsObj
            elif self.silicon_cpu_family == ProductFamilies.SKX:
                import platforms.SKX.skxmc.skxMcUtils as muUtilsObj
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxmc.cpxMcUtils as muUtilsObj
            else:
                import commlibs.mc.xnmmc.xnmMcUtils as muUtilsObj

            return muUtilsObj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_ecc_error_injection_object(self):
        """
        get mcUtils object from platform specific folder

        :return: mcUtils object
        :raises ImportError: if CScripts not available
        """
        try:

            if self.silicon_cpu_family == ProductFamilies.CLX:
                import platforms.CLX.clxerror.cpxerrInj as errorInjObj
            elif self.silicon_cpu_family == ProductFamilies.SKX:
                import platforms.SKX.skxerror.skxerrInj as errorInjObj
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxerror.cpxerrInj as errorInjObj
            else:
                import commlibs.mc.xnmmc.xnmEccInjection as errorInjObj

            return errorInjObj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_dimminfo_object(self):
        """
        get dimminfo object from commlibs or platforms folder

        :return: dimminfo object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        try:

            if self.silicon_cpu_family == ProductFamilies.CLX:
                import platforms.CLX.clxmc.clxdimminfo as dimminfo_obj
            elif self.silicon_cpu_family == ProductFamilies.SKX:
                import platforms.SKX.skxmc.skxdimminfo as dimminfo_obj
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxmc.cpxdimminfo as dimminfo_obj
            elif self.silicon_cpu_family == ProductFamilies.SPR:
                import commlibs.interfaces.cscriptsinterface as _interface_ptr
                plat = _interface_ptr.get_platform()
                plat_module = plat.get_plat_module()
                dimminfo_obj = plat_module.get_mc_obj()
            else:
                import commlibs.mc.xnmmc.xnmDimmInfo as dimminfo_obj

            return dimminfo_obj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_klaxon_object(self):
        """
        get klaxon object from commlibs or platforms folder

        :return: klaxon object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        try:

            if self.silicon_cpu_family in [ProductFamilies.CLX,ProductFamilies.SKX]:
                klaxon_obj = self._utils.get_klaxon_obj()
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import pysvtools.klaxon.klaxon as klaxon_obj
                klaxon_obj = klaxon_obj
            else:
                import platforms.ICX.icx_moka as icx_moka
                klaxon_obj = icx_moka.ICX_Moka()

            return klaxon_obj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def populate_scope_dict(self):
        """
        Loop through sockets and populate dictionary with socket/uncore paths and associated objects
        Account for all sockets case
        update class member _scope_dict
        :return: none
        """
        self._scope_dict[SiliconRegProvider.SV + "." + SiliconRegProvider.SOCKETS] = self._sv.sockets
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

    def get_ras_object(self):
        """
        get ras object from commlibs or platforms folder

        :return: ras object
        :raises RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        try:

            if self.silicon_cpu_family in [ProductFamilies.CLX,ProductFamilies.SKX]:
                ras_obj = self._utils.get_ras_obj()
            elif self.silicon_cpu_family == ProductFamilies.SPR:
                import commlibs.interfaces.cscriptsinterface as _interface_ptr
                plat = _interface_ptr.get_platform()
                plat_module = plat.get_plat_module()
                ras_obj = plat_module.get_ras_obj()
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxras.cpxemca2 as ras
                ras_obj = ras.CPXemca2
            else:
                from platforms.ICX.icxrasdefs import icxrasdefs
                ras_obj = icxrasdefs()

            return ras_obj

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_ei_obj(self):
        try:
            if self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxerror.cpxerrInj as _cpxei
                self._ei = _cpxei._cpx_ei_obj

            return self._ei

        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_add_tran_obj(self):
        """
        get address Translation object from commlibs or platforms folder.

        :return: add_tran_obj
        raise: RuntimeError: CScripts raises RuntimeError exception if anything goes wrong
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.ICX:
                import commlibs.mc.xnmmc.xnmAddressTranslator as at_obj

            return at_obj
        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_bootscript_obj(self):
        """
        get bootscript object from platforms folder

        :return: bootscript object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError("This function will not be supported from Scripts, "
                                  "use PythonSv provider...")

    def get_mc_utils_obj(self):
        """
        get mc utils object from platforms folder

        :return: mc_utils object
        :raises RuntimeError: Pythonsv raises RuntimeError exception if anything goes wrong
        """
        raise NotImplementedError("This function will not be supported from Scripts, "
                                  "use PythonSv provider...")

    def unlock(self, unlock_type, creds, itp_path=""):
        """
        unlock ITP, DAL,OpenIPC, pythonsv

        :param unlock_type: (ipc, dal, ipc)
        :param creds:   <domain>/usid
        :param itp_path: itp path (optional)

        :return: True / False
        :raises RuntimeError: Fail to unlock
        """
        raise NotImplementedError("This function will not be supported from Scripts, "
                                  "use PythonSv provider...")

    def get_upi_obj(self):
        """
        get Upi object from commlibs or platforms folder.

        :return: upi_obj
        raise: ImportError: if cscripts not configured correctly
        """
        try:
            if self.silicon_cpu_family == ProductFamilies.SKX:
                import platforms.SKX.skxupi.skxupi as upi
                upi_obj = upi.SKXupi()
            elif self.silicon_cpu_family == ProductFamilies.CLX:
                import platforms.CLX.clxupi.clxupi as upi
                upi_obj = upi.CLXupi()
            elif self.silicon_cpu_family == ProductFamilies.CPX:
                import platforms.CPX.cpxupi.cpxupi as upi
                upi_obj = upi.CLXupi()
            elif self.silicon_cpu_family == ProductFamilies.SPR:
                from platforms.SPR.sprupidefs import sprupidefs as upi
                upi_obj = upi()
            elif self.silicon_cpu_family == ProductFamilies.ICX:
                from platforms.ICX.icxupidefs import icxupidefs as upi
                upi_obj = upi()
            elif self.silicon_cpu_family in [ProductFamilies.SNR, ProductFamilies.ICXD]:
                from commlibs.qpi.xnmupi.xnmupi import _xnmupi as upi
                upi_obj = upi()
            else:
                raise NotImplementedError("Not Implemente for this '{}' Platform".format(self.silicon_cpu_family))

            return upi_obj
        except ImportError:
            raise ImportError("CScripts library is not available! Please check configuration.")

    def get_status_scope_obj(self):
        # type: () -> None
        """
        get status_scope object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if cscripts/pythonsv not configured correctly
        """
        raise NotImplementedError("Not Supported in CScripts yet")

    def get_ltssm_object(self):
        # type: () -> None
        """
        get status_scope object from tool_ext.

        :return: status_scope_obj
        raise: ImportError: if cscripts/pythonsv not configured correctly
        """
        raise NotImplementedError("Not Supported in CScripts yet")

    def get_mca_dump_object(self):
        """
        This method is to get the MCA Dump object.

        :return mca dump object
        :raise ImportError: If pythonsv not configured correctly
        """
        raise NotImplementedError

    def get_mcu_dump_object(self):
        """
        This method is to get the MCU dump Object.

        :return MCU dump object
        :raise ImportError: If pythonsv not configured correctly
        """
        raise NotImplementedError

    def get_upi_status_obj(self):
        """
        This method is to get the upi status object.

        :return Upi status object
        :raise ImportError: If pythonsv not configured correctly
        """
        raise NotImplementedError

    def get_s3m_obj(self):
        """
        This method is to get the s3m obj.

        :return s3m object
        :raise ImportError: If pythonsv not configured correctly
        """
        raise NotImplementedError

    def get_s3m_object(self):
        """
        This method is to get the s3m obj.

        :return s3m object
        :raise ImportError: If pythonsv not configured correctly
        """
        raise NotImplementedError

    def get_err_injection_obj(self):
        """
        get err_inj object from platform specific folder

        :return: err_inj object
        :raises ImportError: if CScripts not available
        """
        raise NotImplementedError("This function will not be supported from CScripts, "
                                  "use PythonSv provider...")
