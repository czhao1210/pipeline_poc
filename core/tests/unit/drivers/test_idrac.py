from dtaf_core.drivers.internal.bmc.idrac import IdracBmc


class SessionMock:
    def __init__(self, post_status_code_value=None, post_content_value=None,
                 get_status_code_value=None, get_content_value=None, patch_status_code_value=None,
                 patch_content_value=None, *args, **kwargs):
        self.post_status_code_value = post_status_code_value
        self.post_content_value = post_content_value
        self.get_status_code_value = get_status_code_value
        self.get_content_value = get_content_value
        self.patch_status_code_value = patch_status_code_value
        self.patch_content_value = patch_content_value

    def post(self, *args, **kwargs):
        return PostMock(status_code_value=self.post_status_code_value, content_value=self.post_content_value)

    def get(self, *args, **kwargs):
        return GetMock(status_code_value=self.get_status_code_value, content_value=self.get_content_value)

    def patch(self, *args, **kwargs):
        return PatchMock(status_code_value=self.patch_status_code_value, content_value=self.patch_content_value)


class PostMock:

    def __init__(self, status_code_value=None, content_value=None, *args, **kwargs):
        self.status_code = status_code_value
        self.content = content_value


class PatchMock:

    def __init__(self, status_code_value=None, content_value=None, *args, **kwargs):
        self.status_code = status_code_value
        self.content = content_value

    def json(self):
        return {}


class GetMock:

    def __init__(self, status_code_value=None, content_value=None, *args, **kwargs):
        self.status_code = status_code_value
        self.content = content_value

    def json(self):
        return {"BiosVersion": "x.x.x", "Version": "x.x.x",
                "Boot": {"BootOrder": ['x1', 'x2']},
                "Attributes": {"Info.1.CPLDVersion": "x.x.x", "SysInfo.1.POSTCode": "x.x.x"},
                "FirmwareVersion": "xxx", "PowerState": "xxx"}


class TestIdrac:
    @staticmethod
    def test_dc_power_on():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.dc_power_on('xxx')
        assert ret == True

    @staticmethod
    def test_dc_power_off():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.dc_power_off('xxx')
        assert ret == True

    @staticmethod
    def test_dc_power_state():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.dc_power_state('xxx')
        assert ret == "xxx"

    @staticmethod
    def test_dc_power_reset():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.dc_power_reset('xxx')
        assert ret == True

    @staticmethod
    def test_clear_cmos():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.clear_cmos('xxx')
        assert ret == True

    @staticmethod
    def test_get_bmc_version():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.get_bmc_version('xxx')
        assert ret == 'xxx'

    @staticmethod
    def test_flash_bmc():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.flash_bmc(imageURI='x.x.x', username='xxx', password='xxx', transferprotocol='')
        assert ret == True

    @staticmethod
    def test_flash_bios():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.flash_bios(imageURI='x.x.x', username='xxx', password='xxx', transferprotocol='')
        assert ret == True

    @staticmethod
    def test_flash_cpld():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.flash_cpld(imageURI='x.x.x', username='xxx', password='xxx', transferprotocol='')
        assert ret == True

    @staticmethod
    def test_get_bios_version():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.get_bios_version('xxx')
        assert ret == 'x.x.x'

    @staticmethod
    def test_get_cpld_version():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.get_cpld_version('xxx', 'xxx')
        assert ret == 'x.x.x'

    @staticmethod
    def test_get_postcode():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.get_postcode('xxx', 'xxx')
        assert ret == 'x.x.x'

    @staticmethod
    def test_change_bootorder():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(patch_status_code_value=200)
        ret = obj.change_bootorder(bootorder=['select1', 'select2'], FunctionEnabled=True,
                                   TimeoutAction=None, computersystemid='xxx')
        assert ret == True

    @staticmethod
    def test_get_bootorder():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(get_status_code_value=200)
        ret = obj.get_bootorder('xxx')
        assert ret == ['x1', 'x2']

    @staticmethod
    def test_insert_virtual_media():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.insert_virtual_media(image='xxx', username="", password="", transfermethod="",
                                       transferprotocoltype="", inserted=None, writeprotected=None, managerid='xxx',
                                       virtualmediaid='xxx')
        assert ret == True

    @staticmethod
    def test_eject_virtual_media():
        obj = IdracBmc(ip='xxx.xxx.xxx.xxx', username='xxx', password='xxx')
        obj.session = SessionMock(post_status_code_value=200)
        ret = obj.eject_virtual_media(managerid='xxx', virtualmediaid='xxx')
        assert ret == True
