#!/usr/bin/env python
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
from abc import ABCMeta, abstractmethod

from dtaf_core.providers.base_provider import BaseProvider
from six import add_metaclass


@add_metaclass(ABCMeta)
class BiosProvider(BaseProvider):
    """
    Class that manipulate BIOS Menu UI for testing
    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass communication (SOL, Serial). This makes the dependency on specific hardware setups easier to identify.
    """
    DEFAULT_CONFIG_PATH = "suts/sut/providers/bios"
    def __init__(self, cfg_opts,log):
        """
        Create a new BiosMenuProvider object
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BiosProvider, self).__init__(cfg_opts,log)

    @abstractmethod
    def set_bios_bootorder(self,Target,index):
         # type: (int) -> str
         """
         This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file. make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
         :param target:
         :return: True or False
         """
         raise NotImplementedError

    def select_boot_device(self, bootdevice):
         # type: (int) -> str
         """
         This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file. make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
         :param target:  options ("None", "Pxe", "Hdd", "Cd", "Diags", "BiosSetup", "Usb")
         :return: True or False
         """
         raise NotImplementedError

    def get_boot_device(self):
         # type: (int) -> str
         """
         return the current selected boot device
         :return: return device name ("None", "Pxe", "Hdd", "Cd", "Diags", "BiosSetup", "Usb")
         """
         raise NotImplementedError


@add_metaclass(ABCMeta)
class XmlCliBiosProvider(BiosProvider):
    """
    Class that manipulate BIOS Menu UI for testing
    This class cannot be used directly, instead, this interface is applied to the subclasses, with a different subclass communication (SOL,XMLCLI(OS),
    Serial). This makes the dependency on specific hardware setups easier to identify.
    """
    def __init__(self, cfg_opts,log):
        """
        Create a new BiosMenuProvider object
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(XmlCliBiosProvider, self).__init__(cfg_opts,log)
        
    @abstractmethod
    def write_bios_knob_value(self,*inp,**kwargs):
        """
        This function is used to handle if the prompt name are similar in such case by seeing the platform config file you will be passing the parameter
        name directly into this function.
        Return:- True if successfull
        """
        raise NotImplementedError

    @abstractmethod
    def set_bios_knobs(self,*inp,**kwargs):
        # type:() -> list
        """
        This Function is used to program knob to the given knob value and takes the knob name, knob value as an input
        Input Para :- drive name,index from configuration file eg: "Driver Strength",0,"FPK Port 2",3
        Output Return :- Prints the Bios boot order and return True or False.
        """
        raise NotImplementedError

    @abstractmethod
    def read_bios_knobs(self,*inp,**kwargs):
        # type:() -> list
        """
        This Function is used to read the current value of a Bios knob and takes the knob name as an input. We can pass mulitple knobs as an input.
        Input Para :- \*inp eg: 'Driver Strength','FPK Port 2'
        Output Return :- Prints the current value of the knob and Return True or False
        excepection :- Attribute Error
        """    
        raise NotImplementedError

    @abstractmethod
    def get_knob_options(self,*inp):
        # type:() -> list
        """
        This Function is used to get the current value, knob options of the Bios knob and takes knob as an input. We can pass mulitple knobs as an input
        Input Para :- \*inp eg: 'Driver Strength','FPK Port 2'
        Output Return :- print the current value, knob options of the Bios knob and return True or False
        """
        raise NotImplementedError

    @abstractmethod
    def default_bios_settings(self):
        """
        This function is used to set the Bios knobs to default value, takes no input parameter and return Success upon setting the Bios knobs
        to default and return failure upon setting the Bios knobs to not default.
        """
        raise NotImplementedError

    @abstractmethod
    def get_bios_bootorder(self):
        """
        This Function is used to get the current Bios boot order and takes no input parameter.
        return Output :- True or False along with current boot order in the particular platform.
        """
        raise NotImplementedError

    @abstractmethod
    def set_bios_bootorder(self,Target,index):
         # type: (int) -> str
         """
         This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file. make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
         :param target:
         :return: True or False
         """
         raise NotImplementedError

    def select_boot_device(self, bootdevice):
         # type: (int) -> str
         """
         This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file. make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
         :param target:  options ("None", "Pxe", "Hdd", "Cd", "Diags", "BiosSetup", "Usb")
         :return: True or False
         """
         raise NotImplementedError

    def get_boot_device(self):
         # type: (int) -> str
         """
         return the current selected boot device
         :return: return device name ("None", "Pxe", "Hdd", "Cd", "Diags", "BiosSetup", "Usb")
         """
         raise NotImplementedError

    @abstractmethod
    def EFI_set_bios_bootorder(self,Target,index,EFI_commands):
        """
        This function is used to set the bios boot order. It will goto the EFI shell and self._os.execute the input commands.
        Input Target is the OS name i.e., linux or windows or EFI from the config file and Index is the position at which the OS device name is present in config file.
        Output is boot order changes to required boot device.
        """
        raise NotImplementedError
        
    @abstractmethod
    def set_auto_knobpath_knoboptions(self,modify_existingpath,*knobnames):
        """
        This function is used to get the knobname, knob path and knob options.
        Input modify_existingpath=True i.e., if the knob info present in the config file it will modify & false it is not going to modify in the config file.
        And config_file_path is the configuartion file path by default it takes from the global variable & knobnames are the names present in the BIOS or paltform config.xml file. 
        Output is stored in config_file_path self.__platform_file
        works only for enable or disable options
        """
        raise NotImplementedError

    @abstractmethod
    def flash_ifwi_image(self, image_path=None, image_name=None):
        """
        This function is used to get the knobname, knob path and knob options.
        Input modify_existingpath=True i.e., if the knob info present in the config file it will modify & false it is not going to modify in the config file.
        And config_file_path is the configuartion file path by default it takes from the global variable & knobnames are the names present in the BIOS or paltform config.xml file.
        Output is stored in config_file_path self.__platform_file
        works only for enable or disable options
        """
        raise NotImplementedError

    @abstractmethod
    def path_setter(self,path=None):
        """
        :param path: used to set the xmlcli path in the SUT. this is the path where the file has to be Copied.
        :return: True if successfull
        """
        raise NotImplementedError

@add_metaclass(ABCMeta)
class RedfishBiosProvider(BiosProvider):
    @abstractmethod
    def set_bios_bootorder(self, first_order=None):
        # type: (int) -> str
        """
        This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file. make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
        :param target:
        :return: True or False
        """
        raise NotImplementedError

    @abstractmethod
    def get_bios_bootorder(self):
        """
        This Function is used to get the current Bios boot order and takes no input parameter.
        return Output :- True or False along with current boot order in the particular platform.
        """
        raise NotImplementedError