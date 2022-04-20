from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.pyte.screens import Screen, DebugScreen, \
    HistoryScreen, DiffScreen
from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.pyte.streams import Stream


class GernalPYTE(object):
    def __init__(self, width, height):
        self.__screen = Screen(width, height)
        self.__hs_screen = HistoryScreen(width, height, history=200000, ratio=0.5)
        self.__stream = Stream(self.__screen)
        self.__hs_stream = Stream(self.__hs_screen)

    def feed(self, data, history=None):
        """
        put data into pyte for parsing

        :param data: string received from serial port
        :return: None
        """
        # (str) => None
        try:
            if history:
                self.__hs_stream.feed(data)
            else:
                self.__stream.feed(data)
        except Exception as ex:
            print('feed ex from {0}'.format(ex))
            pass

    def get_text(self, colors, area):
        """
        get the text from the specified area

        :param colors: specify the color of text
        :param area: the area of text
        :return: str
        """
        # (tuple, tuple) => str
        text = []
        for r_idx, row in enumerate(self.__screen.buffer):
            if r_idx <= area[0] or r_idx > area[2]:
                continue

            bt = None
            bt_list = []
            for c_idx, single_char in enumerate(row):
                if c_idx <= area[1] or r_idx > area[3]:
                    continue

                if (single_char.bg, single_char.fg) in colors:
                    if bt:
                        if (single_char.bg, single_char.fg) == bt[1]:
                            bt[2] += single_char.data
                        else:
                            bt_list.append([r_idx] + bt)
                            bt = None
                    else:
                        bt = [c_idx, (single_char.bg, single_char.fg), single_char.data]
                else:
                    if bt:
                        bt_list.append([r_idx] + bt)
                        bt = None
            if bt:
                bt_list.append([r_idx] + bt)

            if bt_list:
                text.append(bt_list)

        return text

    def get_screen_display(self):
        # None => tuple
        """
        return the tuple of screen data
        :return: tuple
        """
        return self.__screen.display

    def get_cursor(self):
        # None => tuple
        """
        return the cursor data
        :return: tuple
        """
        return self.__screen.cursor

    def get_history(self):
        """
        return the tuple of screen data
        :return: tuple
        """
        return self.__hs_screen.display_history
