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
import re
import os
import six
import paramiko

from dtaf_core.providers.bios_provider import BiosProvider

if six.PY2:
    import ConfigParser
if six.PY3:
    import configparser as ConfigParser


class BaseBiosXmlCliProvider(BiosProvider):
    def __init__(self, cfg_opts, log):
        """
        :param self._log: Logger object to use for debug and info messages
        :param cfg_opts: Dictionary of configuration options for execution environment.
        """
        super(BaseBiosXmlCliProvider, self).__init__(cfg_opts, log)
        self.__ospath = self._config_model.driver_cfg.sutospath  # xmlfolder location in sut
        self.__bios_cfgfilepath = self._config_model.driver_cfg.bios_cfgfilepath
        self.__bios_cfgfilename = self._config_model.driver_cfg.bios_cfgfilename
        self.__platform_file = (self.__bios_cfgfilepath + self.__bios_cfgfilename)
        self._ip = self._config_model.driver_cfg.ip
        self._port = self._config_model.driver_cfg.port
        self._user = self._config_model.driver_cfg.user
        self._password = self._config_model.driver_cfg.password
        self._root_privellage = self._config_model.driver_cfg.root_privilege
        self._python_path = self._config_model.driver_cfg.python_path

    def __enter__(self):
        return super(BaseBiosXmlCliProvider, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(BaseBiosXmlCliProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def path_setter(self, path=None):
        if path:
            self.__ospath = path
        ret = BaseBiosXmlCliProvider.execute(self, "python " + str(
            self.__ospath) + "/xmlcli_path_setter.py path_setup {0}".format(self.__ospath))
        if ("Path Is Set Properly" in ret):
            self._log.info("xmlcli SUT Path Is Set Properly")
            return True
        else:
            self._log.error("xmlcli SUT Path Issue")
            return False

    def write_bios_knob_value(self, *inp, **kwargs):
        """
        This function is used to handle if the prompt name are similar in such case by seeing the platform config file you will be passing the parameter
        name directly into this function.
        Return:- True if successfull
        """
        try:
            hexa = hex(kwargs['val'])
        except:
            pass
        if (len(inp) % 2 == 0):
            end = (len(inp))
            val = inp[1::2]
            knob = inp[0::2]
            end = len(inp) / 2
            data = []
            str1 = ''
            for i in range(0, int(end)):
                a = (knob[i] + str("=") + str(val[i]) + str(','))
                data.append(a)
            data = (str1.join(data))
            data = data[:len(data) - 1]
            # print(data)
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "/xmlcli_save_read_prog_knobs.py Prog_name \"{0}\"".format(data), Timeout=100)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "/xmlcli_save_read_prog_knobs.py Prog_name \"{0}\"".format(data), Timeout=100)
            for i in range(0, int(end)):
                if ("Bios Knob \"" + str(knob[i]) + "\" does not currently exist" in ret) == True:
                    self._log.error(
                        "Writing up the bios knob Failed Due To Improper Bios_Name " + str(knob[i]) + " was Given")
                    return (
                    False, "Writing up the bios knob Failed Due To Improper Bios_Name " + str(knob[i]) + " was Given")
                elif ("Verify Fail: Knob = " + str(knob[i]) in ret) == True:
                    self._log.error(
                        "Writing up the bios knob Failed, Reason Wrong value Given for Knob {0} with Wrong Value {1}".format(
                            knob[i], val[i]))
                    return (False,
                            "Writing up the bios knob Failed, Reason Wrong value Given for Knob {0} with Wrong Value {1}".format(
                                knob[i], val[i]))
                self._log.info("Writing up the bios Knob {0} with Value {1} Successful".format(knob[i], val[i]))
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "/xmlcli_save_read_prog_knobs.py ReadKnobs_xml \"{0}\"".format(data), Timeout=100)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "/xmlcli_save_read_prog_knobs.py ReadKnobs_xml \"{0}\"".format(data), Timeout=100)
            if ("Verify Passed!" in ret) == True:
                for i in range(0, int(end)):
                    self._log.info(
                        "Read Verification of bios Knob {0} with Value {1} Successful".format(knob[i], val[i]))
                return (True, "Writing up All bios knob options was successfull")
            else:
                return (False, "verification for Bios Knob set Failed")
        else:
            return (False, "Wrong Mismatching BiosKnob and Bios value Was Given")

    def set_bios_knobs(self, *inp, **kwargs):
        """
        This function is used to set the bios knobs to the required value.
        Input is the knob name and the value to which the knob has to set.
        Output is the knob changed to the given input value
        """
        overlap = kwargs.pop('overlap', None)
        if (overlap == True):
            """
            This function is used to handle if the prompt name are similar in such case by seeing the platform config file you will be passing the parameter
            name directly into this function.
            Return:- True if successfull
            """
            if (len(inp) % 2 == 0):
                end = (len(inp))
                val = inp[1::2]
                knob = inp[0::2]
                end = len(inp) / 2
                data = []
                str1 = ''
                for i in range(0, int(end)):
                    a = (knob[i] + str("=") + val[i] + str(','))
                    data.append(a)
                data = (str1.join(data))
                data = data[:len(data) - 1]
                if (self._root_privellage == True):
                    ret = BaseBiosXmlCliProvider.execute(self,
                                                         "echo " + str(self._password) + " | sudo -S python " + str(
                                                             self.__ospath) + "/xmlcli_save_read_prog_knobs.py Prog_name \"{0}\"".format(
                                                             data), Timeout=100)
                else:
                    ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                        self.__ospath) + "/xmlcli_save_read_prog_knobs.py Prog_name \"{0}\"".format(data), Timeout=100)
                for i in range(0, int(end)):
                    if ("Bios Knob \"" + str(knob[i]) + "\" does not currently exist" in ret) == True:
                        self._log.error(
                            "Setting up the bios knob Failed Due To Improper Bios_Name " + str(knob[i]) + " was Given")
                        return (False, "Setting up the bios knob Failed Due To Improper Bios_Name " + str(
                            knob[i]) + " was Given")
                    elif ("Verify Fail: Knob = " + str(knob[i]) in ret) == True:
                        self._log.error(
                            "Setting up the bios knob Failed, Reason Wrong value passed for Knob{0} with Wrong Value {1}".format(
                                knob[i], val[i]))
                        return (False,
                                "Setting up the bios knob Failed, Reason Wrong value passed for Knob{0} with Wrong Value {1}".format(
                                    knob[i], val[i]))
                if ("The Knob value was changed & passed" in ret) == True:
                    for i in range(0, int(end)):
                        self._log.info("Setting up the bios Knob {0} with Value {1} Successful".format(knob[i], val[i]))
                    if (self._root_privellage == True):
                        ret = BaseBiosXmlCliProvider.execute(self,
                                                             "echo " + str(self._password) + " | sudo -S python " + str(
                                                                 self.__ospath) + "xmlcli_save_read_prog_knobs.py ReadKnobs_xml \"{0}\"".format(
                                                                 data), Timeout=100)
                    else:
                        ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                            self.__ospath) + "xmlcli_save_read_prog_knobs.py ReadKnobs_xml \"{0}\"".format(data),
                                                             Timeout=100)
                    if ("Verify Passed!" in ret) == True:
                        for i in range(0, int(end)):
                            self._log.info(
                                "Read Verification of bios Knob {0} with Value {1} Successful".format(knob[i], val[i]))
                        return (True, "Setting up All bios knob options was successfull")
                    else:
                        return (False, "verification for Bios Knob set Failed")
                else:
                    return (False, "XMl Error")
            else:
                self._log.error("Mismatching Input Given, Setting up the bios knob Value Has Failed")
                return (False, "Mismatching Input Given, Setting up the bios knob Value Has Failed")
        else:
            cp = ConfigParser.SafeConfigParser()
            cp.read(self.__platform_file)
            op = cp.sections()
            flag = 1
            di, section, key = ({}, '', '')
            if len(inp) % 2 == 0:
                j = 0
                while (j <= len(inp)) & ((j + 1) <= len(inp)):
                    di[inp[j]] = inp[j + 1]
                    j += 2
            else:
                flag = 0
                self._log.debug("Given less number of inputs")
                return (False, "Given less number of inputs")
            for i, key in di.items():
                if (i in op):
                    target_key = (cp.get(i, 'Target'))
                    target_key = target_key.split(",")
                    try:
                        if (int(key) > len(target_key)):
                            self._log.error("Check Target Key Option Values Properly")
                            return (False, "Check Target Key Option Values Properly")
                        else:
                            di[i] = target_key[int(key)]
                    except Exception as e:
                        self._log.error(e, "Please give the proper input")
                        return (False, "Please give the proper input")
                else:
                    self._log.error("Match Not Found In Any Sections")
                    return (False, "Match Not Found In Any Sections")
            result = None
            section = ','.join(di.keys())
            key = ','.join(di.values())
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_get_verify_knobs.py ProgKnobs_xml" + " " + "\"" + str(
                    section) + "\"" + " " + "\"" + key + "\"", Timeout=100)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_get_verify_knobs.py ProgKnobs_xml" + " " + "\"" + str(
                    section) + "\"" + " " + "\"" + key + "\"", Timeout=100)
            ret = str(ret)
            ret = ''.join(ret)
            if (ret.find("True") != -1):
                self._log.info("Success In Setting Up The Knob")
                result = []
                for i, v in di.items():
                    out = re.findall(
                        r'The Knob {0} was changed to the value {1} & verification passed|The Knob {0} was not changed to the value {1} & verification failed'.format(
                            i, v), ret, re.I | re.M)
                    if out != []:
                        result.append(out[0])
                    else:
                        self._log.error("No output present")
                        return (False, out)
                self._log.info("Resultant output is {0}".format(result))
            else:
                self._log.error("Failure In Setting Up The Knob")
                flag = 0

            if flag == 0:
                return (False, result)
            else:
                return (True, result)

    def execute(self, cmd="", Timeout=None):
        """
        This Function is a workaround function for communicating with SUT via SSH or serial.
        To make the Bios Knob Change Happen from The Os Level.
        """
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self._ip, port=self._port, username=self._user, password=self._password)
            ssh_session = ssh_client.get_transport().open_session()
            if ssh_session.active:
                stdout = ""
                stderr = ""
                stdin, stdout, stderr = ssh_client.exec_command(cmd)
                # received_output=ssh_session.recv(9000)
                stdout = stdout.readlines()
                stderr = stderr.readlines()
                if stdout:
                    #print("=========== >>> got the output",''.join(stdout))
                    return (''.join(stdout))
                elif stderr:
                    print("=========== >>> captured the error", ''.join(stderr))
                    return (''.join(stderr))
                else:
                    print("Nothing came application must be opened")
                    return ("SUCCESS", "N/A")
            else:
                print("SSH not their use microsoft openssh to refer P4V configure it")
        except Exception as e:
            print("connection didn't happen", e)

        finally:
            try:
                ssh_client.close()
            except:
                pass

    def read_bios_knobs(self, *inp, **kwargs):
        """
        This Function is used to read the current value of a Bios knob and takes the knob name as an input. We can pass mulitple knobs as an input.
        Input Para :- *inp eg: 'Driver Strength','FPK Port 2'
        Output Return :- self._log.infos the current value of the knob and Return True or False
        excepection :- Attribute Error
        """
        group = kwargs.pop('group', None)
        if ((str(group)).lower() in ["true", "yes", "on", "enable"]):
            knob = ','
            a = []
            data = (knob.join(inp))
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py verify_knob \"{0}\"".format(data), Timeout=100)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py verify_knob \"{0}\"".format(data), Timeout=100)
            ret = (((ret.strip()).rstrip("\n")).replace("\n", "")).split(",")
            a = ret
            self._log.info('Given Knob Values are {0}'.format(data))
            try:
                ret = (ret[len(ret) - 1])
                s = (ret.index("Verify Fail"))
                res = ret[s:len(ret)]
                res = str(res).split(r"Verify Fail:")
                res = res[1:]
                for i in range(0, len(res)):
                    self._log.error("Mis-Match of Bios {0}".format(res[i]))
            except Exception as e:
                pass
            if ("Verify Passed!" in ret) == True:
                self._log.info("Knob Data verification Matches {0}".format(data))
                return (True, "Setting up All bios knob options was successfull")
            else:
                return (False, res, "verification for Bios Knob set Failed")
        else:
            out = ""
            hexa = kwargs.pop('hexa', None)
            if (hexa == True):
                knob = ','
                data = (knob.join(inp))
                if (self._root_privellage == True):
                    ret = BaseBiosXmlCliProvider.execute(self,
                                                         "echo " + str(self._password) + " | sudo -S python " + str(
                                                             self.__ospath) + "xmlcli_get_verify_knobs.py \"read_current_knob_write\"" + " " + "\"{0}\"".format(
                                                             data), 100)
                else:
                    ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                        self.__ospath) + "xmlcli_get_verify_knobs.py \"read_current_knob_write\"" + " " + "\"{0}\"".format(
                        data), 100)
                ret = ''.join(str(ret))
                try:
                    out = re.findall(r"knob (.*)\n", ret, re.I | re.M)
                    if out != []:
                        # self._log.info('Resultant output is {0}'.format(out))
                        special_sym = ['\"', '\'', '[', ']', ')', '(']
                        for i in special_sym:
                            out = str(out).replace(i, '')
                        out = (''.join(out))
                        out = out.split(',')
                        for i in range(0, len(inp)):
                            self._log.info("Read Data for Given Knob {0}".format(out[i]))
                        return True, out
                    else:
                        self._log.error('No output present'.format(out))
                        return False, out
                except (AttributeError, Exception) as e:
                    self._log.debug(e)
                    raise
            else:
                cp = ConfigParser.SafeConfigParser()
                cp.read(self.__platform_file)
                op = cp.sections()
                flag = 1
                li = []
                for i in inp:
                    li.append(i)
                    section = ','.join(li)
                if (self._root_privellage == True):
                    ret = BaseBiosXmlCliProvider.execute(self,
                                                         "echo " + str(self._password) + " | sudo -S python " + str(
                                                             self.__ospath) + "xmlcli_get_verify_knobs.py \"read_current_knob\"" + " " + "\"" + str(
                                                             section) + "\"", 40)
                else:
                    ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                        self.__ospath) + "xmlcli_get_verify_knobs.py \"read_current_knob\"" + " " + "\"" + str(
                        section) + "\"", 40)
                ret = ''.join(str(ret))
                try:
                    out = re.findall(r"knob (.*)\n", ret, re.I | re.M)
                    if out != []:
                        self._log.debug('Resultant output is {0}'.format(out))
                    else:
                        self._log.info('No output present'.format(out))
                        return False
                except (AttributeError, Exception) as e:
                    self._log.debug(e)
                    raise
                if (ret.find("passed") != -1):
                    return (True, out)
                else:
                    self._log.error("Failure".format(out))
                    return False

    def get_knob_options(self, *inp):
        """
        This Function is used to get the current value, knob options of the Bios knob and takes knob as an input. We can pass mulitple knobs as an input
        Input Para :- *inp eg: 'Driver Strength','FPK Port 2'
        Output Return :- self._log.info the current value, knob options of the Bios knob and return True or False
        """
        cp = ConfigParser.SafeConfigParser()
        cp.read(self.__platform_file)
        op = cp.sections()
        flag = 1
        li = []
        for i in inp:
            li.append(i)
            section = ','.join(li)
        if (self._root_privellage == True):
            ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                self.__ospath) + "xmlcli_get_verify_knobs.py get_option" + " " + "\"" + str(section) + "\"",
                                                 Timeout=100)
        else:
            ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                self.__ospath) + "xmlcli_get_verify_knobs.py get_option" + " " + "\"" + str(section) + "\"",
                                                 Timeout=100)
        ret = ''.join(str(ret))
        try:
            out = re.findall(r"available values for the knob (.*)\n", ret, re.I | re.M)
            if out != []:
                self._log.info('Resultant output is {0}'.format(out))
            else:
                self._log.error('No output present')
                return (False, out)
        except (AttributeError, Exception) as e:
            self._log.debug(e)
            raise
        if (ret.find("Current") != -1):
            return (True, out[0])
        else:
            self._log.error("Failure")
            return (False, "Knob options not available")

    def default_bios_settings(self):
        """
        This function is used to set the Bios knobs to default value, takes no input parameter and return Success upon setting the Bios knobs
        to default and return failure upon setting the Bios knobs to not default.
        """
        if (self._root_privellage == True):
            ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                self.__ospath) + "xmlcli_save_read_prog_knobs.py Default_xml", Timeout=50)
        else:

            ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                self.__ospath) + "xmlcli_save_read_prog_knobs.py Default_xml", Timeout=50)
        ret = ''.join(str(ret))
        out = re.findall(r"The Knob values were set to default", ret, re.I | re.M)
        if out != []:
            self._log.debug('Resultant output is {0}'.format(''.join(out)))
            return (True, ret)
        else:
            self._log.error("Failure")
            return (False, "Failure")

    def get_bios_bootorder(self):
        """
        This Function is used to get the current Bios boot order and takes no input parameter.
        return Output :- True or False along with current boot order in the particular platform.
        """
        try:
            flag = 1
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py Get_boot_order_xml", Timeout=100)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py Get_boot_order_xml", Timeout=100)
            ret = (''.join(str(ret))).strip()
            ret = ret.split("Boot order list is:")
            ret = (ret[1])[2:]
            if (ret != None):
                self._log.debug("{0}".format(ret))
                return (True, ret)
            else:
                self._log.error("Failed To Get BootOrder List")
                return (False, "Failure")

        except Exception as e:
            self._log.error("Failed To Get BootOrder List", e)
            return (False)

    def set_bios_bootorder(self, *inp, **kwargs):
        """
        This Function is used to get the set Bios boot order with the OS drive and takes input parameter as OS drive name from the configuration file.
        make sure extactly the name is given from the Get boot order if white space follow it exactly in the bios platform config file
        Input Para :- linux/windwos/efi/pendrive/boot_target
        Output Return :- True or False
        """
        group = kwargs.pop('Target', None)
        index = kwargs.pop('index', None)
        Target = None
        if (group and index):
            cp = ConfigParser.SafeConfigParser()
            cp.read(self.__platform_file)
            op = cp.sections()
            flag = 1
            if ('BootOrder' in op):
                if (
                        Target == 'linux' or Target == 'windows' or Target == 'efi' or Target == 'pendrive' or Target == 'boot_target'):
                    out = (cp.get('BootOrder', Target))
                    Drive_name = (out.split(','))[index]
                    if (self._root_privellage == True):
                        ret = BaseBiosXmlCliProvider.execute(self,
                                                             "echo " + str(self._password) + " | sudo -S python " + str(
                                                                 self.__ospath) + "xmlcli_save_read_prog_knobs.py Change_boot_order_xml {0}".format(
                                                                 Drive_name), Timeout=120)
                    else:
                        ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                            self.__ospath) + "xmlcli_save_read_prog_knobs.py Change_boot_order_xml {0}".format(
                            Drive_name), Timeout=120)
                    ret = ''.join(str(ret))
                    if (re.search(r'Bios boot order got changed & passed', ret, re.I) != None):
                        # self._log.info("Success",'Bios boot order got changed to {0}'.format(Drive_name))
                        return (True, ret)
                    else:
                        self._log.error("failure Bios boot order not changed & failed")
                        return False
                else:
                    self._log.error("failure Target linux or windows is not present in the configuration file")
                    return False
            else:
                self._log.error("failure BootOrder section is not present in the configuration file")
                return False
        else:
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py Change_boot_order_xml \"" + str(inp) + "\"",
                                                     Timeout=120)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py Change_boot_order_xml \"" + str(inp) + "\"",
                                                     Timeout=120)
            ret = ''.join(str(ret))
            self._log.debug(ret)
            if (re.search(r'Bios boot order got changed & passed', ret, re.I) != None):
                self._log.info("Success " + 'Bios boot order got changed to {0}'.format(inp))
                return (True, ret)
            else:
                self._log.error("failure Bios boot order not changed & failed")
                return False

    def EFI_set_bios_bootorder(self, Target, index, EFI_commands):
        """
        This function is used to set the bios boot order. It will goto the EFI shell and self._os.execute the input commands.
        Input Target is the OS name i.e., linux or windows or EFI from the config file and Index is the position at which the OS device name is present in config file.
        Output is boot order changes to required boot device.
        """
        cp = ConfigParser.SafeConfigParser()
        cp.read(self.__platform_file)
        op = cp.sections()
        flag = 1
        if ('BootOrder' in op):
            if (
                    Target == 'linux' or Target == 'windows' or Target == 'efi' or Target == 'pendrive' or Target == 'boot_target'):
                out = (cp.get('BootOrder', Target))
                Drive_name = (out.split(','))[index]
                if (self._root_privellage == True):
                    ret = BaseBiosXmlCliProvider.execute(self,
                                                         "echo " + str(self._password) + " | sudo -S python " + str(
                                                             self.__ospath) + "xmlcli_save_read_prog_knobs.py EFI_xml {0} {1}".format(
                                                             Drive_name, EFI_commands), 120)
                else:
                    ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                        self.__ospath) + "xmlcli_save_read_prog_knobs.py EFI_xml {0} {1}".format(Drive_name,
                                                                                                 EFI_commands), 120)
                ret = ''.join(str(ret))
                if (re.search(r'Bios boot order got changed', ret, re.I) != None):
                    print("Success", 'Bios boot order got changed to {0}'.format(Drive_name))
                    return (True, ret)
                else:
                    print("failure Bios boot order not changed & failed")
                    return False
            else:
                print("failure Target linux or windows or EFI is not present in the configuration file")
                return False
        else:
            print("failure BootOrder section is not present in the configuration file")
            return False

    def set_auto_knobpath_knoboptions(self, modify_existingpath, *knobnames):
        """
        This function is used to get the knobname, knob path and knob options.
        Input modify_existingpath=True i.e., if the knob info present in the config file it will modify & false it is not going to modify in the config file.
        And config_file_path is the configuartion file path by default it takes from the global variable & knobnames are the names present in the BIOS or paltform config.xml file.
        Output is stored in config_file_path self.__platform_file
        works only for enable or disable options
        """
        cp = ConfigParser.SafeConfigParser()
        cp.read(self.__platform_file)
        op = cp.sections()
        for knobname in knobnames:
            path, options = ("", "")
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_get_verify_knobs.py knobpath \"{0}\"".format(knobname), Timeout=200)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_get_verify_knobs.py knobpath \"{0}\"".format(knobname), Timeout=200)
            out = re.search(r'path is (.*)', ret, re.I)
            if out == None:
                self._log.error("Knob path not found")
            else:
                path = out.group(1).replace('/', ',')
                print(out.group(1))
            result = BaseBiosXmlCliProvider.get_knob_options(self, knobname)
            if result[1] == "Knob options not available":
                pass
            else:
                options = re.findall(r'\:(.*)', str(result[1]), re.I)
                options = options[0]
            if (knobname not in op):
                with open(r"{0}".format(self.__platform_file), 'a') as fp:
                    fp.write('[{0}]'.format(knobname))
                    fp.write('\n')
                    fp.write("Bios_Path = {0}".format(path))
                    fp.write('\n')
                    fp.write('Target = {0}'.format(options))
                    fp.write('\n\n')
            elif (modify_existingpath == True):
                with open(r"{0}".format(self.__platform_file), 'r') as f:
                    newlines = []
                    count = 0
                    for line in f.readlines():
                        if '[' + knobname + ']' in line:
                            newlines.append(line)
                            count += 1
                        elif count == 1:
                            out = re.search(r'Bios_Path = (.*)', line, re.I)
                            # print out.group(1)
                            newlines.append(line.replace(out.group(1), path))
                            count += 1
                        elif count == 2:
                            out = re.search(r'Target = (.*)', line, re.I)
                            newlines.append(line.replace(out.group(1), options))
                            count = 0
                        else:
                            newlines.append(line)
                with open(r"{0}".format(self.__platform_file), 'w') as f:
                    for line in newlines:
                        f.write(line)
            else:
                path = (cp.get(knobname, 'Bios_Path'))
                options = (cp.get(knobname, 'Target'))
            print('Knob {0} path is {1} and the options are {2}'.format(knobname, path, options))
        return True

    def flash_ifwi_image(self, image_path=None, image_name=None):
        try:
            full_path = str(image_path + image_name)
            if (self._root_privellage == True):
                ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo -S python " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py flash_ifwi_image " + full_path, Timeout=120)
            else:
                ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                    self.__ospath) + "xmlcli_save_read_prog_knobs.py flash_ifwi_image  " + str(full_path), Timeout=100)
            ret = (''.join(str(ret))).strip()
            self._log.info(ret)
            if (ret.find("SPI Region Flashed successfully") != -1):
                self._log.info("FLashing of IFWI Image was Successful On Platform")
                return True
            else:
                self._log.error("Failed To Flash IFWI IMAGE on SUT using XMLCLI")
                return False
        except Exception as e:
            self._log.error("Failed To Flash IFWI IMAGE on SUT using XMLCLI", e)
            return False

    def getall_knobspath_options(self):
        """
        This function is used to get the Bios knobname, knob path & knob options.
        Input is the self.__platform_file by default it takes from the global variable.
        And the output is stored in the congiration file.
        """
        result = os.path.exists(r"{0}".format(self.__platform_file))
        if result == True:
            os.remove(r"{0}".format(self.__platform_file))
            self._log.info("Config file is present. So removed it")
        else:
            print("Config file is not present. So no need to remove it")
        if (self._root_privellage == True):
            ret = BaseBiosXmlCliProvider.execute(self, str(self._python_path) + " " + str(
                self.__ospath) + "xmlcli_get_verify_knobs.py getall_knobpath_options", Timeout=3000)
        else:
            ret = BaseBiosXmlCliProvider.execute(self, "echo " + str(self._password) + " | sudo python " + str(
                self.__ospath) + "xmlcli_get_verify_knobs.py getall_knobpath_options", Timeout=3000)
        result = BaseBiosXmlCliProvider.execute(self, "cat " + str(self.__ospath) + "getall_knobspath_options.config",
                                                5000)  # Make sure that the output of this line doesn't exceeds maximum bytes
        self._log.info(result)
        newlines = []
        count = 0
        knobname, path, options = ([], [], [])
        # newlines= result.split('\n')
        if result[1] != 1:
            newlines = result.split('\n')
            for line in newlines:
                if re.search(r'\[(.*)\]', line, re.I) != None:
                    out = re.search(r'\[(.*)\]', line, re.I)
                    knobname.append(out.group(1))
                    count += 1
                if count == 1 and re.search(r'Bios_Path = (.*)', line, re.I) != None:
                    out = re.search(r'Bios_Path = (.*)', line, re.I)
                    path.append(out.group(1))
                    count += 1
                if count == 2 and re.search(r'Target = (.*)', line, re.I) != None:
                    out = re.search(r'Target = (.*)', line, re.I)
                    options.append(out.group(1))
                    count = 0
                    with open(r"{0}".format(self.__platform_file), "a+") as fp:
                        fp.write('[{0}]'.format(knobname[0]))
                        fp.write('\n')
                        fp.write("Bios_Path = {0}".format(path[0]))
                        fp.write('\n')
                        fp.write('Target = {0}'.format(options[0]))
                        fp.write('\n\n')
                    knobname, path, options = ([], [], [])
        else:
            self._log.info("Integer found")
            return False
        return True
