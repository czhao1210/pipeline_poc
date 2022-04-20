import mock

from dtaf_core.drivers.internal.wrapper.usb_pdu import BWUsbPdu


class TestSuites:
    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.wrapper.usb_pdu.ctypes')
    def test_init(mock_ctypes):
        BWUsbPdu.__init__ = object.__init__
        obj = BWUsbPdu()
        obj.outlets = [1, 2, 3]
        obj.usb = mock.Mock()
        obj.usb.SRMOpenStatusByIndex.return_value = 1
        obj.outlets_power(1)
        obj.off()
        obj.on()
        obj.get_desc()
        obj.get_outlet_status()

