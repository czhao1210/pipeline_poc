#! /usr/bin/python2
"""
TCF Driver to run DTAF test cases in-band on SUTs.
"""
import os
import re
import subprocess

import tcfl
import tcfl.pos


@tcfl.tc.interconnect('ipv4_addr')
@tcfl.tc.target('pos_capable')
class dtaf_local_driver(tcfl.pos.tc_pos0_base):
    """
    Driver to run DTAF testcases on a Linux cluster of SUTs in-band.
    """

    # Use Clear Linux as the default execution OS.
    image_requested = os.environ.get("IMAGE", "clear")

    # Execute DTAF test cases out of the /opt directory
    dtaf_deploy_dest = "/opt"

    # DTAF_CONTENT test case regex
    dtaf_python_file_regex = re.compile("^.*\/dtaf_content.*\.py$")

    def __init__(self, name, tc_file_path, origin):
        super(dtaf_local_driver, self).__init__(name, tc_file_path, origin)

        # DTAF consists of two git repositories, dtaf_core and dtaf_content.
        # We need both of them to successfully run a test case.
        # DTAF_CORE path comes from the DTAF_CORE_PATH environment variable
        self.dtaf_core_path = os.environ.get('DTAF_CORE_PATH', None)
        if self.dtaf_core_path is None:
            raise tcfl.tc.blocked_e("DTAF_CORE_PATH environment variable must point to the DTAF_CORE directory!")

        # Extract DTAF_CONTENT path from git.
        self.dtaf_content_path = subprocess.check_output([
            'git', 'rev-parse', '--flags', '--show-toplevel', tc_file_path,
            ],
            stderr=subprocess.STDOUT,
            # CDing into the toplevel dir makes it work if we are
            # calling from inside the git tree or from outside
            cwd=os.path.dirname(tc_file_path)
            ).strip()

    @tcfl.tc.serially()
    def deploy_00(self, target):
        target.deploy_path_src = [self.dtaf_core_path, self.dtaf_content_path]
        target.deploy_path_dest = self.dtaf_deploy_dest
        self.deploy_image_args = dict(extra_deploy_fns=[tcfl.pos.deploy_path])

    def eval_0(self, ic, target):
        # Wait for the system to come up and connect to the network.
        tcfl.tl.linux_wait_online(ic, target)

        # Configure SSH since it is more reliable than serial.
        tcfl.tl.linux_ssh_root_nopwd(target)
        target.shell.run("systemctl restart sshd")

        # Wait for the SSH daemon to restart.
        target.shell.run(
            "while ! exec 3<>/dev/tcp/localhost/22; do"
            " sleep 1s; done", timeout=15)

        # Setup tcp tunnel and start SSH so we can copy around
        target.tunnel.ip_addr = target.addr_get(ic, "ipv4")

        # If we have a preferred console, switch to it (for DTAF, usually SSH)
        target.console.select_preferred(user='root')

        # Switch to simplified prompt to avoid false positives with ANSI sequences involved.
        # TODO: Determine why this is needed and if it can be avoided
        target.shell.shell_prompt_regex = re.compile("LTP-PROMPT% ")
        target.shell.run(
            "export PS1='LTP-PROMPT% '  # a simple prompt is "
            "harder to confuse with general output")

        # Configure proxy on the system
        tcfl.tl.sh_export_proxy(ic, target)

        # Install Python dependencies from DTAF
        target.shell.run("pip install --user -r /opt/dtaf_core/requirements_python3.txt")
        target.shell.run("pip install --user -r /opt/dtaf_content/requirements_python3.txt")
        target.shell.run("export PYTHONPATH=/opt")

        # Install Linux dependencies from DTAF
        target.shell.run("cp /opt/dtaf_core/collateral/volatility /usr/bin")
        target.shell.run("chmod +x /usr/bin/volatility")

    def eval_1(self, target):
        target.shell.run("cd /opt")
        config_file_path = "/opt/dtaf_core/configuration/configuration_sample_local.xml"
        pycmd = "python {} --cfg_file {} --console_debug || echo F''AIL_DTAF".format(self.kws['thisfile'], config_file_path)
        test_output = target.shell.run(pycmd , output=True, trim=True)

        if "<Test Result: Test Passed>" in test_output:
            # DTAF marker for passing test found
            return
        elif "FAIL_DTAF" in test_output:
            # DTAF test case returned with a non-zero exit code
            raise tcfl.tc.failed_e("Test case {} failed!".format(self.name), {"test_log": test_output})
        else:
            # Unknown condition
            raise tcfl.tc.error_e("Unknown error in test case {}!".format(self.name), {"test_log": test_output})

    @classmethod
    def is_testcase(cls, path, from_path, tc_name, subcases_cmdline):
        if not cls.dtaf_python_file_regex.search(os.path.abspath(path)):
            # Not a DTAF test case
            return []  # TODO: Also filter Python files that don't run BaseTestCases
        else:
            # Is a DTAF test case
            return [cls(os.path.split(path)[1], path, from_path)]


tcfl.tc.tc_c.driver_add(dtaf_local_driver)
