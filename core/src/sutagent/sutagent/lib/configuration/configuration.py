#
# Configration model
#
# This model provides set_value() and get_value() to update SUT configuration option and get the configuation option value.
#


import sys
from xml.etree import ElementTree as ET
import socket
import re
import platform
from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.globals import return_code
import os
import six
if six.PY2:
    import ConfigParser
if six.PY3 or six.PY34:
    import configparser as ConfigParser


def is_linux_host():
    sparklogger.debug(platform.system())
    return platform.system().lower() == 'linux'


def is_windows_host():
    return platform.system().lower() == 'windows'


def host_platform():
    return platform.system()


def get_argv(name, default=''):
    argv = default
    try:
        for arg in sys.argv:
            argItems = arg.split('--')
            for item in argItems:
                if item.startswith('{0}='.format(name)):
                    argv = item.replace('{0}='.format(name), '').strip()
                    break
    except Exception as ex:
        sparklogger.info('exception: {}'.format(ex))

    finally:
        return argv


SUT_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SUT_config.cfg'))
if is_windows_host():
    SUT_CONFIG_CLIENTS = SUT_CONFIG 
elif is_linux_host():
    SUT_CONFIG_CLIENTS = SUT_CONFIG 
else:
    raise Exception('commonlib for {0} host not define'.format(host_platform()))


