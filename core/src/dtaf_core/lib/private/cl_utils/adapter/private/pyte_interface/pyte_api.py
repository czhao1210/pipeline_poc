"""
API for pyte
"""
import re
import time

# from dtaf_core.lib.private.cl_utils.adapter.private.log import self._log
from dtaf_core.lib.private.cl_utils.adapter.data_types import BIOS_BOOT_MENU_TYPE, BIOS_SETUP_MENU_TYPE, \
    BIOS_UI_DIR_TYPE, \
    BIOS_UI_OPT_TYPE
from dtaf_core.lib.private.cl_utils.adapter.private.pyte_interface.pyte import DiffScreen, Stream

class PyteAPI(object):

    DEFAULT_DATA = DiffScreen(80, 24).default_char
    def __init__(self, width, height, bios_menu_type, resolution_config, logger):
        self.__logger = logger
        self.__color_list = None
        self.__split_line = None
        self.__highlight_list = None
        self.__popup_groups = None

        self.__border_group = None
        self.__bound = None
        self.__full_boot_bound = False
        self.__bound_color_list = None
        self.__full_popup = False
        self.__screen = DiffScreen(width, height)

        self.__stream = Stream(self.__screen)
        self.__bios_menu_type = bios_menu_type
        self.__config = None
        self.__resolution_config = resolution_config
        self.__init_data()
        self.set_resolution(width=width, height=height)

    def convert_buffer(self, buffer):

        ret = list()
        buffer_items = buffer.items()
        for line in buffer_items:
            tmp_list = list()
            dict_data = line[1]
            dict_key_len = len(dict_data.keys())
            for i in range(0, dict_key_len - 1):
                if i < dict_key_len:
                    tmp_list.append(dict_data[i])
                else:
                    tmp_list.append(PyteAPI.DEFAULT_DATA)
            ret.append(tmp_list)
        return ret


    def __init_data(self):
        self.__color_list = []
        self.__split_line = (-1, -1)
        self.__highlight_list = []
        self.__popup_groups = []

        self.__border_group = None
        self.__bound = (0xFFF, 0xFFF, -1, -1)
        self.__full_boot_bound = True
        self.__full_popup = False

    # def clear_normal_page_highlight(self):
    #     try:
    #         clr_str = "\33[{0};{1}H\33[47;37m{2}\33[0m"
    #         if self.__highlight_list:
    #             for ele in self.__highlight_list:
    #                 self.feed(clr_str.format(ele[0], ele[1], ele[4]))
    #     except Exception, ex:
    #         self._log.error("error in clear_normal_page_highlight {0}".format(ex))
    #         raise Exception(ex)

    def reset_screen(self):
        try:
            self.__init_data()
            self.__screen.reset()
        except Exception as ex:
            self.__logger.error("error in reset_screen {0}".format(ex))
            raise Exception(ex)

    def feed(self, data):
        '''
        feed data to pyte stream for show in screen
        :param data:
        :return:
        '''
        # print("__feed data={0}".format(str(data).replace("\33", "\\33")))
        try:
            self.__logger.debug(
                "FEED_DATA:[%05d][%s]" % (
                    len(data), str(data).replace("\33", "\\33")))
            self.__stream.feed(data)
        except Exception as ex:
            self.__logger.error("FEED_DATA error ex={0}".format(ex))
            raise Exception(ex)

    def set_resolution(self, width, height):
        '''
        API
        :param width:
        :param height:
        :return:
        '''
        self.__logger.debug("set_resolution width={0}, height={1}".format(width, height))
        try:
            self.__screen.resize(height, width)
            self.__screen.reset()

            if (width, height) == (80, 24):
                self.__logger.debug("Change Resolution to [(80*24)]")
                self.__config = self.__resolution_config['PYTE_RESOLUTION_CONFIG_8024']
            elif (width, height) == (100, 31):
                self.__logger.debug("Change Resolution to [(100*31)]")
                self.__config = self.__resolution_config['PYTE_RESOLUTION_CONFIG_10031']
            else:
                raise Exception("RESOLUTION ERROR")

        except Exception as ex:
            self.__logger.error("set_resolution: ex={0}".format(ex))
            raise Exception(ex)

    def get_resolution(self):
        """
        get the title of pyte.
        :return: (columns, lines)
        """
        self.__logger.debug("get_resolution")
        try:
            ret_data = (self.__screen.columns, self.__screen.lines)
            self.__logger.debug("return: {0}".format(ret_data))
            return ret_data
        except Exception as ex:
            self.__logger.error("get_resolution ex={0}".format(ex))
            raise Exception(ex)

    def parse_screen(self):
        '''

        :return: (True/False, {
                                "title": ,
                                "highlight": (hight ok , (name, value, type, (start_row, start_col, end_row)),
                                "bound":, (start_row, start_column, end_column, end_row)
                                "description":,
                                "popup", True/False
                                "items" (name, value, TYPE, start_row)
                               })
        '''
        ret_info = {
            "title": "",
            "highlight": (False, ("", "", "", (None, None, None))),
            "bound": (0xFFFF, 0xFFFF, 0, 0),
            "description": "",
            "popup": False,
            "items": [],
            "full_popup": False
        }
        try:
            # self.reset_screen()
            self.__logger.debug(self.__screen)
            self.__init_data()
            self.__create_color_list()
            for x in self.__color_list:
                self.__logger.debug("{0}".format(x))

            self.__create_border_by_colors()
            self.__logger.debug("BORDERS {0}".format(self.__border_group))

            self.__create_bound()
            self.__logger.debug("BOUND {0}".format(self.__bound))

            ret_info["bound"] = self.__get_bound()
            ret_info["highlight"] = self.__get_highlight()
            ret_info["popup"] = self.__is_popup()
            ret_info["description"] = self.__get_description()
            ret_info["title"] = self.__get_title()
            ret_info["items"] = self.__get_items()
            ret_info["full_popup"] = self.__full_popup

            for key, value in ret_info.items():
                self.__logger.debug("[%s]: [%s]" % (str(key), str(value)))

            return True, ret_info
        except Exception as ex:
            self.__logger.error("error in parse_screen {0}".format(ex))
            return False, ret_info

    def get_windows_bound(self):
        self.__create_color_list()
        bound = [0xFFFF, 0xFFFF, -1, -1]  # top, left, bottom, right
        for eles in self.__color_list:
            for ele in eles:
                if ele[2] not in ['black', 'default']:
                    bound[0] = min(bound[0], ele[0])
                    bound[1] = min(bound[1], ele[1])
                    bound[2] = max(bound[2], ele[0])
                    bound[3] = max(bound[3], ele[1] + len(ele[4]))
                else:
                    if ele[4].strip():
                        bound[0] = min(bound[0], ele[0])
                        bound[1] = min(bound[1], ele[1])
                        bound[2] = max(bound[2], ele[0])
                        bound[3] = max(bound[3], ele[1] + len(ele[4]))

        if 0xFFFF in bound or -1 in bound:
            return [0xFFFF, 0xFFFF, -1, -1]

        bound[2] += 1

        return bound

    def get_screen_info(self):
        bound = self.get_windows_bound()
        if 0xFFFF in bound or -1 in bound:
            return [], (0, 0)

        top, left, bottom, right = bound
        info = []
        for idx, data in enumerate(self.__screen.display):
            if idx < top:
                continue

            if idx > bottom:
                break

            tmp_str = data[left:right]
            if re.search('[ /]-{3}.*-{3}[ \\\\]', tmp_str):
                continue

            if re.search('[ \\\\]-{3}.*-{3}[/ ]', tmp_str):
                continue

            if tmp_str[0] == '|':
                tmp_str = tmp_str[1:]

            if tmp_str[-1] == '|':
                tmp_str = tmp_str[:-1]

            if tmp_str.strip():
                info.append(tmp_str.strip())

        return info, (right - left, bottom - top)

    def parse_popup(self):
        '''

        :return: (True/False, {
                                "title": ,
                                "highlight": (hight ok , (name, value, type, (start_row, start_col, end_row)),
                                "bound":, (start_row, start_column, end_column, end_row)
                                "description":,
                                "popup", True/False
                                "items" (name, value, TYPE, start_row)
                               })
        '''
        ret_info = {
            "title": "",
            "highlight": (False, ("", "", "", (None, None, None))),
            "bound": (0xFFFF, 0xFFFF, 0, 0),
            "items": [],
            "full": False
        }
        try:
            self.__init_data()
            self.__create_color_list()
            for x in self.__color_list:
                self.__logger.debug("{0}".format(x))

            popup_cfg = self.__config["bios_setup_menu"]["border"]["popup"]

            # TODO:
            popup_border = self.__get_border_by_colors(
                popup_cfg["position"], [popup_cfg["border_color"], popup_cfg["item_color"]])
            if not popup_border[0]:
                return False, ret_info

            popup_bound = self.__create_popup_bound(popup_border)
            self.__logger.debug("BOUND {0}".format(popup_bound))
            bound_color_list = self.__create_color_list_in_border(popup_bound)

            highlight_list = self.__get_highlight_list_in_bound(bound_color_list, popup_cfg)

            ret_info["bound"] = popup_bound
            ret_info["highlight"] = self.__get_popup_highlight(highlight_list, popup_cfg, popup_bound)
            ret_info["items"] = self.__get_popup_items(popup_bound)
            ret_info["full"] = self.__full_popup

            for key, value in ret_info.items():
                self.__logger.debug("[%s]: [%s]" % (str(key), str(value)))

            return True, ret_info
        except Exception as ex:
            self.__logger.error("error in parse_screen {0}".format(ex))
            return False, ret_info

    def __create_color_list_in_border(self, border):
        try:
            if not border:
                tmp_bound = (0, 0, self.__screen.lines - 1, self.__screen.columns - 1)
            else:
                tmp_bound = border

            color_list = []
            converted = self.convert_buffer(self.__screen.buffer)
            for row, row_data in enumerate(converted[tmp_bound[0]:tmp_bound[2] + 1]):
                color_list_item = []
                color = tuple()
                char_set = ""
                row_data = row_data[tmp_bound[1]:tmp_bound[3] + 1]
                for column, single_char in enumerate(row_data):
                    if not color:
                        color = (column, single_char.bg, single_char.fg)
                        char_set += single_char.data
                        continue
                    elif (color[1], color[2]) != (single_char.bg, single_char.fg):
                        color_list_item.append(
                            (row + tmp_bound[0], color[0] + tmp_bound[1], color[1], color[2], char_set))
                        color = (column, single_char.bg, single_char.fg)
                        char_set = single_char.data
                    else:
                        char_set += single_char.data

                if color:
                    color_list_item.append((row + tmp_bound[0], color[0] + tmp_bound[1], color[1], color[2], char_set))

                color_list.append(color_list_item)

            return color_list
        except Exception as ex:
            self.__logger.debug("error in __create_color_list {0}".format(ex))
            raise Exception(ex)

    def __create_color_list(self, is_in_bound=False):
        '''

        :return [
            row[(row_index, start_column_index, bg, fg, char),],]:
        '''
        try:
            if not is_in_bound:
                tmp_bound = (0, 0, self.__screen.lines - 1, self.__screen.columns - 1)
            else:
                tmp_bound = self.__bound
            self.__logger.debug("cur bound {0}".format(tmp_bound))

            color_list = []
            redraw_wait = 1.5
            time.sleep(int(redraw_wait))
            converted = self.convert_buffer(self.__screen.buffer)
            for row, row_data in enumerate(converted[tmp_bound[0]:tmp_bound[2] + 1]):
                color_list_item = []
                color = tuple()
                char_set = ""
                row_data = row_data[tmp_bound[1]:tmp_bound[3] + 1]
                for column, single_char in enumerate(row_data):
                    if not color:
                        color = (column, single_char.bg, single_char.fg)
                        char_set += single_char.data
                        continue
                    elif (color[1], color[2]) != (single_char.bg, single_char.fg):
                        color_list_item.append(
                            (row + tmp_bound[0], color[0] + tmp_bound[1], color[1], color[2], char_set))
                        color = (column, single_char.bg, single_char.fg)
                        char_set = single_char.data
                    else:
                        char_set += single_char.data

                if color:
                    color_list_item.append((row + tmp_bound[0], color[0] + tmp_bound[1], color[1], color[2], char_set))

                color_list.append(color_list_item)

            if not is_in_bound:
                self.__color_list = color_list
            else:
                self.__bound_color_list = color_list
        except Exception as ex:
            self.__logger.debug("error in __create_color_list {0}".format(ex))
            raise Exception(ex)

    def __get_border_by_colors(self, position, colors):
        # (row, col, bg, fg, char)
        try:
            border = [0xFFF, 0xFFF, -1, -1]  # start row, start_col, end_row, end_col
            for row_idx, row_list in enumerate(self.__color_list[position[0]:position[1]]):
                for ele in row_list:
                    if (ele[2], ele[3]) in colors:
                        tmp_border = [min(border[0], ele[0]),
                                      min(border[1], ele[1]),
                                      max(border[2], ele[0]),
                                      max(border[3], ele[1] + len(ele[4]) - 1)]
                        border = tmp_border

            if border == [0xFFF, 0xFFF, -1, -1]:
                return False, tuple(border)
            else:
                return True, tuple(border)
        except Exception as ex:
            self.__logger.error("error in __get_border_by_colors {0}".format(ex))
            raise Exception(ex)

    def __create_border_by_colors(self):
        try:
            if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
                cfg = self.__config["bios_boot_menu"]["border"]["Normal"]
                border = self.__get_border_by_colors(
                    cfg["position"], [cfg["border_color"], cfg["item_color"]])
                self.__border_group = [border]
            elif self.__bios_menu_type == BIOS_SETUP_MENU_TYPE:
                hearder_cfg = self.__config["bios_setup_menu"]["border"]["header"]
                popup_cfg = self.__config["bios_setup_menu"]["border"]["popup"]
                tail_cfg = self.__config["bios_setup_menu"]["border"]["tail"]
                header_border = self.__get_border_by_colors(
                    hearder_cfg["position"], [hearder_cfg["border_color"], hearder_cfg["item_color"]])

                tail_border = self.__get_border_by_colors(
                    tail_cfg["position"], [tail_cfg["border_color"]])
                first_line = 0xFFF
                second_line = 0
                if header_border[0]:
                    first_line = header_border[1][2] + 1
                if tail_border[0]:
                    second_line = tail_border[1][0] - 1
                popup_border = self.__get_border_by_colors(
                    (min(popup_cfg["position"][0], first_line),
                     max(second_line, popup_cfg["position"][1])),
                    [popup_cfg["border_color"], popup_cfg["item_color"]])

                self.__border_group = [header_border, popup_border, tail_border]
            else:
                raise Exception("bios_menu_type error {0}".format(self.__bios_menu_type))
        except Exception as ex:
            self.__logger.error("error in __create_border_by_colors {0}".format(ex))
            raise Exception(ex)

    def __get_condition_list(self, data, condition):
        pat = re.compile(condition)
        pat_list = []
        pos = 0
        while True:
            st = pat.search(data, pos)
            if not st:
                break

            pat_list.append((st.regs[0][0], data[st.regs[0][0]:st.regs[0][1]]))
            pos = st.regs[0][1]
        return pat_list

    def __is_border_start(self, data, cfg):
        if isinstance(cfg["top"], dict):
            top_cnd, top_pos = cfg["top"]["cnd"], cfg["top"]["pos"]
        else:
            top_cnd, top_pos = cfg["top"], None

        ret_top = self.__get_condition_list(data, top_cnd)
        if ret_top and top_pos:
            ret_pos = self.__get_condition_list(data, top_pos)
            if ret_pos:
                ret_top = ret_pos
            else:
                return False, (None, None)

        if not ret_top:
            return False, (None, None)
        if len(ret_top) == 1:
            return True, ret_top
        elif len(ret_top) > 1:
            self.__logger.error("more border find")

        return False, (None, None)

    def __is_border_row(self, data, cfg):
        try:
            ret_left = self.__get_condition_list(data[0], cfg["left"])
            ret_right = self.__get_condition_list(data[-1], cfg["right"])

            return not (not ret_left or not ret_right)
        except Exception as ex:
            self.__logger.error("error in __is_border_row {0}".format(ex))
            raise Exception(ex)

    def __is_border_end(self, data, cfg):
        ret_end = self.__get_condition_list(data, cfg["bottom"])
        if not ret_end:
            return False
        return True

    def __is_border_mid(self, data, cfg):
        ret_end = self.__get_condition_list(data, cfg["mid"])
        if not ret_end:
            return False

        return True

    def __create_misc_bound(self, cfg, border):
        bound = [0xFFF, 0xFFF, -1, -1]
        mid = -1
        start_col = border[1]
        end_col = border[3] + 1
        ret_start = (False, [(None, None)])
        row_count = 0
        start_row = -1
        for idx, data in enumerate(self.__screen.display[border[0]:border[2] + 1]):
            if not ret_start[0]:
                ret_start = self.__is_border_start(data[border[1]:border[3] + 1], cfg)
                if ret_start[0]:
                    start_row = idx
                    start_col = border[1] + ret_start[1][0][0]
                    end_col = border[1] + ret_start[1][0][0] + len(ret_start[1][0][1])+1
            else:
                ret_row = self.__is_border_row(data[start_col:end_col], cfg)
                if ret_row:
                    ret_mid = self.__is_border_mid(data[start_col:end_col], cfg)
                    if ret_mid:
                        if mid == -1:
                            mid = idx
                        else:
                            bound = [mid + 1 + border[0],
                                     start_col,
                                     idx - 1 + border[0],
                                     end_col]

                            if not ("min_start_col" in cfg.keys() and cfg['min_start_col'] >= start_col):
                                self.__full_popup = True
                            break
                    row_count += 1
                else:
                    if row_count > 0:
                        ret_end = self.__is_border_end(data[start_col:end_col], cfg)
                        if ret_end:
                            bound = [max(mid, start_row) + 1 + border[0],
                                     start_col,
                                     idx - 1 + border[0],
                                     end_col]
                            if not ("min_start_col" in cfg.keys() and cfg['min_start_col'] >= start_col):
                                self.__full_popup = True
                        else:
                            bound = [max(mid, start_row) + 1 + border[0],
                                     start_col,
                                     idx + border[0],
                                     end_col]
                        break
                    else:
                        ret_start = self.__is_border_start(data[border[1]:border[3] + 1], cfg)
                        if ret_start[0]:
                            start_col = border[1] + ret_start[1][0][0]
                            end_col = border[1] + ret_start[1][0][0] + len(ret_start[1][0][1])
                            start_row = idx

        if bound == [0xFFF, 0xFFF, -1, -1] and row_count > 0 and ret_start[0]:
            if mid == -1:
                bound = [start_row + border[0] + 1,
                         start_col,
                         start_row + row_count + border[0],
                         end_col]
            else:
                bound = [mid + border[0] + 1,
                         start_col,
                         start_row + row_count + border[0] - (mid - start_row),
                         end_col]

        self.__logger.debug("__create_misc_bound out put {0}".format(bound))
        return bound

    def __get_workspace_bound_start(self, bound):
        cfg = self.__config["bios_setup_menu"]["workspace"]
        for row, ele in enumerate(self.__color_list):
            if bound[0] != 0xFFF:
                break

            if len(ele) == 1 and not str(ele[0][4]).strip() \
                    and ele[0][2] in cfg["split_bg_color"]:
                if row > 0:
                    bound[0] = ele[0][0]

            if cfg["prev_page_flag"]["charset"] in "".join(
                    [x[4] for x in ele]).strip() \
                    and cfg["prev_page_flag"]["color"] in [
                        (x[2], x[3]) for x in ele]:
                bound[0] = ele[0][0] + 1

    def __get_workspace_bound_end(self, bound):
        if bound[0] == 0xFFF:
            return

        cfg = self.__config["bios_setup_menu"]["workspace"]
        for row, ele in enumerate(self.__color_list[bound[0]:]):
            if len(ele) == 1 and not str(ele[0][4]).strip() \
                    and ele[0][2] in cfg["split_bg_color"]:
                bound[2] = max(bound[2], ele[0][0])

            if cfg["next_page_flag"]["charset"] in "".join(
                    [x[4] for x in ele]).strip() \
                    and cfg["next_page_flag"]["color"] in [
                        (x[2], x[3]) for x in ele]:
                bound[2] = ele[0][0] - 1

    def __get_lower_misc_bound(self, border, cfg):
        bound = [0xFFF, 0xFFF, -1, -1]
        for idx, data in enumerate(self.__screen.display[border[0]:border[2] + 1]):
            ret_left = self.__get_condition_list(data, cfg["left"])
            if not ret_left:
                continue
            if bound[0] == 0xFFF:
                bound[0] = idx + border[0]
                bound[1] = ret_left[0][0]
                if len(ret_left) > 1:
                    bound[3] = ret_left[-1][0] + len(ret_left[-1][1]) - 1
            bound[2] = idx + border[0]

        if bound == [0xFFF, 0xFFF, -1, -1]:
            prev_group = []
            max_len = 0
            for idx, line in enumerate(self.__color_list):
                colors = [(ele[2], ele[3]) for ele in line]
                if (cfg["item_color"] in colors or \
                    cfg["highlight_color"] in colors or cfg["border_color"] in colors) and \
                        self.__screen.display[idx][border[0]:].strip() \
                        and cfg["position"][0] <= idx < cfg["position"][1]:
                    prev_group.append(idx)
                    max_len = max(
                        max_len, len(self.__screen.display[idx][border[0]:].rstrip()))

            if prev_group:
                bound = [prev_group[0],
                         border[1],
                         prev_group[-1],
                         border[1] + max_len - 1]

        elif bound != [0xFFF, 0xFFF, -1, -1] and bound[3] == -1:
            bound[3] = border[3]
        self.__logger.debug("__get_lower_misc_bound OUTPUT {0}".format(bound))
        return bound

    def __create_popup_bound(self, border):
        cfg = self.__config["bios_setup_menu"]["border"]["popup"]
        bound = self.__create_misc_bound(cfg, border[1])

        return tuple(bound)

    def __create_bound(self):
        bound = [0xFFF, 0xFFF, -1, -1]

        if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
            cfg = self.__config["bios_boot_menu"]["border"]["Normal"]
            if self.__border_group and self.__border_group[0] and self.__border_group[0][0]:
                bound = self.__create_misc_bound(cfg, self.__border_group[0][1])
                if bound == [0xFFF, 0xFFF, -1, -1]:
                    bound = self.__get_lower_misc_bound(self.__border_group[0][1], cfg)
                    self.__full_boot_bound = False
                else:
                    self.__full_boot_bound = True
        elif self.__bios_menu_type == BIOS_SETUP_MENU_TYPE:
            if self.__border_group and self.__border_group[1][0]:
                cfg = self.__config["bios_setup_menu"]["border"]["popup"]
                bound = self.__create_misc_bound(cfg, self.__border_group[1][1])
            if not self.__full_popup:
                if self.__border_group and self.__border_group[0][0]:
                    bound[0] = self.__border_group[0][1][2] + 1
                if self.__border_group and self.__border_group[2][0]:
                    bound[2] = self.__border_group[2][1][0] - 1

                self.__get_workspace_bound_start(bound)
                self.__get_workspace_bound_end(bound)

                if bound[0] != 0xFFF and bound[2] != -1:
                    bound[1] = 0
                    bound[3] = self.__config["bios_setup_menu"]["workspace"]["description_start_column"] - 1
        else:
            raise Exception("bios_menu_type error {0}".format(self.__bios_menu_type))

        self.__bound = tuple(bound)

    def __get_description(self):
        """
        get description from screen description area
        :return:
        """
        description = ""
        if self.__is_popup() or self.__bios_menu_type != BIOS_SETUP_MENU_TYPE:
            return description

        cfg = self.__config["bios_setup_menu"]["workspace"]
        for ele in self.__color_list[self.__bound[0]:self.__bound[2] + 1]:
            for ele_item in ele:
                if (ele_item[2], ele_item[3]) in [cfg["description_color"]]:
                    if ele_item[1] >= cfg["description_start_column"]:
                        if description and not ele_item[4].strip():
                            return description

                        description = " ".join([description, ele_item[4].strip()]).strip()
                    elif ele_item[1] + len(ele_item[4]) >= \
                            cfg["description_start_column"]:
                        tmp_str = \
                            ele_item[4][cfg[
                                            "description_start_column"] - ele_item[1]:].strip()
                        if description and not tmp_str:
                            if description and not ele_item[4].strip():
                                return description

                        if tmp_str:
                            description = " ".join([description, tmp_str]).strip()

        return description

    def __get_highlight_list_in_bound(self, bound_color_list, cfg):
        ret_list = []
        for eles in bound_color_list:
            row_item = []
            for ele in eles:
                if (ele[2], ele[3]) in [cfg["highlight_color"]]:
                    row_item.append(ele)
            if row_item:
                ret_list.append(row_item)
        self.__logger.debug("__get_highlight_list {0}".format(ret_list))
        return ret_list

    def __get_highlight_list(self, cfg):
        ret_list = []
        for eles in self.__bound_color_list:
            row_item = []
            for ele in eles:
                if (ele[2], ele[3]) in [cfg["highlight_color"]]:
                    row_item.append(ele)
            if row_item:
                ret_list.append(row_item)
        self.__logger.debug("__get_highlight_list {0}".format(ret_list))
        return ret_list

    def __get_misc_highlight(self, highlight_list, cfg):
        highlight = (False, ("", "", "", (None, None, None)))
        hig_str = ""
        prev_hig = -1
        start_row = -1
        start_col = -1
        end_col = -1
        for line in highlight_list:
            line_data = "".join([x[4] for x in line])
            tmp_hig_str = self.__misc_row_strip(cfg, line_data)

            if not tmp_hig_str:
                continue

            if prev_hig != -1:
                if prev_hig + 1 != line[0][0]:
                    raise Exception("more highlight in bound")
                else:
                    hig_str = " ".join([hig_str, tmp_hig_str])
                    prev_hig = line[0][0]
            else:
                hig_str = " ".join([hig_str, tmp_hig_str])
                prev_hig = line[0][0]
                start_row = line[0][0]
                start_col = len(line_data) - \
                            len(line_data.lstrip(cfg['left'].strip(' ')).lstrip()) + \
                            self.__bound[1] - 1
            end_col = max(end_col,
                          len(line_data) - \
                          len(line_data.rstrip(cfg['right'].strip(' ')).rstrip()) + \
                          self.__bound[1] - 1
                          )

        if hig_str:
            highlight = (True, (hig_str.strip(), "", BIOS_UI_DIR_TYPE,
                                (start_row, start_col, end_col)))

        return highlight

    def __get_popup_highlight(self, highlight_list, cfg, bound):
        highlight = (False, ("", "", "", (None, None, None)))
        hig_str = ""
        prev_hig = -1
        start_row = -1
        start_col = -1
        end_col = -1
        for line in highlight_list:
            line_data = "".join([x[4] for x in line])
            tmp_hig_str = self.__misc_row_strip(cfg, line_data)

            if not tmp_hig_str:
                continue

            if prev_hig != -1:
                if prev_hig + 1 != line[0][0]:
                    raise Exception("more highlight in bound")
                else:
                    hig_str = " ".join([hig_str, tmp_hig_str])
                    prev_hig = line[0][0]
            else:
                hig_str = " ".join([hig_str, tmp_hig_str])
                prev_hig = line[0][0]
                start_row = line[0][0]
                start_col = len(line_data) - \
                            len(line_data.lstrip(cfg['left'].strip(' ')).lstrip()) + \
                            bound[1] - 1
            end_col = max(end_col,
                          len(line_data) - \
                          len(line_data.rstrip(cfg['right'].strip(' ')).rstrip()) + \
                          bound[1] - 1
                          )

        if hig_str:
            highlight = (True, (hig_str.strip(), "", BIOS_UI_DIR_TYPE,
                                (start_row, start_col, end_col)))

        return highlight

    def __get_highlight_item_value(self, cfg, start_row, row_count):
        value = ""
        name_need = True
        self.__logger.debug('__get_highlight_item_value')
        for idx, line in enumerate(self.__screen.display[start_row:self.__bound[2] + 1]):
            line_name = line[:cfg["item_value_start_column"]].strip()
            line_value = line[cfg["item_value_start_column"]: \
                cfg["description_start_column"]].strip()
            self.__logger.debug("name {0}, value{1}".format(line_name, line_value))
            if line_value:
                if line_name:
                    if idx < row_count:
                        value = " ".join([value, line_value]).strip()
                    else:
                        break
                else:
                    if name_need:
                        name_need = False
                        value = " ".join([value, line_value]).strip()
                    else:
                        break
            else:
                break
        self.__logger.debug("__get_highlight_item_value:{}".format(value))
        return value

    def __get_highlight_item_name(self, cfg, start_row, row_count):
        name = ""
        for idx, line in enumerate(self.__screen.display[start_row:self.__bound[3] + 1]):
            line_name = line[:cfg["item_value_start_column"]].strip()
            line_value = line[cfg["item_value_start_column"]: \
                cfg["description_start_column"]].strip()
            self.__logger.debug("name {0}, value{1}".format(line_name, line_value))
            if line_name:
                if line_value and idx >= row_count:
                    break
                name = " ".join([name, line_name]).strip()
            else:
                break

        self.__logger.debug("__get_highlight_item_name {0}".format(name))
        return name

    def __get_item_row_split_text(self, row_index, description_col):
        item_text = []
        cur_color = None
        value = ''
        converted = self.convert_buffer(self.__screen.buffer)
        for idx, sig_char in enumerate(converted[row_index][:description_col]):
            if not cur_color:
                cur_color = (idx, sig_char.bg, sig_char.fg)
                value = sig_char.data
            elif (cur_color[1], cur_color[2]) != (sig_char.bg, sig_char.fg):
                if value.strip():
                    item_text.append(value)
                value = sig_char.data
                cur_color = (idx, sig_char.bg, sig_char.fg)
            else:
                value = ''.join([value, sig_char.data])

        if value.strip():
            item_text.append(value)

        return item_text

    def __get_workspace_highlight(self, highlight_list, cfg):
        highlight = (False, ("", "", "", (None, None, None)))
        hig_str = ""
        prev_hig = -1
        start_row = -1
        row_count = 0
        start_col = 0xFFF
        end_col = -1
        for line in highlight_list:
            line_data = "".join([x[4] for x in line])
            tmp_hig_str = line_data.strip()

            if not tmp_hig_str:
                continue

            if prev_hig != -1:
                if prev_hig + 1 != line[0][0]:
                    raise Exception("more highlight in bound")
                else:
                    hig_str = " ".join([hig_str, tmp_hig_str]).strip()
                    prev_hig = line[0][0]
            else:
                hig_str = " ".join([hig_str, tmp_hig_str]).strip()
                prev_hig = line[0][0]
                start_row = line[0][0]

            row_count += 1
            cur_start_col = line[0][1] + (len(line_data) - len(line_data.lstrip()))
            cur_end_col = line[-1][1] + len(line[-1][4]) - 1 - (len(line_data) - len(line_data.rstrip()))
            start_col = min(start_col, cur_start_col)
            end_col = max(end_col, cur_end_col)
        self.__logger.debug(
            "start_col: {0}, end_col {1}, hig_str {2}, start_row {3}".format(
                start_col, end_col, hig_str, self.__screen.display[start_row]))
        if hig_str:
            if start_col >= cfg["item_value_start_column"]:
                name = self.__get_highlight_item_name(cfg, start_row, row_count)

                if name.strip():
                    highlight = (True, (name, hig_str, BIOS_UI_OPT_TYPE,
                                        (start_row, start_col, end_col)))
                else:
                    highlight = (True, (hig_str, "", BIOS_UI_DIR_TYPE,
                                        (start_row, start_col, end_col)))
            else:
                item_str = self.__screen.display[start_row][
                           :cfg["description_start_column"]]
                name_str = self.__screen.display[start_row][
                           :cfg["item_value_start_column"]]
                value_str = self.__screen.display[start_row][
                            cfg["item_value_start_column"]:cfg["description_start_column"]]

                text_list = self.__get_item_row_split_text(
                    start_row, cfg["description_start_column"])
                self.__logger.debug('text_list %s' % str(text_list))
                self.__logger.debug(
                    "item_str [%s], name_str [%s], value_str [%s]" % (
                        item_str, name_str, value_str))
                self.__logger.debug(
                    "item_str_x [%s]" % item_str.strip().lstrip('>').strip())

                if item_str.strip().lstrip('>').strip() in text_list or not value_str.strip():
                    self.__logger.debug('name only')
                    highlight = (True, (hig_str, "", BIOS_UI_DIR_TYPE,
                                        (start_row, start_col, end_col)))
                else:
                    value = self.__get_highlight_item_value(cfg, start_row, row_count)
                    self.__logger.debug(value)
                    if value:
                        highlight = (True, (hig_str, value, BIOS_UI_OPT_TYPE,
                                            (start_row, start_col, end_col)))
                    else:
                        highlight = (True, (hig_str, value, BIOS_UI_DIR_TYPE,
                                            (start_row, start_col, end_col)))

        return highlight

    def __get_highlight(self):
        """
        internal function to parse highlighted item
        Any item within bound matches the highlight color schema will be saved as a highlighted item
        :return:
        """
        self.__create_color_list(True)

        if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
            cfg = self.__config["bios_boot_menu"]["border"]["Normal"]
            highlight_list = self.__get_highlight_list(cfg)
            highlight = self.__get_misc_highlight(highlight_list, cfg)
        elif self.__bios_menu_type == BIOS_SETUP_MENU_TYPE:
            if self.__is_popup():
                cfg = self.__config["bios_setup_menu"]["border"]["popup"]
                highlight_list = self.__get_highlight_list(cfg)
                highlight = self.__get_misc_highlight(highlight_list, cfg)
            else:
                cfg = self.__config["bios_setup_menu"]["workspace"]
                highlight_list = self.__get_highlight_list(cfg)
                highlight = self.__get_workspace_highlight(highlight_list, cfg)
        else:
            raise Exception("__bios_menu_type error {0}".format(self.__bios_menu_type))

        self.__logger.debug("highlight: %s" % str(highlight))
        return highlight

    def __get_title(self):
        title = ""
        if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
            if self.__full_boot_bound:
                cfg = self.__config["bios_boot_menu"]["border"]["Normal"]

                boot_bound = self.__bound
                mid = -1
                for line in self.__screen.display[boot_bound[0]:boot_bound[2] + 1]:
                    if self.__is_border_mid(line[boot_bound[1]:boot_bound[3] + 1], cfg):
                        mid = line
                        break
                if mid != -1:
                    start = None
                    for line in self.__screen.display[self.__border_group[0][1][0]:mid]:
                        if not start:
                            start = self.__is_border_start(line[boot_bound[1]:boot_bound[3] + 1], cfg)
                            continue
                        title = " ".join([title, line[boot_bound[1]:boot_bound[3] + 1].lstrip(
                            cfg['left'].strip(' ')).rstrip(
                            cfg['right'].strip(' ')).strip(' ')])
        elif self.__bios_menu_type == BIOS_SETUP_MENU_TYPE:
            if self.__is_popup():
                cfg = self.__config["bios_setup_menu"]["border"]["popup"]
                popup = self.__bound
                mid = -1
                for line in self.__screen.display[popup[0]:popup[2] + 1]:
                    if self.__is_border_mid(line[popup[1]:popup[3] + 1], cfg):
                        mid = line
                        break
                if mid != -1:
                    start = None
                    for line in self.__screen.display[self.__border_group[1][1][0]:mid]:
                        if not start:
                            start = self.__is_border_start(line[popup[1]:popup[3] + 1], cfg)
                            continue
                        title = " ".join([title, line[popup[1]:popup[3] + 1].lstrip(
                            cfg['left'].strip(' ')).rstrip(
                            cfg['right'].strip(' ')).strip(' ')])
            else:
                if self.__border_group and self.__border_group[0] \
                        and self.__border_group[0][0]:
                    top = self.__border_group[0][1]
                    cfg = self.__config["bios_setup_menu"]["border"]["header"]
                    end = top[2]
                    if not self.__is_border_end(self.__screen.display[top[2]], cfg):
                        end += 1
                    for line in self.__screen.display[top[0] + 1:end]:
                        title = " ".join([
                            title, line.lstrip(
                                cfg['left'].strip(' ')).rstrip(
                                cfg['right'].strip(' ')).strip(' ')])
        else:
            raise Exception("__bios_menu_type error {0}".format(self.__bios_menu_type))
        return title.strip()

    def __get_bound(self):
        """

        :return: (top, left, right, bottom)
                (start_row, start_column, end_column, end_row)
        """
        bound = (self.__bound[0], self.__bound[1], self.__bound[3], self.__bound[2])
        return bound

    def __misc_row_strip(self, cfg, data):
        line = data.strip()
        line = line.lstrip(cfg['left'].replace(' ', ""))
        line = line.rstrip(cfg['right'].replace(' ', ""))
        return line.strip()

    def __get_popup_items(self, bound):
        items = []
        cfg = self.__config["bios_setup_menu"]["border"]["popup"]
        for idx, line in enumerate(
                self.__screen.display[bound[0]:bound[2] + 1]):
            items.append((self.__misc_row_strip(cfg, line[bound[1]:bound[3]]),
                          "", BIOS_UI_DIR_TYPE, idx + bound[0]))
        return items

    def __get_items(self):
        items = []
        if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
            cfg = self.__config["bios_boot_menu"]["border"]["Normal"]
            if self.__full_boot_bound:

                for idx, line in enumerate(
                        self.__screen.display[self.__bound[0]:self.__bound[2] + 1]):
                    items.append((self.__misc_row_strip(cfg, line),
                                  "", BIOS_UI_DIR_TYPE, idx + self.__bound[0]))
            else:

                for idx, line in enumerate(
                        self.__screen.display[self.__bound[0]:self.__bound[2] + 1]):
                    if not self.__is_border_mid(line[self.__bound[1]:self.__bound[3]], cfg):

                        items.append((self.__misc_row_strip(cfg, line),
                                      "", BIOS_UI_DIR_TYPE, idx + self.__bound[0]))
        elif self.__bios_menu_type == BIOS_SETUP_MENU_TYPE:
            if self.__full_popup:
                cfg = self.__config["bios_setup_menu"]["border"]["popup"]
                for idx, line in enumerate(
                        self.__screen.display[self.__bound[0]:self.__bound[2] + 1]):
                    items.append((self.__misc_row_strip(cfg, line),
                                  "", BIOS_UI_DIR_TYPE, idx + self.__bound[0]))
            else:
                cfg = self.__config["bios_setup_menu"]["workspace"]
                prev_value, prev_name, start_row = "", "", -1

                for idx, data in enumerate(self.__screen.display[self.__bound[0]:self.__bound[2] + 1]):
                    name = data[self.__bound[1]:cfg["item_value_start_column"]].strip()
                    value = data[cfg["item_value_start_column"]:self.__bound[3] + 1].strip()
                    full = data.strip()

                    if not full:
                        if prev_name:
                            if prev_value:
                                items.append((prev_name, prev_value, BIOS_UI_OPT_TYPE, start_row))
                            else:
                                items.append((prev_name, "", BIOS_UI_DIR_TYPE, start_row))
                            prev_name, prev_value, start_row = "", "", -1
                    elif name:
                        if prev_name:
                            if value:
                                items.append((prev_name, prev_value, BIOS_UI_OPT_TYPE, start_row))
                            else:
                                items.append((prev_name, "", BIOS_UI_DIR_TYPE, start_row))
                        prev_name, prev_value, start_row = \
                            name, value, self.__bound[0] + idx
                    elif value:
                        if prev_name:
                            prev_value = " ".join([prev_value, value])
                        else:
                            items.append((data, value, BIOS_UI_DIR_TYPE, self.__bound[0] + idx))
                            prev_name, prev_value, start_row = "", "", -1

                if prev_name:
                    if prev_value:
                        items.append((prev_name, prev_value, BIOS_UI_OPT_TYPE, start_row))
                    else:
                        items.append((prev_name, "", BIOS_UI_DIR_TYPE, start_row))
        else:
            raise Exception("__bios_menu_type error {0}".format(self.__bios_menu_type))
        return items

    def __is_popup(self):
        '''

        :return: True/False
        '''
        if self.__bios_menu_type == BIOS_BOOT_MENU_TYPE:
            return False

        return self.__full_popup

    def show_screen(self):
        '''

        :return:
        '''
        self.__logger.debug(
            "SCREEN RESOLUTION [%d*%d]" % (self.__screen.lines, self.__screen.columns))
        columns = self.__screen.columns
        self.__logger.debug("*%s*" % ("*" * columns))
        for line in self.__screen.display:
            self.__logger.debug("*%s*" % line)
        self.__logger.debug("*%s*" % ("*" * columns))
