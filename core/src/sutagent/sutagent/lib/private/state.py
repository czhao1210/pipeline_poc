"""
State defines all the possible environment and power state
"""

from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.private.context import ContextInstance as _ContextInstance
from sutagent.lib.globals.return_code import RET_ENV_FAIL, RET_TEST_FAIL, RET_SUCCESS, RET_INVALID_INPUT
from sutagent.lib.configuration import configuration
import json
import os

POWER_STATE_S0 = r'S0'
POWER_STATE_S3 = r'S3'
POWER_STATE_S4 = r'S4'
POWER_STATE_S5 = r'S5'
POWER_STATE_G3 = r'G3'

ENV_STATE_EFISHELL = r'EFIShell'
ENV_STATE_BIOS_BOOT_MENU = r'BIOS_BOOT_MENU'
ENV_STATE_BIOS_SETUP_MENU = r'BIOS_SETUP_MENU'
ENV_STATE_ENTRY_MENU = r'EntryMenu'
ENV_STATE_WINDOWS = r'Windows'
ENV_STATE_NANO = r'Nano'
ENV_STATE_LINUX = r'Linux'
ENV_STATE_SIMICS = r'Simics'
ENV_STATE_PXE = r'PXE'
ENV_STATE_BIOS_UI = 'BIOS_UI'
ENV_STATE_VMWARE = 'VMkernel'

# Unknown can be valid both for env and power state
STATE_Unknown = r'Unknown'
# NA status is only valid for env state while power state is in S5/G3/S4
STATE_NotAvailable = r'NA'
is_presilicon = configuration.is_presilicon()


def get_entity_name_by_pid(pid):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'entity_map.json'),
              'r') as f:
        map_dict_data = json.load(f)
    entity_name = None
    for k, v in map_dict_data.items():
        if v == pid:
            entity_name = k
            break
    return entity_name


def get_environment_state():
    """
        get current environment state from previous set state result which can be a file or environment variable.

        :return: current environment state
                ENV_STATE_BIOS_SETUP_MENU/ENV_STATE_BIOS_BOOT_MENU/ENV_STATE_EFISHELL/ENV_STATE_ENTRY_MENU

                /ENV_STATE_WINDOWS/ENV_STATE_LINUX/STATE_Unknown/STATE_NotAvailable

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    if configuration.is_cluster_mode():
        state_file_path = _ContextInstance.get(None).state_file
    else:
        if is_presilicon and configuration.is_linux_host():
            pid = os.getpid()
            entity_name = get_entity_name_by_pid(pid)
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
                                           'state_%s.tmp' % entity_name)
        else:
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'state.tmp')
    try:
        fd = open(state_file_path, mode='r')
        dict_env_power_state = json.JSONDecoder().decode("".join(fd.readlines()))
        fd.close()
        return STATE_Unknown if not dict_env_power_state['EnvState'] else dict_env_power_state['EnvState']
    except Exception as ex:
        sparklogger.error(r'%s:get_environment_state' % ex.message)
        return STATE_Unknown


def set_state(state, pid=None):
    if not check_state_available(state):
        return RET_INVALID_INPUT

    dict_env_power_state = {'EnvState': state.env_state, 'PowerState': state.power_state}
    if configuration.is_cluster_mode():
        state_file_path = _ContextInstance.get(None).state_file
    else:
        if is_presilicon and configuration.is_linux_host():
            if not pid:
                pid = os.getpid()
            entity_name = get_entity_name_by_pid(pid)
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
                                           'state_%s.tmp' % entity_name)
        else:
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'state.tmp')
    try:
        fd = open(state_file_path, mode='w+')
        json_state = json.JSONEncoder().encode(dict_env_power_state)
        fd.write(json_state)
        fd.close()
    except Exception as ex:
        sparklogger.error(r'%s:_set_state' % ex.message)
        return RET_ENV_FAIL

    return RET_SUCCESS


def get_simic_power_state():
    """
        get current power state from previous set state result which can be a file or environment variable.

        if the temp file is null, return S0.

        :return: current simics power state POWER_STATE_S0/POWER_STATE_S5/POWER_STATE_G3

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    if configuration.is_cluster_mode():
        state_file_path = _ContextInstance.get(None).state_file
    else:
        if is_presilicon and configuration.is_linux_host():
            pid = os.getpid()
            entity_name = get_entity_name_by_pid(pid)
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
                                           'state_%s.tmp' % entity_name)
        else:
            state_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'state.tmp')
    try:
        fd = open(state_file_path, mode='r')
        dict_env_power_state = json.JSONDecoder().decode("".join(fd.readlines()))
        fd.close()
        return POWER_STATE_S0 if not dict_env_power_state['PowerState'] else dict_env_power_state['PowerState']
    except Exception as ex:
        sparklogger.error(r'%s:get_simic_power_state' % ex.message)
        return POWER_STATE_S0


