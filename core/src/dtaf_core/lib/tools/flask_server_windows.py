#jan-01-2021 created skelton
import re
import os
import sys
import time
import ctypes
import datetime
import paramiko
import threading
import subprocess
from subprocess import Popen,PIPE,STDOUT

flask_invt = r"C:\flask_inventory.txt"
#Initializing Library Requiremnet for Flask
try:
    from flask import Flask, request, abort, jsonify, send_from_directory
except:
    print("FLASK service not installed")
    try:
        if sys.platform == 'win32':
            try:
                a=subprocess.check_output("c:\python36\python.exe -m pip install --upgrade pip --proxy https://proxy-chain.intel.com:911", shell=True)
            except:
                subprocess.check_output(
                    "C:\Python27\python.exe -m pip install --upgrade pip --proxy=\"https://proxy-chain.intel.com:911\"",
                    shell=True)
            a = subprocess.check_output("python -m pip install flask --proxy=\"https://proxy-chain.intel.com:911\"", shell=True)
            print("INstallation Done")
            from flask import Flask, jsonify, request
        else:
            subprocess.check_output(
                "export http_proxy=http://proxy-chain.intel.com:911;export https_proxy=http://proxy-chain.intel.com:912;sudo pip install flask",
                shell=True)
    except:
        print("Flask Missing ")

try:
    import socket
    hostname = socket.gethostname()
    ipadd = socket.gethostbyname(hostname)
except:
    ipadd = "Hostmachine_ipaddress"
    print("socket Library Not Found")
    pass

try:
    import configparser
    config = configparser.ConfigParser()
    config.read(flask_invt)
except:
    print("configparser Libraries not installed")
    try:
        if sys.platform == 'win32':
            try:
                a = subprocess.check_output(
                    "python -m pip install configparser --proxy=\"http://proxy-chain.intel.com:911\"", shell=True)
            except:
                subprocess.check_output(
                    "C:\Python27\python.exe -m pip install --upgrade pip --proxy=\"https://proxy-chain.intel.com:911\"",
                    shell=True)
                a = subprocess.check_output(
                    "python -m pip install configparser --proxy=\"http://proxy-chain.intel.com:911\"", shell=True)
                import configparser
                config = configparser.ConfigParser()
                config.read(flask_invt)
        else:
            print("linux not yet coded")
    except:
        print(
            "configparser library missing install it manually pip install configparser --proxy=http://proxy-chain.intel.com:911")

#Initializing Library Requirement for pdu
try:
    from raritan import rpc
    from raritan.rpc import pdumodel
except:
    print("PDU Libraries not installed")
    try:
        if sys.platform == 'win32':
            try:
                a=subprocess.check_output("python -m pip install cloudshell-pdu-raritan==1.0.55 --proxy=http://proxy-chain.intel.com:911",shell=True)
            except:
                subprocess.check_output(
                    "C:\Python27\python.exe -m pip install --upgrade pip --proxy=https://proxy-chain.intel.com:911",
                    shell=True)
                a = subprocess.check_output(
                    "python -m pip install cloudshell-pdu-raritan==1.0.55 --proxy=http://proxy-chain.intel.com:911", shell=True)
                print("INstallation Done")
                from raritan import rpc
                from raritan.rpc import pdumodel
        else:
            print("linux not yet coded")
    except:
        print("PDU control library missing install it manually pip install cloudshell-pdu-raritan==1.0.55 --proxy=http://proxy-chain.intel.com:911")

#info passing hostmachine details
try:
    import socket
    hostname = socket.gethostname()
    host_ipadd = socket.gethostbyname(hostname)
except:
    ipadd = "rpi_ipaddress"
    print("socket Library Not Found")
    pass

try:
    import zipfile
except:
    if sys.platform == 'win32':
        try:
            a = subprocess.check_output(
                "python -m pip install zipfile --proxy=http://proxy-chain.intel.com:911", shell=True)
        except:
            subprocess.check_output(
                "C:\Python27\python.exe -m pip install --upgrade pip --proxy=https://proxy-chain.intel.com:911",
                shell=True)
            a = subprocess.check_output(
                "python -m pip install zipfile --proxy=http://proxy-chain.intel.com:911", shell=True)
            import zipfile
    else:
        print("linux not yet coded")

UPLOAD_DIRECTORY = "C:\\flask_firmware\\"
BANINO_DIRECTORY ="C:\\banino\code\\"
try:
    if not os.path.exists(UPLOAD_DIRECTORY):
        subprocess.check_output("mkdir C:\\flask_firmware\\",shell=True)
        time.sleep(1)
        subprocess.check_output("mkdir C:\\flask_firmware\\bmc", shell=True)
        time.sleep(1)
        subprocess.check_output("mkdir C:\\flask_firmware\\ifwi", shell=True)
except:
    print("This is a Not a Windows Machine")
    pass

