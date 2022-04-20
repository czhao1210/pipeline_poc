import six
import paramiko

import tcfl

from dtaf_core.lib.os_lib import LinuxDistributions, os_rel_map


class ProvisionBase(object):
    """
    Base class for running the provisioning steps needed to enable DTAF execution with TCF.
    """

    # Common RSA key to enable repeatable login with TCF+DTAF-provisioned systems.
    # Do not use this key for anything other than enabling temporary login with TCF as Git is not secure storage for
    # RSA private keys. Anyone with access to this repo can use this key, so it is not proof of identity.
    dtaf_pk_str = """\
        -----BEGIN RSA PRIVATE KEY-----
        MIIEowIBAAKCAQEAuMOzv4lsH7igz9/r7jtZ1sGzoCfjLwcdhWaCtmdDdodOBGYz
        bYnBB6p/UP+6DAnlV7Ah08TBk0WqXzBP+co00CLQTkanyUj3EAcfptN/5SGiH04P
        0Fl/esxZN/9LDILAUq8Kcoi/XbGQ7zibUsGt/8MENSl3F0tUNAsk/p9ommO4F9Of
        C2osdu9uv32oUTnPS4/EXXQZ1T+XtU+cElZ8tTOIjHZL6y0qGVc/q9lJ5KG6db8N
        KLUJXsUURqGXFYtVLk7IZHxxES7nSkJg5uueqTk8caYz/1juzNhJBJWi7sJsC1j/
        HpEDZpCoPXrz4qmHnE+prqaSgva4QPlFysXHXQIDAQABAoIBAFawU7zRYG69tI3z
        9QFwzWUKuxmwvVIKV5qIj1m/t5J8R2me/hAt6uiK4XOCmKsfVYC//g8bKOvNavOA
        enWrnv3s56liU0UIvArEHOCsKTy7fBKOELNj2oEmMdIpMPAsxMnGoPM+H/N45ZSo
        DZBVmSsAOBAtZVgDmv1UIUZqSqzswpJXxMU2w/lererr1rTzlf08qMTReI+xaHcs
        pJSAGiflP8djCFcSHUXGJbO40MHeLopR0UhEwXZb2kYie6WmT541c9HTdUTh5mm3
        SZEQLHdFIc3IwKxBHhcyNuu87XqrRRxPv2MqVmJTRH9wtTy9r1iiBvk7L5dzXXBn
        2qsHl+0CgYEA24RMq1z5//qW+I9Gez49CvbYdE00xMeiu6PRZ1ShkGxi9F2CeVgD
        Ts/Rjys4/2a+iE56sKm7tMaBGwbS3hXLbYtPM41tfqsLDoRpjSiSM+9OTI+2V70e
        5ekCe9kjeLO/1NzxPrd+tWQnIbTpU2zagS00Yl1DaMJCHpbSZ8wtAMcCgYEA13jO
        0QGFnl5m1l4XRqS47FHUflUdHIN1x07eE238EShxI2jZbt49JNO4up511/5/+lOw
        VFHVOaCr79dw/wxnmkWnDnCLZTASr31xXTX67TuQutu61we98vEA5sVcObxj2+DU
        Zsm2yVqoJJQQiwKRcN09u5B5+fNu1W1D45+eGrsCgYEAleTWMaGQeJHVqy6ykw9h
        wW3jSi86HDCx1206XVO16xeHzpNXt6I4yAUydI+wIP44lnz4XE/ag8uUdy8GqG27
        djbNQ0eMgBUtvKEALkqI4vvCvJbZjTnvslCUyJryFMaw9BpWhVvpItWbvvF47eWD
        oveKMKy8jfkwCxEz5XrPNBsCgYB9GAX6EYghiWzqx3V77eXuTROwxHlCNJAMRh1n
        6lKNI42LoTOayit1VfXJYnXIEFj8W9njGh9QdZdchxdy+yCq0AVMvMow1NgESi+m
        jdBAKnS8BxVSAYylnoWHdM02N8lBviWSB0m3XIqBsfRov/TwMYHFgvtNwaZ3AhiH
        7gM8QQKBgG2rSkXNhCeskdqpPRn9m4ismddf5ZIXd63XPSO7Ls+kxom/JpqVOBiD
        /QZhaaebkPVWe/UW1limwd/NkCh/3wK+6cysyfrfOfvhATEmYmSUjuHsiCV7W5pg
        xtdTQT/hOdDRk7euZ7xsaD8eT3cJx9pE7fynR460g0Blb0YmOvq5
        -----END RSA PRIVATE KEY-----"""
    dtaf_pk = paramiko.RSAKey.from_private_key(six.StringIO(dtaf_pk_str))

    @classmethod
    def _setup_ssh(cls, ic, target):
        """Enable SSH and key-based login on the target"""
        tcfl.tl.linux_ssh_root_nopwd(target)  # TCF default setup
        # Enable key-based authentication
        target.shell.run('''\
cat >> /etc/ssh/sshd_config
RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile  %h/.ssh/authorized_keys
\x04''')

        # Add dtaf key to the system
        public_ek = "{} {}".format(cls.dtaf_pk.get_name(), cls.dtaf_pk.get_base64())
        target.shell.run("""\
mkdir -p ~/.ssh
cat >> ~/.ssh/authorized_keys
{}
\x04""".format(public_ek))
        tcfl.tl.linux_sshd_restart(ic, target)  # restart ssh to apply changes
        target.console.select_preferred(user='root')  # switch to using ssh

    @classmethod
    def setup_target_attrs(cls, ic, target):
        """Get dynamic config file information from the SUT and populate it into the target structure"""
        os_info = tcfl.tl.linux_os_release_get(target)
        kernel_version = target.shell.run("uname -r", output=True)
        target.kws["dtaf"] = {}
        target.kws["dtaf"]["SutOsProvider"] = {
            "os_type": "Linux",  # TODO: Add Windows, ESXi, etc later
            "os_subtype": os_rel_map[os_info["ID"]],
            "os_version": os_info["VERSION_ID"],
            "os_kernel": kernel_version.split("\n")[1],
            "sut_private_key": cls.dtaf_pk,
            "user": "root",  # TODO: When non-Linux OSes are added, this will also need to change
            "sut_address": "{}:{}".format(target.ssh._ssh_host, target.ssh._ssh_port)
        }

    @classmethod
    def _pre_ssh_provisioning(cls, ic, target):
        # Wait for the system to come up and connect to the network.
        tcfl.tl.linux_wait_online(ic, target)

        # Configure proxy on the system
        tcfl.tl.sh_export_proxy(ic, target)

    @classmethod
    def _post_ssh_provisioning(cls, ic, target):
        pass

    @classmethod
    def setup_os(cls, ic, target):
        cls._pre_ssh_provisioning(ic, target)
        cls._setup_ssh(ic, target)
        cls._post_ssh_provisioning(ic, target)


