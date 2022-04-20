import threading
import xml.etree.ElementTree as ET

from dtaf_core.drivers.internal.sol_driver import SolDriver


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)

    warn = warning
    fatal = critical


log = _Log()

cnf_normal = ET.fromstring("""
                        <sol>
                            <address>10.239.181.194</address>
                            <port>2200</port>
                            <timeout>120</timeout>
                            <credentials user="root" password="0penBmc"/>
                        </sol>
""")


class SolDriverSub(SolDriver):
    def __init__(self, cnf_normal, log):
        self._addressed = '10.239.181.194'
        self._serial_lock = threading.Lock()
        self._serial = SerialMock(self)
        self._sol_ssh = SolSSHMock()
        self._push_to_all_buffer = PushToAllBufferMock
        self._READ_SIZE = 1024
        self._log = log


def PushToAllBufferMock(*args, **kwargs):
    return True


class SerialMock():
    def __init__(self, fa=None, *args, **kwargs):
        self.number = 0
        self.fa = fa

    def close(self, *args, **kwargs):
        return True

    def recv_ready(self, *args, **kwargs):
        return "b"

    def recv(self, *args, **kwargs):
        try:
            self.fa._stopped = True
        except:
            pass
        return b"testsend"

    def sendall(self, *args, **kwargs):
        return True


class SolSSHMock():
    def close(self):
        return True


class SSHClientMock():
    def __init__(self, *args, **kwargs):
        pass

    def set_missing_host_key_policy(self, *args, **kwargs):
        return True

    def connect(self, *args, **kwargs):
        return True

    def invoke_shell(self, *args, **kwargs):
        return SerialMock()


class SolDriverMock(SolDriver):
    def __init__(self, cfg_opts, log):
        self._addressed = None
        super(SolDriverMock, self).__init__(cfg_opts, log)


class TestSolDriver(object):

    @staticmethod
    def _test_run():
        sd_obj = SolDriverSub(cnf_normal, log)
        sd_obj.run()

    @staticmethod
    def _test_write():
        sd_obj = SolDriverSub(cnf_normal, log)
        sd_obj._closed = ""
        sd_obj.write("abc")
        sd_obj._closed = "ok"
        try:
            sd_obj.write("abc")
        except:
            pass

    @staticmethod
    def test_init():
        from src.dtaf_core.drivers.internal.sol_driver import paramiko
        paramiko.SSHClient = SSHClientMock
        try:
            sd_obj = SolDriverMock(cnf_normal, log)
        except:
            pass
