import ctypes
import sys
import time
import os
port_pwr_delay_sec = 2

class BWUsbPdu:
    def __init__(self, ac_outlets):
        self.outlets = ac_outlets
        self.outlets = self.outlets.split(',')
        self.outlets = [int(i) for i in self.outlets]
        # self.usb = ctypes.cdll.LoadLibrary(".\\USBPower")
        self.usb = ctypes.cdll.LoadLibrary(dll_path)

    def outlets_power(self, value):
        for o in self.outlets:
            print("setting port " + str(o) + " to " + str(value))
            self.usb.SRMLineOpenByIndex(0, o, value)
            time.sleep(port_pwr_delay_sec)

    def off(self):
        self.outlets_power(0)

    def on(self):
        self.outlets_power(1)

    def get_desc(self):
        return self.usb.GetUSBPowerList()

    # this is for future use if API is fixed(urrently returns 0xff)
    def get_outlet_status(self):
        pwr_status = self.usb.SRMOpenStatusByIndex()
        print(pwr_status)
        print("outlets=" + str(self.outlets))
        bitmask = 1 << (self.outlets[0] - 1) # outlets 1 to 5
        print("bitmask="+ str(bitmask))
        outlet_status = pwr_status & bitmask
        print(str(outlet_status))
        if outlet_status == 0:
            return False
        else:
            return True


if __name__ == '__main__':

    if sys.argv.__len__() < 4:
        print("\nUsage:")
        print("python usb_pdu.py <USBPower.dll path> <outlets> <command>")
        print("\nExample:")
        print("python ./USBPower.dll usb_pdu.py 1,2 ON\n")
        exit()
    dll_path = os.path.normpath(str(sys.argv[1]))
    ac_outlets = str(sys.argv[2])
    action = str(sys.argv[3])

    pdu = BWUsbPdu(ac_outlets)
    # print(pdu.get_desc())  # prints number of usb pdu devices

    if action == "ON":
        print(pdu.on())
    elif action == "OFF":
        print(pdu.off())
    elif action == "Cycle":
        pdu.off()
        time.sleep(45)
        pdu.on()
    elif action == "get_outlet_status":
        pdu.get_outlet_status()
    else:
        print("Command not received")
        print("Command must be OFF, ON, or Cycle")