class MyConfigParser(ConfigParser.ConfigParser):
    def __init__(self, defaluts=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


def __get_sutconfig_path():
    sparklogger.debug('sut config clients {}'.format(SUT_CONFIG_CLIENTS))
    return SUT_CONFIG_CLIENTS if os.path.exists(SUT_CONFIG_CLIENTS) else SUT_CONFIG


def get_value_from_xml(section, option):
    '''
    This API is used to get the configuration element value.

    :param: section: SUT_config.xml section

    :return: The value of the child and element in the SUT_config.xml file.

    :black box equivalent class: child and element are valid --> return value = RET_SUCCESS;

                                 child is invalid --> return value = RET_INVALID_INPUT;

                                 element is invalid --> return value = RET_INVALID_INPUT.

    '''
    xml_path = get_argv('xml_config')
    try:
        tree = ET.parse(xml_path)
        temp = section.replace(" ", "_")
        if option == '':
            return return_code.RET_INVALID_INPUT
        else:
            value = tree.find(temp + '/' + option).text
            return value

    except Exception:
        sparklogger.info(r'data not fount in xml checking in cfg')
        return get_value_from_cfg(section, option)


def get_value_from_cfg(section, option):
    '''
    This API is used to get the configuration options value.

    :param: section: SUT_config.cfg section

    :return: The input SUT configuration option value.

    :dependency: None

    :black box equivalent class: section and option are valid;

                                 section is invalid --> return RET_INVALID_INPUT;

                                 option is invalid --> return RET_INVALID_INPUT.
    '''

    # Reference code
    # conf = ConfigParser.ConfigParser()
    # conf.read('SUT_config.cfg')
    # value = conf.get(section,option)  # May raise NoOptionError or NoSectionError exception. Capture them and return RET_INVALID_INPUT.
    # return value
    sut_cfg = __get_sutconfig_path()
    if not section or not option or not sut_cfg:
        sparklogger.error(r'input value error,section {0},option {1},sut_cfg {2}'.format(section, option, sut_cfg))
        return return_code.RET_INVALID_INPUT
    conf = ConfigParser.ConfigParser()
    #conf = MyConfigParser()
    try:
        conf.read(sut_cfg)
        return conf.get(section, option)
    except Exception:
        sparklogger.error(r'get_value raise error')
        return return_code.RET_INVALID_INPUT


def set_value_to_xml(section, option, value):
    '''
    This API is used to get the configuration element value.

    :param: section: SUT_config.xml section

    :We can change the value of a element

    :black box equivalent class: child and element are valid --> return value = RET_SUCCESS;

                                 child is invalid --> return value = RET_INVALID_INPUT;

                                 element is invalid --> return value = RET_INVALID_INPUT.


    '''

    xml_path = get_argv('xml_config')
    try:
        tree = ET.parse(xml_path)
        temp = section.replace(" ", "_")
        if option == '':
            return return_code.RET_INVALID_INPUT
        else:
            tree.find(temp + '/' + option).text = value
            tree.write(xml_path)
            sparklogger.debug(r'set_value successfully changed the value')
            return return_code.RET_SUCCESS
    except Exception:
        sparklogger.info(r'data not found in xml file checking in cfg file')
        return set_value_to_cfg(section, option, value)


def set_value_to_cfg(section, option, value):
    '''
    This API is used to set value of a SUT configure option.

    1. Please check the input parameter to see if it is a configure option in SUT_config.cfg file. If not, return RET_INVALID_INPUT.

    2. Write the value to the correct configure option in SUT_config.cfg file.

    3. Read the configure file again to see if the configuration option value has been set correctly. If not correct, return RET_ENV_FAIL.

    :param: section: SUT_config.cfg section

            option: config option in one config section of SUT_config.cfg

            value: config option value

    :return:RET_SUCCESS: successful to set value

            RET_INVALID_INPUT: failed to set value due to invalid input

            RET_ENV_FAIL: failed to set value

    :dependency: None

    :black box equivalent class: section and option are valid --> return value = RET_SUCCESS;

                                 section is invalid --> return value = RET_INVALID_INPUT;

                                 option is invalid --> return value = RET_INVALID_INPUT.

                                 return value  = RET_ENV_FAIL
    '''

    # Reference code
    # conf = ConfigParser.ConfigParser()
    # fp = open('SUT_config.cfg', 'w')
    # conf.write(fp)
    # conf.set(section,option,value)    # May raise exception NoSectionError. Capture it and return RET_INVALID_INPUT.
    # fp.close()
    sut_cfg = __get_sutconfig_path()

    if not section or not option or not value or not sut_cfg:
        sparklogger.error(r'input value error,section {0},option {1},value {2},sut_cfg {3}'.format(section, option, value, sut_cfg))
        return return_code.RET_INVALID_INPUT
    #conf = ConfigParser.ConfigParser()
    conf = MyConfigParser()
    try:
        conf.read(sut_cfg)
        if not conf.has_section(section):
            sparklogger.error(r'not have section {0}'.format(section))
            return return_code.RET_INVALID_INPUT
        conf.set(section, option, value)
        with open(sut_cfg, 'w') as f:
            conf.write(f)
        sparklogger.debug(r'set_value success end')
        return return_code.RET_SUCCESS
    except Exception:
        sparklogger.error(r'set_value raise error')
        return return_code.RET_ENV_FAIL


def set_value(section, option, value):
    '''
    This API is used to set value to either SUT config file or SUT xml file .

    1. If the xml_config option is passed from the command line then this API will set the value in the SUT xml file for the given section.

        a. If the given section is found in SUT xml file the it will set the value of the section for that particular option.

        b. If the given section is not found in SUT xml file the it will look that section in SUT config file and if it found it will set the value of the section for that particular option.

        c. If the given section is not found in SUT xml file and SUT config file both then it will return invalid input.

    2. If the xml_config option is not passed from the command line then this API will set the value directly in the SUT config file.

        a. If the given section is found in SUT config file then it will set the value of the section for that particular option.

        b. If the given section is not found in SUT config file then it will return invalid input.


    3. param: section: SUT_config.cfg or SUT_config.xml section

            option: config option in one config section of SUT_config.cfg or SUT_config.xml

            value: config option value in SUT_config.cfg or SUT_config.xml

    4. return:RET_SUCCESS: successful to set value

            RET_INVALID_INPUT: failed to set value due to invalid input
    '''

    for item in sys.argv:
        arg = item.split('=')[0]
        if '--xml_config' in arg:
            val = set_value_to_xml(section, option, value)
            break
    else:
        sparklogger.info("data is loading from cfg file")
        val = set_value_to_cfg(section, option, value)

    return val


def get_value(section, option):
    '''
    This API is used to get value from either SUT config file or SUT xml file .

    1. If the xml_config option is passed from the command line then this API will get the value in the SUT xml file for the given section.

        a. If the given section is found in SUT xml file the it will get the value of the section for that particular option.

        b. If the given section is not found in SUT xml file the it will look that section in SUT config file and if it found it will get the value of the section for that particular option.

        c. If the given section is not found in SUT xml file and SUT config file both then it will return invalid input.

    2. If the xml_config option is not passed from the command line then this API will get the value directly in the SUT config file.

        a. If the given section is found in SUT config file then it will get the value of the section for that particular option.

        b. If the given section is not found in SUT config file then it will return invalid input.


    3. param: section: SUT_config.cfg or SUT_config.xml section

            option: config option in one config section of SUT_config.cfg or SUT_config.xml

            value: config option value in SUT_config.cfg or SUT_config.xml

    4. return: return value = RET_INVALID_INPUT.
               return value = Value of the section's option.
    '''

    for item in sys.argv:
        arg = item.split('=')[0]
        if '--xml_config' in arg:
            val = get_value_from_xml(section, option)
            break
    else:
        sparklogger.info("data is loading from cfg file")
        val = get_value_from_cfg(section, option)

    return val


def get_sut_platform():
    platform = os.getenv('SUT.platform') if \
        os.getenv('SUT.platform') else get_value('Platform Info', 'platform')

    if platform == return_code.RET_INVALID_INPUT:
        return ''

    return platform


def get_simics_configuration():
    platform = get_sut_platform()
    if not platform:
        platform = 'Default'

    default_section_name = 'Platform.%s' % 'Default'
    section_name = 'Platform.%s' % platform
    sut_cfg = __get_sutconfig_path()

    simics_configuration = {}
    simics_script = ''
    conf = MyConfigParser()
    try:
        flag = 'simics.'
        conf.read(sut_cfg)
        try:
            for opt, value in conf.items(section_name):
                sparklogger.debug('{0}:{1}'.format(opt, value))
                opt = opt.strip()
                if not re.search('^%s' % flag, opt.lower()):
                    continue

                if opt[len(flag):].lower() == 'launch_script':
                    simics_script = str(value.strip())
                    continue

                simics_configuration["${0}".format(opt[len(flag):])] = str(value.strip())
        except Exception as ex:
            sparklogger.debug(ex)

        if simics_configuration or simics_script:
            return simics_configuration, simics_script

        for opt, value in conf.items(default_section_name):
            sparklogger.debug('{0}:{1}'.format(opt, value))
            opt = opt.strip()
            if not re.search('^%s' % flag, opt.lower()):
                continue

            if opt[len(flag):].lower() == 'launch_script':
                simics_script = str(value.strip())
                continue

            simics_configuration["${0}".format(opt[len(flag):])] = str(value.strip())

        return simics_configuration, simics_script
    except Exception as ex:
        sparklogger.error(r'get_value raise error {0}'.format(ex))
        return None, None


def get_platform_item(item_name):
    sparklogger.debug('item_name={0} '.format(item_name))

    platform = get_sut_platform()
    sparklogger.debug('platform={0}'.format(platform))
    if not platform or platform == return_code.RET_INVALID_INPUT:
        platform = 'Default'

    default_section_name = 'Platform.Default'
    section_name = 'Platform.%s' % platform

    value = get_value(section_name, item_name)
    sparklogger.debug('value={0}'.format(value))
    if value != return_code.RET_INVALID_INPUT:
        return value

    value = get_value(default_section_name, item_name)
    sparklogger.debug('value={0}'.format(value))
    return value


def is_presilicon():
    silicon = os.getenv('SUT.silicon') if os.getenv('SUT.silicon') else \
        get_value('Platform Info', 'silicon')

    sparklogger.debug('SILICON {0}'.format(silicon))
    if silicon == return_code.RET_INVALID_INPUT:
        sparklogger.debug('SILICON False 1')
        return False

    if silicon.strip().lower() == 'presilicon':
        sparklogger.debug('SILICON true 1')
        return True

    sparklogger.debug('SILICON false 2')
    return False


def get_simics_port_name(entity=None):
    if is_windows_host():
        port = get_value("Simics", "ComPort")
    elif is_linux_host():
        if not entity:
            port = get_value('Simics', 'comport_linux')
        else:
            port = entity['comport_linux']
    else:
        raise Exception('host platform is {0}, not config'.format(host_platform()))

    if port == return_code.RET_INVALID_INPUT:
        return ''

    return port


def get_simics_extend_port_name(entity=None):
    if is_windows_host():
        port = get_value("Simics", "Extend_ComPort")
    elif is_linux_host():
        if not entity:
            port = entity['extend_comport_linux']
        else:
            port = get_value("Simics", "Extend_ComPort_Linux")
    else:
        raise Exception('host platform is {0}, not config'.format(host_platform()))

    if port == return_code.RET_INVALID_INPUT:
        return ''

    return port


def get_main_port_name(entity=None):
    if is_windows_host():
        port = get_value('Main Serial Port Configuration', 'port')
    elif is_linux_host():
        if not entity:
            port = get_value('Main Serial Port Configuration', 'port_Linux')
        else:
            port = entity['Main_serial_port_Linux']
    else:
        raise Exception('host platform is {0}, not config'.format(host_platform()))

    if port == return_code.RET_INVALID_INPUT:
        return ''

    return port


def get_sutagent_port_name(entity=None):
    if is_windows_host():
        port = get_value('SUTAgent Serial Port Configuration', 'port')
    elif is_linux_host():
        if not entity:
            port = get_value('SUTAgent Serial Port Configuration', 'port_Linux')
        else:
            port = entity['SUTAgent_port_Linux']
    else:
        raise Exception('host platform is {0}, not config'.format(host_platform()))

    if port == return_code.RET_INVALID_INPUT:
        return ''

    return port


def get_controlbox_serial_port_name():
    if is_windows_host():
        port = get_value('ControlBox Serial Port Configuration', 'port')
    elif is_linux_host():
        port = get_value('ControlBox Serial Port Configuration', 'port_Linux')
    else:
        raise Exception('host platform is {0}, not config'.format(host_platform()))

    if port == return_code.RET_INVALID_INPUT:
        return ''

    return port


def main_log_raw_data():
    log_raw_data = get_value('Main Serial Port Configuration', 'log_raw_data')
    if log_raw_data == return_code.RET_INVALID_INPUT:
        return True

    if log_raw_data.lower() == 'true':
        return True
    else:
        return False


def isPortFree(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
    except Exception as e:
        sock.close()
        print(e)
        return False
    sock.close()
    return True


def get_cl_host_client_port():
    try:
        __simics_client_port = int(get_value('Simics', 'ClientPort'))
    except Exception:
        __simics_client_port = 60221
    while True:
        if isPortFree(__simics_client_port):
            break
        else:
            __simics_client_port += 1
    sparklogger.debug('CURENT host Receive port = {0}'.format(__simics_client_port))
    return __simics_client_port


def get_open_telnet_timeout(pid):
    try:
        __timeout = int(get_value('Simics', 'Telnet_Session_Timeout'))
        if not (isinstance(__timeout, int) and __timeout > 1):
            print('Warning: Please set Telnet session timeout to integer greater than 1! Will be set to default')
            __timeout = 120
    except BaseException:
        __timeout = 120

    print('Telnet Session Timeout set to = {0} second(s)'.format(__timeout))
    return __timeout


def get_cl_host_service_port():
    try:
        __simics_service_port = get_value('Simics', 'ServicePort')
        if not __simics_service_port or __simics_service_port == return_code.RET_INVALID_INPUT:
            raise Exception('')
    except BaseException:
        __simics_service_port = 60122

    print('CURENT host Send port = {0}'.format(__simics_service_port))
    return __simics_service_port


def get_sut_ssh_config():
    try:
        ssh_ip = get_value('SUT Connection', 'ssh_ip')
        if not ssh_ip or ssh_ip == return_code.RET_INVALID_INPUT:
            raise Exception('')
    except Exception:
        ssh_ip = None

    if not ssh_ip:
        return None, None, None, None

    try:
        ssh_port = get_value('SUT Connection', 'ssh_port')
        if not ssh_port or ssh_port == return_code.RET_INVALID_INPUT:
            raise Exception('')
        ssh_port = int(ssh_port)
    except Exception:
        ssh_port = 22

    try:
        ssh_username = get_value('SUT Connection', 'ssh_username')
        if not ssh_username or ssh_username == return_code.RET_INVALID_INPUT:
            raise Exception('')
    except Exception:
        ssh_username = ''

    try:
        ssh_password = get_value('SUT Connection', 'ssh_password')
        if not ssh_password or ssh_password == return_code.RET_INVALID_INPUT:
            raise Exception('')
    except Exception:
        ssh_password = ''

    return ssh_ip, ssh_port, ssh_username, ssh_password


def is_cluster_mode():
    try:
        work_mode = os.getenv('sut_work_mode'.upper(), '')
        if work_mode.lower() == 'cluster':
            return True

        return False
    except Exception as ex:
        raise ex


def get_log_path():
    log_path = os.getenv('CAF_CASE_LOG_PATH') if os.getenv('CAF_CASE_LOG_PATH') else os.getenv('LC_RESULT_PATH')
    if not log_path:
        if is_windows_host():
            log_path = r'C:\Temp'
        elif is_linux_host():
            log_path = r'/tmp'
        else:
            raise Exception('platform not config {0}'.format(host_platform()))

        if not os.path.exists(log_path):
            os.mkdir(log_path)

    return log_path


def state_file():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'state.tmp')