class ClearProvision(ProvisionBase):
    @classmethod
    def _post_ssh_provisioning(cls, ic, target):
        super(ClearProvision, cls)._post_ssh_provisioning(ic, target)
        tcfl.tl.swupd_bundle_add(ic, target, "sysadmin-basic")  # Needed for screen


class UbuntuProvision(ProvisionBase):
    @classmethod
    def _pre_ssh_provisioning(cls, ic, target):
        super(UbuntuProvision, cls)._pre_ssh_provisioning(ic, target)
        target.shell.run("apt-get update && apt-get install -y openssh-server screen")


class TcfDeploy(object):
    # TCF base image types supported by DTAF
    IMAGE_BASE_NAMES = {
        LinuxDistributions.ClearLinux: "clear",
        LinuxDistributions.Ubuntu: "ubuntu"
    }

    # Map of image base names to the DTAF provisioning classes
    DEPLOY_CLS_MAP = {
        IMAGE_BASE_NAMES[LinuxDistributions.ClearLinux]: ClearProvision,
        IMAGE_BASE_NAMES[LinuxDistributions.Ubuntu]: UbuntuProvision
    }

    @classmethod
    def get_deploy_cls(cls, distribution):
        """
        Get a utility class that can provision the specified distribution using the TCF API.

        :param distribution: One of dtaf_core.lib.os_lib.LinuxDistributions
        :return: Subclass of tcf_deploy.ProvisionBase
        """
        return cls.DEPLOY_CLS_MAP[distribution]
