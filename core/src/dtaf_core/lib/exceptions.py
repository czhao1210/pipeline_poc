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


class ItemNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super(ItemNotFoundException, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(ItemNotFoundException, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(ItemNotFoundException, self).__getslice__(start, stop)


class AuthenticationException(Exception):
    def __init__(self, *args, **kwargs):
        super(AuthenticationException, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(AuthenticationException, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(AuthenticationException, self).__getslice__(start, stop)


class ConnectionFailureException(Exception):
    def __init__(self, *args, **kwargs):
        super(ConnectionFailureException, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(ConnectionFailureException, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(ConnectionFailureException, self).__getslice__(start, stop)


class IncorrectKeyException(Exception):
    def __init__(self, *args, **kwargs):
        super(IncorrectKeyException, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(IncorrectKeyException, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(IncorrectKeyException, self).__getslice__(start, stop)


class DriverIOError(IOError):
    """
    Error
    """
    def __init__(self, *args, **kwargs):
        super(DriverIOError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(DriverIOError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(DriverIOError, self).__getslice__(start, stop)


class ControlboxError(DriverIOError):
    """
    Error
    """
    def __init__(self, *args, **kwargs):
        super(ControlboxError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(ControlboxError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(ControlboxError, self).__getslice__(start, stop)


class SoundWaveError(ControlboxError):
    def __init__(self, *args, **kwargs):
        super(SoundWaveError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(SoundWaveError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(SoundWaveError, self).__getslice__(start, stop)

class InputError(ControlboxError):
    def __init__(self, *args, **kwargs):
        super(InputError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(InputError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(InputError, self).__getslice__(start, stop)


class RPiError(ControlboxError):
    def __init__(self, *args, **kwargs):
        super(RPiError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(RPiError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(RPiError, self).__getslice__(start, stop)


class RSC2Error(ControlboxError):
    def __init__(self, *args, **kwargs):
        super(RSC2Error, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(RSC2Error, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(RSC2Error, self).__getslice__(start, stop)


class PduusbError(ControlboxError):
    def __init__(self, *args, **kwargs):
        super(PduusbError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(PduusbError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(PduusbError, self).__getslice__(start, stop)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        super(TimeoutException, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(TimeoutException, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(TimeoutException, self).__getslice__(start, stop)


class InvalidParameterError(Exception):
    def __init__(self, *args, **kwargs):
        super(InvalidParameterError, self).__init__(*args, **kwargs)

    def __getitem__(self, i):
        return super(InvalidParameterError, self).__getitem__(i)

    def __getslice__(self, start, stop):
        return super(InvalidParameterError, self).__getslice__(start, stop)


class OsBootTimeoutException(Exception):
    """Exception raised when the SUT doesn't boot within the expected time period."""


class UnsupportedOsException(Exception):
    """Exception raised when the OS in use is not supported by the OsProvider class or called method."""


class OsStateTransitionException(Exception):
    """Exception raised when the OS fails to change the state of the SUT."""


class OsCommandException(Exception):
    """Generic exception raised when a command cannot be completed."""


class OsCommandTimeoutException(Exception):
    """Exception raised when an OS command times out."""


class DebuggerException(Exception):
    """Base exception class for Silicon debug tool exceptions."""


class ReadBackException(DebuggerException):
    """Exception raised when read-back after a register or memory write fails."""


class RegisterInconsistencyException(DebuggerException):
    """Exception raised when package-level MSRs are not consistent between threads."""


class FlashProgrammerException(Exception):
    """Exception raised when flash emulator cannot complete the requested action."""


class FlashEmulatorException(Exception):
    """Exception raised when flash emulator cannot complete the requested action."""