def check_state_available(state):
    """
    This API will used to check the state is accessible or not on DUT

    :param:     State: Object including env_state and power_state

    :return:    True/False

    :black box valid equivalent class:
                                        State = State(ENV_STATE_EFISHELL,POWER_STATE_S0),

                                        State(ENV_STATE_BIOS_BOOT_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_BIOS_SETUP_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_ENTRY_MENU,POWER_STATE_S0),

                                        State(ENV_STATE_WINDOWS,POWER_STATE_S0),

                                        State(ENV_STATE_WINDOWS,POWER_STATE_S3),

                                        State(ENV_STATE_LINUX,POWER_STATE_S0),

                                        State(ENV_STATE_LINUX,POWER_STATE_S3),

                                        State(STATE_NotAvailable,POWER_STATE_S4),

                                        State(STATE_NotAvailable,POWER_STATE_S5),

                                        State(STATE_NotAvailable,POWER_STATE_G3),

                                        State(STATE_Unknown,POWER_STATE_S0),

                                        State(STATE_Unknown,POWER_STATE_S3),

                                        State(STATE_Unknown,POWER_STATE_S4),

                                        State(STATE_Unknown,POWER_STATE_S5),

                                        State(STATE_Unknown,POWER_STATE_G3),

                                        State(STATE_Unknown,STATE_Unknown),

                                        State(ENV_STATE_SIMICS,POWER_STATE_S0),

                                        State(ENV_STATE_NANO, POWER_STATE_S0)
    :black box invalid equivalent class:
                                        State = State(ENV_STATE_WINDOWS,POWER_STATE_S5),

                                        State(ENV_STATE_LINUX,POWER_STATE_G3)

    estimated LOC = 10
    """
    if (state.env_state, state.power_state) not in [(ENV_STATE_EFISHELL, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_BOOT_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_SETUP_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_ENTRY_MENU, POWER_STATE_S0),
                                                    (ENV_STATE_WINDOWS, POWER_STATE_S0),
                                                    (ENV_STATE_WINDOWS, POWER_STATE_S3),
                                                    (ENV_STATE_LINUX, POWER_STATE_S0),
                                                    (ENV_STATE_LINUX, POWER_STATE_S3),
                                                    (STATE_NotAvailable, POWER_STATE_S4),
                                                    (STATE_NotAvailable, POWER_STATE_S5),
                                                    (STATE_NotAvailable, POWER_STATE_G3),
                                                    (STATE_Unknown, POWER_STATE_S0),
                                                    (STATE_Unknown, POWER_STATE_S3),
                                                    (STATE_Unknown, POWER_STATE_S4),
                                                    (STATE_Unknown, POWER_STATE_S5),
                                                    (STATE_Unknown, POWER_STATE_G3),
                                                    (STATE_Unknown, STATE_Unknown),
                                                    (ENV_STATE_NANO, POWER_STATE_S0),
                                                    (ENV_STATE_SIMICS, POWER_STATE_S0),
                                                    (ENV_STATE_BIOS_UI, POWER_STATE_S0),
                                                    (ENV_STATE_VMWARE, POWER_STATE_S0)]:
        return False
    return True


class State(object):
    """
    SUT State:
        including environment state and power state

        all definitions are in above state code
    """

    def __init__(self, env_state, power_state):
        """
        initialize env state power state

        :param: env_state: env state

        :param: power_state: power state

        :return:

        :black box valid equivalent class: env_state, power_state is None

        :black box valid equivalent class: env_state,power_state is not None

        estimated LOC = 5
        """
        self.env_state = env_state
        self.power_state = power_state