post_code = "C:\\postcode\\rfat_modified.tcl"
try:
    if not os.path.exists(post_code):
        subprocess.check_output("mkdir C:\\postcode\\",shell=True)
        time.sleep(1)
        subprocess.check_output("curl -X GET bdcspiec010.gar.corp.intel.com/files/postcode.zip --output C:\\cpld_postcode.zip",shell=True)
        with zipfile.ZipFile("C:\\cpld_postcode.zip", 'r') as zip_ref:
            zip_ref.extractall("C:\\")
            zipfile.close()
except:
    print("This is a Not a Windows Machine")
    pass

try:
    if not os.path.exists(BANINO_DIRECTORY):
        print("Banino Doesn't exists")
        subprocess.check_output("curl -X GET bdcspiec010.gar.corp.intel.com/files/banino.zip --output C:\\banino.zip",shell=True)
        with zipfile.ZipFile("C:\\banino.zip", 'r') as zip_ref:
            zip_ref.extractall("C:\\")
            zipfile.close()
except Exception as ex:
    print("error",ex)
    pass

def pdu_configure(outlet,ip,usr,pwd):
    try:
        f=open(flask_invt,'w')
        print("aaaaaaaaa")
        f.write("[pdu]\noutlet="+str(outlet)+"\nip="+str(ip)+"\nusername="+str(usr)+"\npassword="+str(pwd)+"")
        f.close()
        return True
    except Exception as ex:
        print (ex)
        return False

app = Flask(__name__)
class PduDriver():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(flask_invt)
        username = config.get('pdu', 'username')
        password = config.get('pdu', 'password')
        ip = config.get('pdu', 'ip')
        outlet = config.get('pdu', 'outlet')
        print(ip)
        print(username)
        print(outlet)
        print(password)
        self.username = username
        self.password = password
        self.outlets = outlet
        self.port = 22
        self.ip = ip
        self.invoke_timeout = 5
        self.powerstate_timeout = 20
        self.cmd_on = ["power outlets {} on /y \n".format(i) for i in self.outlets]
        self.cmd_off = ["power outlets {} off /y \n".format(i) for i in self.outlets]
        self.cmd_show = ["show outlets {} \n".format(self.outlets)]
        self.recv_data = b''

    def get_recv_data(self, ssh):
        self.recv_data = b''
        self.recv_data = ssh.recv(1024)

    def wait_for_invoke(self, ssh):
        nowtime = datetime.datetime.now()
        while (datetime.datetime.now() - nowtime).seconds < int(self.invoke_timeout):
            t = threading.Thread(target=self.get_recv_data, args=[ssh])
            t.setDaemon(True)
            t.start()
            t.join(3)
            if b'#' in self.recv_data or b'>' in self.recv_data:
                return
        time.sleep(int(self.invoke_timeout))

    def _execute(self, cmd_list):
        ssh = None
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ip, port=self.port,
                           username=self.username, password=self.password)
            ssh = client.get_transport().open_session()
            ssh.get_pty()
            ssh.invoke_shell()
            self.wait_for_invoke(ssh)
            for cmd in cmd_list:
                num = 0
                while num < 3:
                    ssh.sendall(cmd)
                    time.sleep(0.5)
                    num += 1
        except Exception as ex:
            print("[%s] %s target failed, the reason is %s"
                  % (datetime.datetime.now(), self.ip, str(ex)))
            raise ex
        finally:
            ssh.close()
            client.close()

    def _check_dict_value(self, dict_data):
        data = set(dict_data.values())
        if len(data) > 1:
            return False
        elif len(data) == 1 and list(data)[0]:
            return True
        elif len(data) == 1 and not list(data)[0]:
            return False
        else:
            return None

    def ac_power_on(self, timeout=None):
        # type: (int) -> bool
        """
        This API changes SUT from G3 to S0/S5. API will not check
        the initial state of SUT. It just sends signal.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                  API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been connected.
                None        : Fail to send power on command
        :raise DriverIOError: if command execution failed in driver
        """

        self._execute(self.cmd_on)
        return self.get_ac_power_state(timeout)

    def ac_power_off(self, timeout=None):
        # type: (int) -> bool
        """
        This API will change SUT from S5/S0 to G3.
        It will check if the entrance state is S5 and if the final state is G3.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
                operation turn off or turn on universal standard 0 is off 1 is on.
                timeout  :second, the max time spend for executing AC_power_off to
                 SUT enter into G3, it should more than 0. If it is None,
                 API will refer to configuration for the default value.
        :return:
                True        : AC power supply has been removed.
                None        : Fail to send power off command
        :raise DriverIOError: if command execution failed in driver
        :raise TimeoutException: fail to respond before timeout
        """

        self._execute(self.cmd_off)
        return self.get_ac_power_state(timeout)

    def get_ac_power_state(self, timeout):
        # type: (None) -> bool
        """
        Get AC power Detection of SUT.
        :param: username needs to be given for the pdu secure login identification purpose
                password for verfication of the username exists
                channel which power socket on the PDU needs to be controlled
        :return:
            True    -    AC POWER Detected
            NONE     -   AC POWER NOT Detected

        :raise DriverIOError: if command execution failed in driver
        """
        ssh = None
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ip, port=self.port, username=self.username,
                           password=self.password, timeout=timeout)
            ssh = client.get_transport().open_session()
            ssh.get_pty()
            ssh.invoke_shell()
            self.wait_for_invoke(ssh)
            state_list = {}
            for cmd in self.cmd_show:
                num = 0
                while num < 3:
                    ssh.sendall(cmd)
                    time.sleep(0.5)
                    ret_data = ssh.recv(1024).decode("utf-8")
                    if 'On' in ret_data:
                        state_list[cmd] = True
                    elif 'Off' in ret_data:
                        state_list[cmd] = False
                    num += 1
            return self._check_dict_value(state_list)
        except Exception as ex:
            print("[%s] %s target failed, the reason is %s"
                  % (datetime.datetime.now(), self.ip, str(ex)))
            raise ex
        finally:
            ssh.close()
            client.close()

