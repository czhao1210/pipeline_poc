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
"""
SUT Agent
"""
import codecs
import json
import os
import platform
import signal
import subprocess
import threading
import time
from datetime import datetime
import base64
import six

from sutagent import SutConfig, serial, network
from sutagent.lib import init, delete
from sutagent.lib.globals.data_type import TYPE_STANDBY, TYPE_EXECUTE_ASYNC, \
    TYPE_EXECUTE, TYPE_RESPONSE, TYPE_ENTEROS, TYPE_REBOOT, \
    TYPE_HIBERNATE, TYPE_DELETE, TYPE_SHUTDOWN, TYPE_CLOSE, TYPE_WRITE, TYPE_READ, TYPE_OPEN_FOR_READ, \
    TYPE_OPEN_FOR_WRITE, \
    ENTER_OS_RESUME, ENTER_OS_START_UP
from sutagent.lib.private.serial_transport import sparklogger, Message
from sutagent.serial_auto_detect import SerialAutoDetect

SERIAL_AUTO_DETECT = True if SerialAutoDetect.serial_auto_detect.lower() == "true" else False

if serial:
    if SERIAL_AUTO_DETECT:
        if not SerialAutoDetect.seek_available_port():
            sparklogger.error("No available port to initialize")
            raise Exception("No available port to initialize")
        else:
            SerialAutoDetect.set_config('SUT', 'serial_auto_detect', False)
    init()
    if SERIAL_AUTO_DETECT:
        from sutagent.lib.private import serial_transport

        if six.PY3 or six.PY34:
            from imp import reload
        reload(serial_transport)
elif network:
    from sutagent.lib.private.socket_server_client import sut_eth_message_receive, \
        sut_eth_message_send, SocketError
    from sutagent import IP_ADDRESS, IP_PORT

EXECUTION_THREAD = None
STATE_THREAD = None
TERMINATED = False


def terminal_signal_handler(sig_num, frame):
    """
    receive termination signal by this handle, before exit application, close serial port first.
    then close current running command process, if no process runs, return.

    Linux/Windows have different termination signal, this API will separately handle them.

    :param sig_num: signal number
    :param frame: interrupted stack frame.
    :return:
    """
    global EXECUTION_THREAD
    sparklogger.info("received terminal signal:%s" % sig_num)
    if sig_num == signal.SIGINT or sig_num == signal.SIGTERM or sig_num == signal.SIGABRT:
        if EXECUTION_THREAD:
            sparklogger.info("kill execution...")
            EXECUTION_THREAD.cancel_timer()
            EXECUTION_THREAD.kill()

    if SutConfig().is_linux() and sig_num == signal.SIGSTOP:
        sparklogger.info("sts signal to kill pid %s" % os.getpid())
        os.kill(os.getpid(), 9)

    if SutConfig().is_windows() and sig_num in [signal.SIGBREAK, signal.SIGABRT]:
        sparklogger.info("break or abort signal to kill pid %s" % os.getpid())
        os.popen('taskkill /F /PID ' + str(os.getpid()))

    time.sleep(1)
    global TERMINATED
    TERMINATED = True
    delete()


def register_signal():
    """
    register_signal
    :return:
    """
    signal.signal(signal.SIGINT, terminal_signal_handler)
    signal.signal(signal.SIGTERM, terminal_signal_handler)
    signal.signal(signal.SIGABRT, terminal_signal_handler)


#    if SutConfig().is_linux():
#        signal.signal(signal.SIGSTOP, terminal_signal_handler)
#    elif SutConfig().is_windows():
#        signal.signal(signal.SIGBREAK, terminal_signal_handler)


def send(dict_data, is_response=True):
    """
    send message
    :param dict_data:
    :param is_response:
    :return:
    """
    try:
        json_str = json.dumps(dict_data)
    except Exception as ex:
        sparklogger.error(ex)
        if is_response:
            json_str = json.dumps({TYPE_RESPONSE: [-3, -1, str(ex)]})
        else:
            json_str = json.dumps({TYPE_ENTEROS: [platform.system(), str(ex)]})
    try:
        if serial:
            Message.send(json_str)
        elif network:
            sut_eth_message_send(json_str)
    except Exception as ex:
        sparklogger.error(ex)


