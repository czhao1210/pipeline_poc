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
Serial Transport Layer in SUT
"""
import binascii
from datetime import datetime

from serial import SerialException, SerialTimeoutException

from sutagent.lib.configuration import configuration
from sutagent.lib.private.log_logger import sparklogger
from sutagent.lib.private.shared_data import SerialOutputCapture

if not configuration.is_cluster_mode():
    import sutagent.lib as g_main_serial_service

    try:
        import sutagent as sutagent_serial_port
    except ImportError:
        pass


def length_char(string, length):
    new_len_str = string
    for c in range(length - len(string)):
        new_len_str = '0' + new_len_str
    return new_len_str


def calculate_timeout(start_time, timeout_sec):
    if timeout_sec > 0:
        return (datetime.now() - start_time).seconds <= timeout_sec
    else:
        return True


class TransportTimeout(Exception):
    pass


class TransportError(Exception):
    pass


class FrameError(Exception):
    pass


transportSendFrameTimeout = TransportTimeout('send frame data timeout')
transportRecvFrameTimeout = TransportTimeout('receive frame data timeout')

SERIAL_DATA = ''


def receive_frame(timeout):
    """
    receive a frame with in specified time. if couldn't receive it with in that time raise TransportTimeout

    :param timeout: seconds. if timeout <= 0, there is no timeout, already receive frame
    :return: frame data

    :exception: TransportTimeout
    :dependence serial_port.read

    :black box equivalent class: timeout < 0, timeout = 0, timeout > 0

    """
    # if timeout <= 0:
    #     raise ValueError('error input timeout, it should bigger than 0')

    sparklogger.debug('receive frame --> start')
    start_time = datetime.now()

    global SERIAL_DATA
    try:
        serial_port = g_main_serial_service.g_sutagent_serial_service
    except BaseException:
        serial_port = sutagent_serial_port.sutagent_serial_port
    frame_buffer = ''
    frame_phase = 0  # 0: haven't got header
    frame_data_length = 0
    if not serial_port:
        raise SerialException('Open port fail !')
    while calculate_timeout(start_time, timeout):
        buf = serial_port.read()
        if buf:
            sparklogger.info('buffer  data is {}'.format(buf))
        if not isinstance(SERIAL_DATA, bytes):
            SERIAL_DATA = SERIAL_DATA.encode('utf-8')
        if not isinstance(buf, bytes):
            buf = buf.encode('utf-8')
        SERIAL_DATA = SERIAL_DATA + buf
        if not SERIAL_DATA:
            continue
        ret = SerialOutputCapture.get_instance().return_on_detection()
        if ret:
            raise Exception('serial data is in error {0}'.format(ret))
        if frame_phase == 0:
            for i in range(len(SERIAL_DATA)):
                header = SERIAL_DATA[i:i + 2]

                if header == Frame.HEADER_FLAG:
                    frame_buffer = header
                    SERIAL_DATA = SERIAL_DATA[i + 2:]
                    frame_phase = 1
                    break
        if frame_phase == 0:
            SERIAL_DATA = SERIAL_DATA[-1:]
            continue
        if frame_phase == 1:
            frame_type = SERIAL_DATA[0:1]
            # no more data, parse next coming data from serial port
            flag = ''
            if isinstance(frame_type, bytes):
                flag = b''
            if frame_type == flag:
                continue
            # check frame type if correct
            elif frame_type in [Frame.TYPE_TXTS,
                                Frame.TYPE_TXTE,
                                Frame.TYPE_TXTO,
                                Frame.TYPE_TXTD,
                                Frame.TYPE_ACK]:
                frame_buffer += frame_type
                SERIAL_DATA = SERIAL_DATA[1:]
                frame_phase = 2
            # if incorrect frame type, discard header, and reset temporary env
            else:
                frame_buffer = ''
                frame_phase = 0
                frame_data_length = 0
                continue
        if frame_phase == 2:
            data_length = SERIAL_DATA[0:3]
            if len(data_length) == 3:
                try:
                    length = int(data_length)
                # if has illegal char(not integer), discard header, and reset temporary env
                except ValueError:
                    SERIAL_DATA = frame_buffer[2:] + SERIAL_DATA
                    frame_buffer = ''
                    frame_phase = 0
                    frame_data_length = 0
                    continue
                # if has illegal char(bigger than max length), discard header, and reset temporary env
                if length > Frame.MAX_DATA_LEN:
                    SERIAL_DATA = frame_buffer[2:] + SERIAL_DATA
                    frame_buffer = ''
                    frame_phase = 0
                    frame_data_length = 0
                    continue
                else:
                    frame_buffer += data_length
                    frame_data_length = length
                    SERIAL_DATA = SERIAL_DATA[3:]
                    frame_phase = 3
            # not enough length data, parse next coming data from serial port
            else:
                continue
        if frame_phase == 3:
            sparklogger.debug('frame_phase 333 show data {},{},{}'.format(frame_buffer, SERIAL_DATA, frame_data_length))
            if len(frame_buffer) + len(SERIAL_DATA) < frame_data_length + 14:
                frame_buffer += SERIAL_DATA
                SERIAL_DATA = ''
            else:
                need_len = frame_data_length + 14 - len(frame_buffer)

                frame_buffer += SERIAL_DATA[0:need_len]
                SERIAL_DATA = SERIAL_DATA[need_len:]
                frame_phase = 4
        if frame_phase == 4:
            rec_crc = frame_buffer[-8:]
            body = frame_buffer[2:-8]
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            body_crc = length_char(hex(binascii.crc32(body) & 0xFFFFFFFF).rstrip('L').lstrip('0x'), 8)
            # crc wrong, discard header , and reset temporary env
            if not isinstance(body_crc, bytes):
                body_crc = body_crc.encode('utf-8')
            if not body_crc == rec_crc:
                frame_phase = 0
                frame_data_length = 0
                SERIAL_DATA = frame_buffer[2:] + SERIAL_DATA
                frame_buffer = ''
            # got a correct frame, break while and return frame
            else:
                break
    else:
        if not isinstance(SERIAL_DATA, bytes):
            SERIAL_DATA = SERIAL_DATA.encode('utf-8')
        if not isinstance(frame_buffer, bytes):
            frame_buffer = frame_buffer.encode('utf-8')

        SERIAL_DATA = frame_buffer + SERIAL_DATA
        raise TransportTimeout("No correct frame data received with in %s seconds" % timeout)
    serial_port.write_log(False, False, frame_buffer)
    sparklogger.debug('receive frame --> end , frame: {}'.format(frame_buffer))
    return frame_buffer


def send_frame(frame_data):
    '''
    send a frame

    :param frame_data: frame data which is matched frame structure
    :return:

    :dependence serial_port.write
    :black box equivalent class: frame_data=None, len(frame_data) < 10
                                 len(frame_data) = 10
                                 10 < len(frame_data) < 16
                                 16 <= len(frame_data) < 32
                                 serial_port.write = SerialTimeoutException
                                 serial_port.write = SerialException

    '''
    sparklogger.debug('send frame --> start {}'.format(frame_data))
    global serial_port
    try:
        serial_port = g_main_serial_service.g_sutagent_serial_service
    except BaseException:
        serial_port = sutagent_serial_port.sutagent_serial_port
    count, rem = divmod(len(frame_data), 16)
    if rem > 0:
        count = count + 1

    serial_port.write_log(True, False, frame_data)
    for i in range(count):
        try:
            serial_port.write(frame_data[i * 16: (i + 1) * 16])
        except SerialTimeoutException as ex:
            raise transportSendFrameTimeout
        except SerialException as ex:
            raise TransportError('{}'.format(ex))
    sparklogger.debug('send frame --> end')


class Frame(object):
    HEADER_FLAG = (chr(0x7E) + chr(0x24)).encode('utf-8')
    # __ITEM_TAIL = chr(0x7F)
    # __ESCAPE_CHAR = chr(0x7D)

    TYPE_TXTO = '1'.encode('utf-8')  # odd content frame
    TYPE_TXTE = '2'.encode('utf-8')  # even content frame
    TYPE_TXTD = '3'.encode('utf-8')  # the latest content frame
    TYPE_TXTS = '4'.encode('utf-8')  # the start content frame
    TYPE_ACK = '5'.encode('utf-8')  # acknowledge frame

    MAX_DATA_LEN = 127
    CRC_LEN = 8

    def __init__(self, frame_type, raw_data=''):
        self.__frame_type = frame_type
        self.__raw_data = raw_data
        self.__frame_data = ''
        if not isinstance(self.__frame_type, bytes):
            self.__frame_type = self.__frame_type.encode('utf-8')
        if self.__frame_type not in [self.TYPE_TXTD, self.TYPE_TXTE,
                                     self.TYPE_TXTO, self.TYPE_ACK,
                                     self.TYPE_TXTS]:
            raise ValueError('nonsupport frame type')

    @classmethod
    def parse(cls, frame_data):
        '''
        parse received frame data to generate a frame object.

        :param frame_data: frame data you want to parse
        :return: Frame object

        :exception: FrameError
        :dependence serial_port.write
        :black box equivalent class: frame_data=None, frame_data = ''
                    after parse, check frame object's frame type and frame data is correct
                                 frame_data = '~$11271234567890qazxswedcvrfvcdewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf1234567890qazxswedcvrfvcewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf[\iuyre36976e342'
                                 frame_data = '~$21271234567890qazxswedcvrfvcdewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf1234567890qazxswedcvrfvcewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf[\iuyre36976e342'
                                 frame_data = '~$31271234567890qazxswedcvrfvcdewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf1234567890qazxswedcvrfvcewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf[\iuyre36976e342'
                                 frame_data = '~$4271234567890qazxswedcvrfvcdewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf1234567890qazxswedcvrfvcewsxz#$%^&*()_+sl;'l,kmjn.lk[]iuytf[\iuyre36976e342'
                                 frame_data = '~$10271234567890qazxsdc*()_+sl;'lc7d81b04'
                                 frame_data = '~$20271234567890qazxsdc*()_+sl;'lc7d81b04'
                                 frame_data = '~$30271234567890qazxsdc*()_+sl;'lc7d81b04'
                                 frame_data = '~$40271234567890qazxsdc*()_+sl;'lc7d81b04'
                                 frame_data = '~$50011ec20da52'
                                 frame_data = '~$5001275298be8'
                                 frame_data = '~$50013022ebb7e'
                                 frame_data = '~$500149c4a2edd'
        '''
        # remove head and tail
        sparklogger.debug('parse frame --> start')
        if isinstance(frame_data, bytes):
            frame_data = frame_data.decode('utf-8')
        data = frame_data[2:]
        # parse frame type
        frame_type = data[0]
        len_3char = data[1:4]
        data_length = int(len_3char)

        raw_data = data[4:4 + data_length]
        sparklogger.debug('parse frame --> end, frame_type:{}, raw_data:{}'.format(frame_type, raw_data))
        return Frame(frame_type, raw_data)

    def get_frame_data(self):
        '''
        according frame raw data to generate frame data.

        :param:
        :return: frame data

        :exception:
        :dependence: length_char, uchar_checksum_to_4hex_chars, escape

        :black box equivalent class: raw_data > MAX_DATA_LEN,
                                     raw_data <= MAX_DATA_LEN,
        '''
        sparklogger.debug('create frame data --> start')
        if self.__frame_data:
            return self.__frame_data

        raw_len = len(self.__raw_data)
        if raw_len > self.MAX_DATA_LEN:
            raise ValueError('raw data length is bigger than {0}, should less equal than {1}'.format(raw_len,
                                                                                                     self.MAX_DATA_LEN))

        len_3char = length_char(str(len(self.__raw_data)), 3)
        if not isinstance(len_3char, bytes):
            len_3char = len_3char.encode('utf-8')
        if not isinstance(self.__raw_data, bytes):
            self.__raw_data = self.__raw_data.encode('utf-8')
        frame_data = self.type + len_3char + self.__raw_data
        crc = length_char(hex(binascii.crc32(frame_data) & 0xFFFFFFFF).rstrip('L').lstrip('0x'), 8)

        # checksum_str = uchar_checksum_to_4hex_chars(len_3char + self.__raw_data)

        # data = self.escape(self.__raw_data + checksum_str)
        if not isinstance(crc, bytes):
            crc = crc.encode('utf-8')
        frame_data = self.HEADER_FLAG + frame_data + crc

        self.__frame_data = frame_data
        sparklogger.debug('create frame data --> end, frame data {}'.format(frame_data))
        return frame_data

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def type(self):
        return self.__frame_type

        # @classmethod
        # def escape(cls, data):
        #     '''
        #     scan the data, if find tail, header or escape characters in it, need escape them.
        #     :param data:
        #     :return:
        #
        #     :dependence:
        #
        #     :black box equivalent class: data contains tail characters,
        #                                  data contains header characters,
        #                                  data contains escape characters,
        #                                  data doesn't contains escape, tail, header characters
        #     '''
        #     new_data = ''
        #     for c in data:
        #         if c == cls.__ITEM_TAIL \
        #             or c == cls.__ITEM_HEADER \
        #                 or c == cls.__ESCAPE_CHAR:
        #             new_data += cls.__ESCAPE_CHAR + chr(0x20 ^ ord(c))
        #         else:
        #             new_data += c
        #     return new_data

        # @classmethod
        # def anti_escape(cls, data):
        #     '''
        #     scan the data, if find escape characters in it, need anti-escape the character behind it.
        #     :param data: data need anti-escape
        #     :return:
        #
        #     :dependence:
        #
        #     :black box equivalent class: data contains tail characters,
        #                                  data contains header characters,
        #                                  data contains escape characters,
        #                                  data doesn't contains escape, tail, header characters
        #     '''
        #     new_data = ''
        #     need_anti = False
        #     for c in data:
        #         if need_anti:
        #             new_data += chr(0x20 ^ ord(c))
        #             need_anti = False
        #             continue
        #         else:
        #             if c == cls.__ESCAPE_CHAR:
        #                 need_anti = True
        #                 continue
        #             else:
        #                 new_data += c
        #     return new_data


class Message(object):
    @classmethod
    def receive(cls, timeout):
        '''
        receive a message from sender, sender will send the message by one frame by one frame. this function need
        combine all frames together according the frame order, if all frames are received transfer them to message
        and return it.

        while received a frame, need parse it and check if the frame correct according to checksum, if it is correct
        acknowledge sender to send next frame. else sender will send this frame a again, this function need receive
        it again, till timeout.

        :param timeout: receive timeout. if timeout <= 0, there is no timeout, already receive message
        :return: message data which contains one message's all frame data

        :exception
        :dependence: Frame.parse, receive_frame, send_frame

        :black box equivalent class: timeout > 0, timeout <= 0,
                                   1.
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTE frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTO frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data
                                     Frame.parse = Frame
                                     send_frame
                                     return message
                                   2.
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTE frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data
                                     Frame.parse = Frame,
                                     send_frame
                                     return message
                                   3.
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     return message
                                   4.
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTE frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTO frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TransportTimeout
                                   5.
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TransportTimeout
                                   6.
                                     receive_frame = TXTO frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     return message
                                   7.
                                     receive_frame = TXTO frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTE frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TransportTimeout
                                   8.
                                     receive_frame = TXTE frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTO frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTS frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     receive_frame = TXTD frame data,
                                     Frame.parse = Frame,
                                     send_frame
                                     return message
        '''
        # if timeout <= 0:
        #     raise ValueError('error input timeout, it should bigger than 0')
        sparklogger.debug('receive message --> start')
        global SERIAL_DATA
        serial_data = ''

        start_time = datetime.now()
        pre_transporting_type = -1
        message = ''
        while calculate_timeout(start_time, timeout):
            remainder_time = timeout - (datetime.now() - start_time).seconds
            frame_data = receive_frame(remainder_time)
            frame_data = frame_data.decode("utf-8")
            try:
                txt_frame = Frame.parse(frame_data)
                # if got a start frame, reset message
                if txt_frame.type == Frame.TYPE_TXTS:
                    # sparklogger.warning('waste frame, discard it:{}'.format(txt_frame.get_frame_data()))
                    # create ACK frame to acknowledge sender
                    message = txt_frame.raw_data
                    pre_transporting_type = txt_frame.type
                    ack_frame = Frame(Frame.TYPE_ACK, txt_frame.type)
                    send_frame(ack_frame.get_frame_data())
                # if already got start frame, save coming frame data
                elif not message == '' and not txt_frame.type == pre_transporting_type:
                    message += txt_frame.raw_data

                    # create ACK frame to acknowledge sender
                    ack_frame = Frame(Frame.TYPE_ACK, txt_frame.type)
                    send_frame(ack_frame.get_frame_data())

                    pre_transporting_type = txt_frame.type
                    # if it is the last frame, break receive and return message
                    if txt_frame.type == Frame.TYPE_TXTD:
                        break
                # if duplicated frame or , discard
                elif not message == '':
                    # create ACK frame to acknowledge sender
                    ack_frame = Frame(Frame.TYPE_ACK, txt_frame.type)
                    send_frame(ack_frame.get_frame_data())
                    # if same, discard it, continue receiving new frame
            except FrameError as ex:
                print(ex)
        else:
            raise TransportTimeout("couldn't complete message receive with in specified time %s" % timeout)
        sparklogger.debug('receive message --> end, message: {}'.format(message))
        return message

    @classmethod
    def send(cls, message):
        '''
        send a message to receiver, during sending split the message to frame, then send them one by one.

        :param message: message data
        :return:
        :exception: TransportError

        :dependence: send_frame, receive_frame, Frame.parse
        :black box equivalent class: message = '', message = None
                                     len(message) > 127, len(message) = 127, len(message) < 127
                                   1.
                                     send_frame(start frame)
                                     receive_frame = TransportTimeout
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     send_frame(end frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     successfully send
                                   2.
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     send_frame(end frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     successfully send
                                   3.
                                     send_frame(start frame)
                                     receive_frame = TransportTimeout
                                     send_frame(start frame)
                                     receive_frame = TransportTimeout
                                     send_frame(start frame)
                                     receive_frame = TransportTimeout
                                     raise TransportError
                                   4.
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = Frame
                                     send_frame(odd frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     send_frame(end frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     successfully send
                                   5.
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = Frame
                                     send_frame(odd frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     send_frame(even frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     send_frame(end frame)
                                     receive_frame = frame data
                                     Frame.parse = ACK Frame
                                     successfully send
                                   6.
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = Frame
                                     send_frame(odd frame)
                                     receive_frame = TransportTimeout
                                     send_frame(odd frame)
                                     receive_frame = TransportTimeout
                                     send_frame(odd frame)
                                     receive_frame = TransportTimeout
                                     raise TransportError
                                   7.
                                     send_frame(start frame)
                                     receive_frame = frame data
                                     Frame.parse = Frame
                                     send_frame(odd frame)
                                     receive_frame = ACK frame
                                     send_frame(even frame)
                                     receive_frame = TransportTimeout
                                     send_frame(even frame)
                                     receive_frame = TransportTimeout
                                     send_frame(even frame)
                                     receive_frame = TransportTimeout
                                     raise TransportError
        '''
        sparklogger.debug('send message --> start')

        global SERIAL_DATA
        SERIAL_DATA = ''

        x, y = divmod(len(message), Frame.MAX_DATA_LEN)
        if y > 0:
            x += 1

        retry = 5
        try:
            ack_wait_time = int(configuration.get_value('Serial Output', 'wait_ACK_timeout'))
        except BaseException:
            ack_wait_time = 3

        if x == 1:
            x += 1

        for i in range(x):
            if i == 0:
                pre_transporting_type = Frame.TYPE_TXTS
            elif i == x - 1:
                pre_transporting_type = Frame.TYPE_TXTD
            else:
                start, data_type = divmod((i + 1), 2)
                if data_type == 1:
                    pre_transporting_type = Frame.TYPE_TXTO
                else:
                    pre_transporting_type = Frame.TYPE_TXTE

            raw_data = message[i * Frame.MAX_DATA_LEN: (i + 1) * Frame.MAX_DATA_LEN]
            txt_frame = Frame(pre_transporting_type, raw_data)

            success = False
            for j in range(retry):
                send_frame(txt_frame.get_frame_data())
                try:
                    while True:
                        ack_frame_data = receive_frame(ack_wait_time)
                        sparklogger.info('check data ack_frame_data {}'.format(ack_frame_data))
                        ack_frame = Frame.parse(ack_frame_data)
                        if not ack_frame.type == ack_frame.TYPE_ACK:
                            sparklogger.warning("Non-ACK frame received after sent a text frame:{}"
                                                .format(ack_frame.get_frame_data()))
                            sparklogger.warning('continue to receive ACK')
                        else:
                            frame_type = txt_frame.type
                            if not isinstance(frame_type, str):
                                frame_type = frame_type.decode('utf-8')
                            if ack_frame.raw_data == frame_type:
                                success = True
                                break
                    if success:
                        break
                except TransportTimeout as ex:
                    # the sent frame doesn't be received by receiver. and there is no ACK frame send back.
                    # retry
                    sparklogger.error(ex)

            # not received right ACK
            if not success:
                raise TransportError('retry send frame 3 times, but no acknowledge received')
        sparklogger.debug('send message --> end')