def aconfromacoff(timeouton=None):
    try:
        pdu = PduDriver()
        a=pdu.ac_power_on()
        print(a)
        if(a==True):
            return True
        else:
            return False
    except Exception as ex:
        return "Error"

def acofffromacon(timeoutoff=None):
    try:
        pdu = PduDriver()
        a=pdu.ac_power_off()
        print(a)
        if( a == False):
            return True
        else:
            return False
    except Exception as ex:
        return "Error"
#Banino==================================================================================================================================
class BaninoDriver():
    def __init__(self):
        self._power_cmd = r"C:\banino\code\Banino_SXState"
        self.chip_write_verification_ifwi = False
        self.chip_write_verification_bmc = False
        self.ladybird = ctypes.cdll.LoadLibrary(r"C:\banino\code\Banino_SXState\x64\ladybird.dll")

    def conect_relay(self, relay_num, relay_port):
        try:
            relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
            print("Relay_status {0}".format(relay_state))
            if relay_state == 1:
                print("Relay Connected")
                return True
            else:
                self.ladybird.SetRelayState(1, relay_num, relay_port, 1)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
                if relay_state == 1:
                    print("Connecting Relay Successful")
                    return True
                else:
                    print("Connecting Relay Fail")
                    raise
        except Exception as ex:
            print("Relay Connect Error {0}".format(ex))
            raise

    def conect_relay_custom(self, relay_port):
        """
        SetRelayState(unsigned int baninoNumber, unsigned int relayGroup, unsigned int relayNumber, unsigned int relayState)
        relayGroup 2
        relayNumber 1 - 7
        """
        try:
            relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
            print("Relay_status {0}".format(relay_state))
            if (relay_state == 1):
                print("Relay Connected")
                return True
            else:
                self.ladybird.SetRelayState(1, 2, relay_port, 1)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
                if (relay_state == 1):
                    print("Connecting Custom Relay Number {0} Successful".format(relay_port))
                    return True
                else:
                    print("Connecting Custom Relay Number {0} Failed".format(relay_port))
                    raise
        except Exception as ex:
            print("Custom Relay Connect Error {0}".format(ex))
            raise

    def disconnect_relay_custom(self, relay_port):
        """
        SetRelayState(unsigned int baninoNumber, unsigned int relayGroup, unsigned int relayNumber, unsigned int relayState)
        relayGroup 2
        relayNumber 1 - 7
        """
        try:
            relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
            print("Relay_status {0}".format(relay_state))
            if (relay_state == 0):
                print("Relay Disconnected")
                return True
            else:
                self.ladybird.SetRelayState(1, 2, relay_port, 0)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, 2, relay_port)
                if (relay_state == 0):
                    print("Disconnecting Custom Relay Number {0} Successful".format(relay_port))
                    return True
                else:
                    print("Disconnecting Custom Relay Number {0} Failed".format(relay_port))
                    raise
        except Exception as ex:
            print("Custom Relay Disconnect Error {0}".format(ex))
            raise

    def disconnect_relay(self, relay_num, relay_port):
        try:
            relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
            if (relay_state == 0):
                print("Relay Disconnected")
                return True
            else:
                self.ladybird.SetRelayState(1, relay_num, relay_port, 0)
                time.sleep(1)
                relay_state = self.ladybird.GetRelayState(1, relay_num, relay_port)
                if relay_state == 0:
                    print("Disconnecting Relay Successful")
                    return True
                else:
                    print("Disconnecting Relay Fail")
                    raise
        except Exception as ex:
            print("Relay Disconnect Error {0}".format(ex))
            raise

    def connect_usb_to_sut(self, timeout=None):
        """
        Connect shared USB drive to the system under test.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            print("start to switch usb disk to sut")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000, 0x00)
            time.sleep(2)
            print("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1, 0x2000000, 0x00)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000, 0x4000000)
            time.sleep(3)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            print("Switch_Flash_Disk Usb_To_Sut_Failure {0}".format(ex))
            raise

    def connect_usb_to_host(self, timeout=None):
        """
        Connect shared USB drive to the lab host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            print("start to switch usb disk to host")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000, 0x00)
            time.sleep(2)
            print("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1, 0x2000000, 0x2000000)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000, 0x4000000)
            time.sleep(3)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            print("Switch_Flash_Disk Usb_To_Host_Failure {0}".format(ex))
            raise

    def disconnect_usb(self, timeout=None):
        """
        Dis-connect USB drive From SUT and Host.
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            print("start to Disconnect switch usb from Host and SUT")
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 2)
            self.ladybird.SetGpioDirection(lbHandle, 1, 0x6000000, 0x6000000)
            self.ladybird.SetGpioState(lbHandle, 1, 0x4000000, 0x00)
            time.sleep(2)
            print("Short Relay_1_4")
            self.ladybird.SetGpioState(lbHandle, 1, 0x00, 0x00)
            time.sleep(3)
            # self.self.ladybird.close(lbHandle)
            return True
        except Exception as ex:
            print("Switch_Flash_Disk Usb_To_Host_Failure {0}".format(ex))
            raise

    def set_clear_cmos(self, timeout=None):
        """
        Clears the current configured data with factory setting
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            if (self.conect_relay(1, 3) != True):
                print("Short Clear COMS Pin Failed")
                raise
            else:
                print("Short Clear COMS Pin pass")
            time.sleep(5)
            if (self.disconnect_relay(1, 3) != True):
                print("Open Clear COMS pin failed")
                raise
            else:
                print("Open Clear COMS Jumper Connected")
            return True
        except Exception as ex:
            print("Clear CMOS Failed To Happen {0}".format(ex))
            raise

    def dc_power_on(self, timeout=None):
        """
        :send DC_POWER_ON command to Gpio Turn The Relay to go High for Short Duration which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 1
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("Short switch power button is {0}".format(relay_state))
            time.sleep(1)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("short switch power button is {0}".format(relay_state))
            return True
        except Exception as ex:
            print("Dc-Power ON via Banino Failed To Happen {0}".format(ex))
            raise

    def dc_power_off(self, timeout=None):
        """
        :send DC_POWER_OFF command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 1
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("short switch power off button is {}".format(relay_state))
            time.sleep(5)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("short switch power button is {}".format(relay_state))
            return True
        except Exception as ex:
            print("Dc-Power OFF via Banino Failed To Happen {0}".format(ex))
            raise

    def get_dc_power_state(self):
        """
        This API shields platform and control box difference.
        according to the platform setting in Config module,
        which signals' voltage need to be got are different support.
        Power states dependent on platform power schematic.
        :return:
        On      -   True
        Off     -   NONE
       :exception Banino_Error: Banino Library Throws Error.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        print(power_status)
        if (power_status == "S0"):
            print("S0 State Detected")
            return True
        elif (power_status == "S5"):
            print("S5 State Detected")

    def get_sx_power_state(self):
        """
        :return Actuall state of the platform, combines function of get dc power and ac power
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
            power_status = output.strip()
            print(power_status)
            return power_status
        except Exception as ex:
            print("Error Occured During Banino State Detection {0}".format(ex))
            raise

    def dc_power_reset(self):
        """
        :send DC_Reset command to Gpio To Turn The Relay to go High which physically interact with Front Panel Gpio.
        :return: True or None
        :exception Banino_Error: Banino Library Throws Error.
        """
        try:
            num = 1
            port = 2
            self.ladybird.SetRelayState(1, num, port, 1)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("Short switch reset button is {0}".format(relay_state))
            time.sleep(2)
            self.ladybird.SetRelayState(1, num, port, 0)
            time.sleep(2)
            relay_state = self.ladybird.GetRelayState(1, num, port)
            print("short switch power button is {0}".format(relay_state))
            return True
        except Exception as ex:
            print("Dc-Power ON via Banino Failed To Happen {0}".format(ex))
            raise

    def read_s3_pin(self):
        # type: () -> bool
        """
        Read the state of the S3 pin
        :return: True if S3 pin is indicating SUT is in S3, None otherwise.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        print(power_status)
        if (power_status == "S3"):
            print("S3 State Detected")
            return True
        else:
            print("S3 State is Not Detected")

    def read_s4_pin(self):
        # type: () -> bool
        """
        Read the state of the S4 pin
        :return: True if S4 pin is indicating SUT is in S4, None otherwise.
        """
        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        print(power_status)
        if (power_status == "S4"):
            print("Get S4 State Success")
            return True
        else:
            print("S4 State is Not Detected")

    def get_ac_power_state(self):

        output = os.popen(str("cd ") + self._power_cmd + str("& SxState.exe")).read()
        power_status = output.strip()
        print(power_status)
        if (power_status == "G3"):
            print("G3 State Detected")
        else:
            print("G3 State is Not Detected")
            return True

    def program_jumper(self, state, gpio_pin_number, timeout=""):
        """
        program_jumper controls the gpio pins of Banino
        :param timeout:
        :param gpio_pin_number:
        :param state=set or unset this makes the gpio pin high or low to communicate with the relay
        gpio_pin_number which pins that needs to be programmed
        :return: True
        :exception Banino_Error: Banino Gpio Library Throws Error.
        """
        try:
            if (str(state) == "set"):
                if (self.conect_relay_custom(gpio_pin_number) == True):
                    return True
                else:
                    return False
            elif (str(state) == "unset"):
                if (self.disconnect_relay_custom(gpio_pin_number) == True):
                    return True
                else:
                    return False
        except Exception as ex:
            print("Failed to " + str(state) + " Jumper for Custom Relay Group 2 Channel {0}{1}".format(ex,
                                                                                                                 gpio_pin_number))
            raise

    def chip_flash(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the latest time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is firmware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if self.conect_relay_custom(1) != True:
            print("connect VCC relay fail, please check the hard connection")
            return False
        if self.conect_relay_custom(3) != True:
            print("connect VCC relay fail, please check the hard connection")
            return False
        try:
            print("Starting to do Flash IFWI with mentioned Version {0}".format(image_name))
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 3)
            print("{0}".format(lbHandle))
            flashDevice = 0
            flashStartAddress = 0
            image_namepath = path + image_name
            filePath = ctypes.create_string_buffer(bytes(image_namepath, 'utf-8'))
            writeSize = os.path.getsize(filePath.value)
            print("{0} object, size {1}".format(filePath, writeSize))
            fileOffset = 0
            result = 1
            result = self.ladybird.FlashReady(lbHandle, ctypes.c_char(flashDevice))
            if (result != 0):
                print("FlashReady:{}, IFWI SPI Chip not Detected".format(result))
                return False
            else:
                print("FlashReady:{}, IFWI SPI Chip have Detected".format(result))

            print("Start to Erase SPI flash Chip")
            result = self.ladybird.FlashErase(lbHandle, ctypes.c_char(flashDevice))
            if (result != 0):
                print("FlashErase:{}, Erase IFWI SPI chip Erase fail".format(result))
                return False
            else:
                print("FlashErase:{}, Erase IFWI chip passed ".format(result))
            print("Start to Write IFWI file to flash")
            result = self.ladybird.FlashWriteFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize,
                                                  filePath, fileOffset)
            if (result != 0):
                print("FlashWriteFile:{}, Burning IFWI SPI chip fail".format(result))
                return False
            else:
                print("FlashWriteFile:{}, Burning IFWI SPI chip pass".format(result))
            if (self.chip_write_verification_ifwi == False):
                print("Skipped to Verify SPI IFWI Chip")
            else:
                print("Start to Verify write file")
                result = self.ladybird.FlashVerifyFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress,
                                                       writeSize, filePath, fileOffset)
                if (result != 0):
                    print("FlashVerifyFile:{}, Verify IFWI SPI chip fail".format(result))
                    return False
                else:
                    print("FlashVerifyFile:{}, Verify IFWI SPI chip pass".format(result))
            print("Flash IFWI successful")
            self.ladybird.Close(lbHandle)
            return True
        except Exception as ex:
            print("Error --> {0}".format(ex))
            return False
        finally:
            if (self.disconnect_relay_custom(1) != True):
                print("disconnect VCC relay fail")
                return False
            if (self.disconnect_relay_custom(3) != True):
                print("disconnect VCC relay fail")
                return False

    def chip_flash_bmc(self, path=None, image_name=None):
        """
        This function takes care of identifying and erasing and writing a new image from a location.
        it takes the ifwi image or the bmc image based on the modification/creation time it is going to take the latest time by default of the image.
        Image for flashing will be taken from the "+str(root)+"/firmware/ folder name is firmware from this the image will be taken.
        path in this are fixed path even though folders don't exists it will created it,2nd time run it will copy them
        """
        if self.conect_relay(1, 5) != True:
            print("connect VCC relay fail, please check the hard connection")
            return False
        try:
            print("Starting to do Flash BMC with mentioned Version {0}".format(image_name))
            lbHandle = self.ladybird.OpenByBaninoNumber(1, 1)
            flashDevice = 0
            flashStartAddress = 0
            image_namepath = path + image_name
            filePath = ctypes.create_string_buffer(bytes(image_namepath, 'utf-8'))
            writeSize = os.path.getsize(filePath.value)
            print("{0} object, size {1}".format(filePath, writeSize))
            fileOffset = 0
            result = 1
            result = self.ladybird.FlashReady(lbHandle, ctypes.c_char(flashDevice))
            if (result != 0):
                print("FlashReady:{}, BMC Chip not Detectected".format(result))
                return False
            else:
                print("FlashReady:{}, BMC Chip have Detected".format(result))
            print("Start to Erase flash")
            result = self.ladybird.FlashErase(lbHandle, ctypes.c_char(flashDevice))
            if (result != 0):
                print("FlashErase:{}, Erase bmc chip Erase fail".format(result))
                return False
            else:
                print("FlashErase:{}, Erase bmc chip passed ".format(result))
            print("Start to Write BMC file to flash")
            result = self.ladybird.FlashWriteFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress, writeSize,
                                                  filePath, fileOffset)
            if (result != 0):
                print("FlashWriteFile:{}, Burning bmc chip fail".format(result))
                return False
            else:
                print("FlashWriteFile:{}, Burning bmc chip pass".format(result))
            if (self.chip_write_verification_bmc == False):
                print("Skipped to Verify SPI BMC Chip")
            else:
                print("Start to Veritfy write file")
                result = self.ladybird.FlashVerifyFile(lbHandle, ctypes.c_char(flashDevice), flashStartAddress,
                                                       writeSize,
                                                       filePath, fileOffset)
                if (result != 0):
                    print("FlashVerifyFile:{}, Verify BMC chip fail".format(result))
                    return False
                else:
                    print("FlashVerifyFile:{}, Verify BMC chip pass".format(result))
            print("Flash BMC successfully verified")
            self.ladybird.Close(lbHandle)
            return True
        except Exception as ex:
            print("Error --> {0}".format(ex))
            return False
        finally:
            if (self.disconnect_relay(1, 5) != True):
                print("disconnect VCC relay fail")
                return False

banino = BaninoDriver()
def shutdown(timeoutoff=None):
    banino = BaninoDriver()
    if(banino.dc_power_off(timeoutoff) == True):
        return True
    else:
        return False

def wake_up(timeouton=None):
    banino = BaninoDriver()
    if(banino.dc_power_on(timeouton) == True):
        return True
    else:
        return False

def clearcmos():
    if(banino.set_clear_cmos() == True):
        return True
    else:
        return False

def dcdetection():
    if(banino.get_dc_power_state() == True):
        return True
    else:
        return False

def reboot():
    if(banino.dc_power_reset() == True):
        return True
    else:
        return False

def acdetection():
    if(banino.get_ac_power_state() == True):
        return True
    else:
        return False

def usb_switch_to_sut():
    if (banino.connect_usb_to_sut() == True):
        return True
    else:
        return False

def usb_disconnect():
    if (banino.disconnect_usb() == True):
        return True
    else:
        return False

def usb_switch_to_host():
    if (banino.connect_usb_to_host() == True):
        return True
    else:
        return False

def flash_ifwi(name):
    if(banino.chip_flash(path="C:\\flask_firmware\\ifwi\\",image_name=name) == True):
        return True
    else:
        return False

def flash_bmc(name):
    if(banino.chip_flash_bmc(path="C:\\flask_firmware\\bmc\\",image_name=name) == True):
        return True
    else:
        return False

def update():
    try:
        subprocess.check_output(
            "curl -X GET bdcspiec010.gar.corp.intel.com/files/flask_windows/flask.zip --output C:\\flask.zip", shell=True)
        return True
    except Exception as ex:
        return ex

class UsbblasterDriver():
    def __init__(self):
        self.__cpld_app_path = r"C:\intelFPGA_pro\18.1\qprogrammer\\bin64"

    def health_status_check_usbblaster(self):
        self.__cpld_app_path += "\quartus_pgm.exe"
        cmd = (self.__cpld_app_path + " -c 1 -a")
        try:
            ret = subprocess.check_output(cmd, shell=True)
            print("{0}".format(ret))
            if "Quartus Prime Programmer was successful. 0 errors, 0 warnings" in str(ret):
                print("Quartus Programming USB Blaster is Detected In Host Machine")
                return True
        except Exception as ex:
            print("Errors Quartus USB Blaster Is Not Detected {0}".format(ex))
            return False

    def chip_flash_primary(self, path=None, image_name=None):
        if(self.health_status_check_usbblaster() != True):
            return False
        cpld_image_name = path+"\\"+image_name
        cmd=(self.__cpld_app_path+" -c 1 --mode=JTAG --operation="+"\"p;"+cpld_image_name+"\"")
        try:
            print("CPLD Primary Frimware Flashing Is In Progress")
            ret=subprocess.check_output(cmd,shell=True)
            print("output {0}".format(ret))
            if "0 errors, 0 warnings" in str(ret):
                print("CPLD Flashing for Primary Chip is Successful")
                return True
            else:
                print("Failed To Flash CPLD Primary Chip")
                return False
        except Exception as ex:
            print("Errors Caught During CPLD Primary firmware Flashing {0}".format(ex))
            raise

    def chip_flash_secondary(self, path=None, image_name=None):
        if (self.health_status_check_usbblaster() != True):
            return False
        cpld_image_name = path + "\\" + image_name
        cmd = (self.__cpld_app_path + " -c 1 --mode=JTAG --operation=" + "\"p;" + cpld_image_name + "\"@2")
        try:
            print("CPLD  Secondary Frimware Flashing Is In Progress")
            ret = subprocess.check_output(cmd, shell=True)
            print("output {0}".format(ret))
            if "0 errors, 0 warnings" in str(ret):
                print("CPLD Flashing for Secondary Chip is Successful")
                return True
            else:
                print("Failed To Flash CPLD Secondary Chip")
                return False
        except Exception as ex:
            print("Errors Caught During CPLD Secondary firmware Flashing {0}".format(ex))
            raise

    def read_postcode(self):
        self.__cpld_app_path = r"C:\intelFPGA_pro\18.1\qprogrammer\bin64\quartus_stp_tcl -t rfat_modified.tcl"
        try:
            self.__cpld_app_path = "cd C:\postcode &&" + self.__cpld_app_path
            print("log",self.__cpld_app_path)
            output = Popen(self.__cpld_app_path, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            cmd = output.stdout.read()
            cmd = str(cmd)
            ind = (str(cmd).index("BIOS CODE:"))
            post_code = (cmd[int(ind + 11):int(ind + 13)])
            print(post_code)
            return True,post_code
        except Exception as ex:
            #print("Errors Caught While Reading Postcode {0}".format(ex))
            return False

cpld =UsbblasterDriver()
def platform_postcode():
    try:
        ret=cpld.read_postcode()
        print("aaaa",ret)
        if(ret[0] == True):
            return ret[1]
        else:
            return "N/A"
    except Exception as ex:
        #print(ex)
        return "N/A"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def homepage():
    ret = subprocess.check_output("hostname", shell=True)
    ret = ret.strip()
    return "Version 1.0 20-jan-2021 Neptune_Raptor"

@app.route('/help',methods=['GET'])
@app.route('/options',methods=['GET'])
def informer():
    return (
            r"img_upload ---- uploading .rom/.bin From your Device To HostMachine ""\n""curl -T full_location_path of image_name.bin|.rom -X POST http://" + str(
        ipadd) + "/img_upload/ifwi/ or bmc/  \n\t \nwrite_chip/bmc/xxx.rom/ ----- Flashes the choosen BMC image under \"C:\\flask_firmware\\bmc\" \n\t \nwrite_chip/ifwi/xxx.bin/ ----- Flashes the choosen IFWI image under \"C:\\flask_firmware\ifwi\"  \ndcpower/0 ------- To DC Turn Off Platform \ndcpower/1 ------- To DC Turn On Platform \nacpower/config/outlet_number/pdu_ip/pdu_username/pdu_password ------ Setting up PDU \n     eg:- acpower/config/x/10.xx.xx.xx/Adminstrator/intel@123 \nacpower/0 ------- To AC Power Turn Off Platform \nacpower/1 ------- To AC Power Turn On Platform \nclearcmos \nreboot \npostcode \nusb2host ----- USB Device TO HOST Machine \nusb2sut ----- USB Device TO HOST Machine \nusbdiscnt ----- USB DISCONNECT FROM BOTH SUT AND HOST \ndcdetect \nacdetect \nupdate ----- Updates Latest Flask Service")
@app.route('/',methods=['GET','POST'])
def index():
    if(required.method == 'POST'):
        some_json = request.get_json()
        return jsonify({'you sent':some_json}),201
    else:
        return jsonify({"Power on"})

@app.route('/clearcmos',methods=['GET'])
def platform_clearcmos():
    if(clearcmos()==True):
        return "ClearCmos Command Issued"
    else:
        return "N/A"

@app.route('/acpower/config/<string:outlet_number>/<string:pdu_ip>/<string:pdu_username>/<string:pdu_password>',methods=['GET'])
def pdu_config(outlet_number,pdu_ip,pdu_username,pdu_password):
    try:
        if(pdu_configure(outlet_number,pdu_ip,pdu_username,pdu_password) == True):
                return str("PDU configured With Outlet --> {0} \nPDU_IP_Address --> {1}\npdu_username --> {2}\npdu_password --> {3}").format(outlet_number,pdu_ip,pdu_username,pdu_password)
        else:
            return "Failed to Configure PDU"
    except Exception as ex:
        return str("Make sure PDU Credentials are Proper")

@app.route('/postcode',methods=['GET'])
def platform_pstcode():
    ret=platform_postcode()
    if(ret=="N/A"):
        return "N/A"
    else:
        return ret
@app.route('/dcdetect',methods=['GET'])
def platform_dcpower():
    if dcdetection()==True:
        return "DC power detected"
    else:
        return "N/A"

@app.route('/reboot',methods=['GET'])
def platform_reboot():
    if(reboot()==True):
        return "Reboot Command Issued"

@app.route('/update',methods=['GET'])
def flask_update():
    if(update()==True):
        return "Flask SCript Updated Command Issued"

@app.route('/acdetect',methods=['GET'])
def platform_acpower():
    if(acdetection()==True):
        return "AC power detected"
    else:
        return "N/A"

@app.route('/usb2host', methods=['GET'])
def usb2host():
    if (usb_switch_to_host() == True):
        return "USB Switch to Host Done"
    else:
        return "Failed to Switch the Usb To Host"


@app.route('/usbdiscnt', methods=['GET'])
def usbdisconnect():
    if (usb_disconnect() == True):
        return "USB Disconnect Done"
    else:
        return "Failed to Disconnect USB"


@app.route('/usb2sut', methods=['GET'])
def usb2sut():
    if (usb_switch_to_sut() == True):
        return "USB Switch to SUT Done"
    else:
        return "Failed to Switch the Usb To SUT"

@app.route('/acpower/num/',defaults={'timeout':None},methods=['GET'])
@app.route('/acpower/<int:num>',methods=['GET'])
@app.route('/acpower/<int:num>/<int:timeout>',methods=['GET'])
def acpower(num,timeout=None):
    if num == 0:
        if(acofffromacon(timeoutoff=timeout)==True):
            return "Power Turned OFF and Verified"
        else:
            return "AC Power OFF Failed"
    elif num == 1:
        if(aconfromacoff(timeouton=timeout)==True):
            return "Power Turned ON and Verified"
        else:
            return "AC Power ON Failed"
    else:
        return "Invalid Input:-\n 0 is Turn Power OFF \n 1 is Turn Power On"

@app.route('/dcpower/num/',defaults={'timeout':None},methods=['GET'])
@app.route('/dcpower/<int:num>',methods=['GET'])
@app.route('/dcpower/<int:num>/<int:timeout>',methods=['GET'])
def dcpower(num,timeout=None):
    if num == 0:
        if(shutdown(timeoutoff=timeout)==True):
            return "DC Power Turned OFF and Verified"
        else:
            return "Failed To DC Power Turned OFF"
    elif num == 1:
        if(wake_up(timeouton=timeout)==True):
            return "Dc Power Turned ON and Verfied"
        else:
            return "Failed To DC Power Turned ON"
    else:
        return "Invalid Input:-\n 0 is Turn Power OFF \n 1 is Turn Power On"

@app.route("/img_upload/<type>/<filename>", methods=["POST"])
def upload_img_file(type,filename):
    try:
        if "/" in filename:
            abort(400, "no subdirectories directories allowed")
        if(type.lower() == "bmc"):
            with open(os.path.join(UPLOAD_DIRECTORY+str("bmc"), filename), "wb") as fp:
                fp.write(request.data)
        elif(type.lower() == "ifwi"):
            with open(os.path.join(UPLOAD_DIRECTORY+str("ifwi"), filename), "wb") as fp:
                fp.write(request.data)
        return str("uploading Image "+str(filename)+"... Completed")
    except Exception as ex:
        return str("Uploading Image Failed {0}".format(ex))

@app.route('/write_chip/<string:type>/<string:img>',methods=['GET'])
@app.route('/write_chip/',defaults={'img':None},methods=['GET'])
@app.route('/write_chip/',defaults={'type':None},methods=['GET'])
def chip_write(img=None,type=None):
    try:
        start = time.time()
        if(type.lower() == "ifwi"):
            if(flash_ifwi(img) == True):
                end2 = time.time()
                turn_off_via_cmd = (abs(start - end2))
                turn_off_via_cmd = ("{:05.2f}".format(turn_off_via_cmd))
                return str("Flashing IFWI Chip With "+str(img)+"Image ... Successfull It Took {0}".format(turn_off_via_cmd))
            else:
                return str("Flashing Failed For IFWI Chip || Make sure Platform is Turned OFF || Image Name & Available")
        elif(type.lower() == "bmc"):
            if(flash_bmc(img) == True):
                end2 = time.time()
                turn_off_via_cmd = (abs(start - end2))
                turn_off_via_cmd = ("{:05.2f}".format(turn_off_via_cmd))
                return str("Flashing BMC Chip With " + str(img) + "Image ... Successful It Took {0}".format(turn_off_via_cmd))
            else:
                return str("Flashing Failed For BMC Chip || Make sure Platform is Turned OFF || Image Name & Available")
    except Exception as ex:
        return str("Do Give Proper Syntax  write_chip/chip_type/image_name \nchip_type ifwi or BMC \nifwi_image_name.bin or bmc_img_name.rom")
        return str("chip_type ifwi or BMC")

if __name__ == "__main__":
    app.run(host="0.0.0.0",threaded=True,port=80,debug=True)