def receive(timeout):
    """
    receive message
    :param timeout:
    :return:
    """
    data = None
    message = ''
    try:
        if serial:
            message = Message.receive(timeout)
        elif network:
            message = sut_eth_message_receive(timeout)
        data = json.loads(message)
        sparklogger.debug('receive show data is {}'.format(type(message)))
    except SocketError as error:
        print("ignore network issue")
    return data


class ExecutionThread(object):
    """
    Execution Thread
    """

    def __init__(self, cmd_list):
        self.cmd = cmd_list[0]
        self.timeout = int(cmd_list[1])
        self.proc = None
        self.launch_code = 0
        self.killed = False
        self.timeout_timer = None
        self.output = ''

    def kill(self):
        '''
        if the subprocess if still running, call os.system to terminate the execution subprocess
        :return: True: terminate operation is success. os.system return 0
                 False: os.system doesn't return 0. ## FIXME. how to handle this case.
         '''
        while self.proc and self.proc.poll() is None:
            pid = self.proc.pid
            self.killed = True
            sparklogger.info("will kill process with {pid} pid".format(pid=pid))
            if SutConfig().is_linux():
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                sparklogger.info('execution is killed, since timeout is occurred')
            elif SutConfig().is_windows():
                ret = os.system("TASKKILL /F /T /PID {pid}".format(pid=pid))
                if ret == 0:
                    sparklogger.info('execution is killed, since timeout is occurred')
                else:
                    sparklogger.error('timeout is occurred, but kill execution is failed')
            else:
                sparklogger.info("non-supported os platform")

    def cancel_timer(self):
        """
        cancel timer
        :return:
        """
        if self.timeout_timer and self.timeout_timer.is_alive():
            self.timeout_timer.cancel()

    def enable_timer(self):
        """
        enable timer
        :return:
        """
        self.timeout_timer = threading.Timer(self.timeout, self.kill)
        self.timeout_timer.setDaemon(True)
        self.timeout_timer.start()

    def run(self):
        """
        launch input cmd as a subprocess, and redirect this
        subprocess's output a local temporary file.

        if the subprocess is killed because of kill message which is
        sent by host, the subprocess will be killed by
        this object's.

        if the subprocess is finished, send response message to host.
        if it is killed, should specify the return code.
        if it is normally finished, should read all data from local
        output file and fill it into response message.

        :return:
        """
        sparklogger.info("will execute {cmd}".format(cmd=self.cmd))
        try:
            self.enable_timer()
            preexec_fn = None if SutConfig().is_windows() else os.setsid()
        except OSError as ex:
            preexec_fn = None
            sparklogger.info(ex)
        try:
            if preexec_fn:
                self.proc = subprocess.Popen(self.cmd, shell=True, preexec_fn=preexec_fn,
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                self.proc = subprocess.Popen(self.cmd, shell=True, start_new_session=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = self.proc.stdout.readline()
                print("proc=>{}".format(line))
                if line:
                    if isinstance(line, bytes):
                        line = line.decode('utf-8')
                    self.output += line
                    sparklogger.info("run=>line {}".format(line))
                if self.proc.poll() is not None and not line:
                    try:
                        self.proc.stdout.close()
                    except Exception as ex:
                        sparklogger.error(ex)
                    # self.terminated = True
                    break
        except Exception as ex:
            sparklogger.error(ex)
            self.launch_code = -2

        if self.killed:
            self.launch_code = -1

        self.cancel_timer()

    def response(self):
        """
        response
        :return:
        """
        exitcode = self.proc.returncode if self.proc else -1
        response = {TYPE_RESPONSE: [self.launch_code, exitcode, self.output]}
        return response


class StateHandlerThread():
    """
    this thread only can be create and start while sut agent received hibernate and standby message.
    """
    STATE_STANDBY = 'STANDBY'
    STATE_HIBERNATE = 'HIBERNATE'

    def __init__(self, state):
        self.state = state  # hibernate or standby message
        # super(StateHandlerThread, self).__init__()
        self.psshutdown = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'bin', 'PSTools', 'psshutdown.exe')

    def check_if_resume_from_linux(self, state):
        sparklogger.info("waiting for system resume")
        while True:
            with codecs.open(r'/sys/power/state', "rb", encoding="utf-8") as state_file:
                if state_file.read() == state:
                    return True
            time.sleep(.5)

    def check_if_resume_from_windows(self):
        """
        check_if_resume_from_windows
        :return:
        """
        sparklogger.info("waiting for system resume")
        import wmi
        core_lib = wmi.WMI()
        watcher = core_lib.Win32_PowerManagementEvent.watch_for(EventType=7)
        watcher()
        return True

    def run(self):
        '''
        according to os type and input state to decide
        1. run which to let os enter into specified state
        2. use which method to wait os resume from S3 and S4.
            1). windows: use wmi module to wait for PBT_APMRESUMEAUTOMATIC(0x12) event.
            2). linux: loop monitor /sys/power/state if recovered to OS state
        then send enter os message to host to let host know sut is waked up.

        if waked up, tear down this method.
        :return:
        '''
        if SutConfig().is_linux():
            local_file = codecs.open(r"/sys/power/state", "rb", encoding="utf-8")
            origin = local_file.read()
            local_file.close()
            if self.state == StateHandlerThread.STATE_STANDBY:
                ret = os.system(r"echo mem>/sys/power/state")
                if ret != 0:
                    return
                if self.check_if_resume_from_linux(origin):
                    sparklogger.info("resume from {mode} state".format(mode=self.state))
            elif self.state == StateHandlerThread.STATE_HIBERNATE:
                ret = os.system(r"echo disk>/sys/power/state")
                if ret != 0:
                    return
                if self.check_if_resume_from_linux(origin):
                    sparklogger.info("resume from {mode} state".format(mode=self.state))
            else:
                sparklogger.info("unknown power state")
        elif SutConfig().is_windows():
            if self.state == StateHandlerThread.STATE_STANDBY:
                ret = os.system("{psshutdown} /accepteula /d".format(psshutdown=self.psshutdown))
                if ret != 0:
                    sparklogger.error('fail to enter into {mode} state'.format(mode=self.state))
                    return
                if self.check_if_resume_from_windows():
                    sparklogger.info("resume from {mode} state".format(mode=self.state))
            elif self.state == StateHandlerThread.STATE_HIBERNATE:
                ret = os.system("{psshutdown} /accepteula /h".format(psshutdown=self.psshutdown))
                if ret != 0:
                    sparklogger.error('fail to enter into {mode} state'.format(mode=self.state))
                    return
                if self.check_if_resume_from_windows():
                    sparklogger.info("resume from {mode} state".format(mode=self.state))
            else:
                sparklogger.info("unknown power state")
        else:
            sparklogger.info("non-supported os platform")
        response = {TYPE_ENTEROS: [platform.system(), ENTER_OS_RESUME]}
        send(response, False)


# register terminal and resume handle in main function.
# get SUTAgent configuration information by Config module. create serial
# handle object to open serial port.
#
# Loop receiving message from serial port. currently, SUTAgent only support
# receive execution message. if got such kind of message, launch a
# sub-process to run this command, during it executing, this function should
# read back all output message from sub-process stdout and stderr.
#
# during the command execution, if received a timeout message, then kill the
# command sub-process and response host. if timeout message doesn't received,
# response host when sub-process is completed.


def main():
    """
    Main Entry
    :return:
    """
    global TERMINATED
    global EXECUTION_THREAD
    register_signal()
    if not SERIAL_AUTO_DETECT:
        response = {TYPE_ENTEROS: [platform.system(), ENTER_OS_START_UP]}
        send(response, False)
    fd = None

    while not TERMINATED:
        message = receive(0)
        if message:
            try:
                keys = list(message.keys())
                types = keys[0]
                val = message[types]
                # if type == TYPE_KILL:
                #     global gExecutionTrd
                #     if gExecutionTrd and gExecutionTrd.isAlive():
                #         gExecutionTrd.kill()
                #     else:
                #         sparklogger.warning('received timeout message, but no execution running')
                # elif type == TYPE_EXECUTE:
                if types == TYPE_EXECUTE:
                    # if gExecutionTrd and gExecutionTrd.isAlive():
                    #     gExecutionTrd.kill()
                    #     gExecutionTrd.join()
                    if EXECUTION_THREAD:
                        EXECUTION_THREAD.cancel_timer()
                        EXECUTION_THREAD.kill()
                    EXECUTION_THREAD = ExecutionThread(val)
                    # gExecutionTrd.setDaemon(True)
                    # gExecutionTrd.start()
                    EXECUTION_THREAD.run()

                    send(EXECUTION_THREAD.response())
                    EXECUTION_THREAD = None
                elif types == TYPE_OPEN_FOR_WRITE:
                    try:
                        fd = open(val[0], "wb+")
                        send({TYPE_RESPONSE: [0, 0, "{} is open".format(val[0])]})
                    except FileNotFoundError as err:
                        send({TYPE_RESPONSE: [-1, -1, err]})
                elif types == TYPE_OPEN_FOR_READ:
                    try:
                        fd = open(val[0], "rb")
                        send({TYPE_RESPONSE: [0, 0, "{} is open".format(val[0])]})
                    except FileNotFoundError as err:
                        fd = None
                        send({TYPE_RESPONSE: [-1, -1, err]})
                elif types == TYPE_READ:
                    try:
                        if fd:
                            data = fd.read(102400)
                            msg = base64.b64encode(data).decode('utf-8')
                            send({TYPE_RESPONSE: [0, 0, msg]})
                    except Exception as err:
                        fd = None
                        send({TYPE_RESPONSE: [-1, -1, err]})
                elif types == TYPE_WRITE:
                    try:
                        if fd:
                            data = base64.b64decode(val[0])
                            print("write data into data into file")
                            fd.write(data)
                    except Exception as err:
                        fd = None
                elif types == TYPE_CLOSE:
                    try:
                        if fd:
                            fd.close()
                        send({TYPE_RESPONSE: [0, 0, "file closed"]})
                    except Exception as err:
                        send({TYPE_RESPONSE: [-1, -1, err]})
                    fd = None
                elif types == TYPE_EXECUTE_ASYNC:
                    exec_th = ExecutionThread(val)
                    thrd = threading.Thread(target=exec_th.run)
                    thrd.setDaemon(True)
                    thrd.start()

                    prev = datetime.now()
                    while (datetime.now() - prev).seconds < min(10, val[1]):
                        if exec_th.proc:
                            break
                        time.sleep(0.001)

                    resp = exec_th.response()
                    sparklogger.debug('th.proc.pid {0}'.format(exec_th.proc.pid))
                    if exec_th and exec_th.proc:
                        resp[TYPE_RESPONSE][2] = '{0}'.format(exec_th.proc.pid)
                    else:
                        resp[TYPE_RESPONSE][2] = ''
                    send(resp)
                elif types == TYPE_STANDBY:
                    STATE_THREAD = StateHandlerThread(StateHandlerThread.STATE_STANDBY)
                    STATE_THREAD.run()
                elif types == TYPE_HIBERNATE:
                    STATE_THREAD = StateHandlerThread(StateHandlerThread.STATE_HIBERNATE)
                    STATE_THREAD.run()
                elif types == TYPE_SHUTDOWN:
                    if SutConfig().is_windows():
                        os.system(r'shutdown -s -t 5')
                    elif SutConfig().is_linux():
                        os.system(r'systemctl poweroff')
                    else:
                        sparklogger.info("non-supported os platform")
                    if network:
                        TERMINATED = True

                elif types == TYPE_REBOOT:
                    if SutConfig().is_windows():
                        os.system(r'shutdown -r -t 5')
                    elif SutConfig().is_linux():
                        os.system(r'systemctl reboot')
                    else:
                        sparklogger.info("non-supported os platform")

                elif types == TYPE_DELETE:
                    import socket
                    net_sockect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        net_sockect.connect((IP_ADDRESS, IP_PORT))
                    except BaseException:
                        sparklogger.info('a connection is already deleted')
                    else:
                        sparklogger.info('delete a connection')
                else:
                    sparklogger.error('non--supported message type:{}'.format(type))
                    time.sleep(0.1)
            except Exception as ex:
                sparklogger.error(ex)


if __name__ == '__main__':
    main()
