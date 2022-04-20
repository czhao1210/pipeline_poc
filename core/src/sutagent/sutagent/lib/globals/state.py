"""
State defines all the possible environment and power state
"""
from sutagent.lib.private import state as private_state


def get_environment_state():
    """
        get current environment state from previous set state result which can be a file or environment variable.

        :return: current environment state
                ENV_STATE_BIOS_SETUP_MENU/ENV_STATE_BIOS_BOOT_MENU/ENV_STATE_EFISHELL/ENV_STATE_ENTRY_MENU

                /ENV_STATE_WINDOWS/ENV_STATE_LINUX/STATE_Unknown/STATE_NotAvailable

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    return private_state.get_environment_state()


def get_simic_power_state():
    """
        get current power state from previous set state result which can be a file or environment variable.

        if the temp file is null, return S0.

        :return: current simics power state POWER_STATE_S0/POWER_STATE_S5/POWER_STATE_G3

        :black box equivalent class: file or env variable is null,file or env variable is not null.

        estimated LOC = 10
    """
    return private_state.get_simic_power_state()


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
    return private_state.check_state_available(state)


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
