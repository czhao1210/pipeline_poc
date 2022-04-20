from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class RedfishDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(RedfishDriverConfig, self).__init__(cfg_opts, log)
        try:
            driver_name = list(cfg_opts.keys())[0]
            cfg_dict = dict(cfg_opts)
            self.__ip = cfg_dict[driver_name][r"ip"].strip()
            self.__username = cfg_dict[driver_name][r"username"].strip()
            self.__password = cfg_dict[driver_name][r"password"].strip()
        except KeyError as k_e:
            self.__ip = None
            self.__username = None
            self.__password = None

        self.__ip = cfg_dict[driver_name].get("ip")

        try:
            self.__image_name = cfg_dict[driver_name][r"image_name_bmc"].strip()
        except KeyError as k_e:
            self.__image_name = None

        try:
            self.__image_path = cfg_dict[driver_name][r"image_path_bmc"].strip()
        except KeyError as attrib_err:
            self.__image_path = None

        try:
            self.__image_name_bios = cfg_dict[driver_name][r"image_name_bios"].strip()
        except Exception as ex:
            self.__image_name_bios = None
        try:
            self.__image_path_bios = cfg_dict[driver_name][r"image_path_bios"].strip()
        except Exception as ex:
            self.__image_path_bios = None

        try:
            self.__image_name_cpld = cfg_dict[driver_name][r"image_name_cpld"].strip()
        except Exception as ex:
            self.__image_name_cpld = None
        try:
            self.__image_path_cpld = cfg_dict[driver_name][r"image_path_cpld"].strip()
        except Exception as ex:
            self.__image_path_cpld = None

        try:
            self.__bmc_type = cfg_dict[driver_name][r"bmc_type"].strip()
        except Exception:
            self.__bmc_type = None
        if self.__bmc_type in ["aurora"]:
            self.__blade = cfg_dict[driver_name].get("blade")
            try:
                self.__chassis_username = cfg_dict[driver_name].get("chassis").get("username")
                self.__chassis_password = cfg_dict[driver_name].get("chassis").get("password")
                self.__chassis_server = cfg_dict[driver_name].get("chassis").get("server")
                self.__chassis_port = int(cfg_dict[driver_name].get("chassis").get("port"))
            except:
                self.__chassis_username = r"root"
                self.__chassis_password = r"initial0"
                self.__chassis_server = r"localhost"
                self.__chassis_port = 92
            try:
                self.__system_username = cfg_dict[driver_name].get("system").get("username")
                self.__system_password = cfg_dict[driver_name].get("system").get("password")
                self.__system_server = cfg_dict[driver_name].get("system").get("server")
                self.__system_port = int(cfg_dict[driver_name].get("system").get("port"))
            except:
                self.__system_username = r"admin"
                self.__system_password = r"initial0"
                self.__system_server = r"localhost"
                self.__system_port = 5443
            try:
                self.__safe_time = int(cfg_dict[driver_name].get("safe_time"))
            except Exception as ex:
                self.__safe_time = 15

        try:
            self.__image_username = cfg_dict[driver_name]["flash_image"][r"image_username"].strip()
        except Exception:
            self.__image_username = None

        try:
            self.__image_password = cfg_dict[driver_name]["flash_image"][r"image_password"].strip()
        except Exception:
            self.__image_password = None

        try:
            self.__transferprotocol = cfg_dict[driver_name]["flash_image"][r"transferprotocol"].strip()
        except Exception:
            self.__transferprotocol = None

        try:
            self.__bmc_mac = cfg_dict[driver_name][r"mac"].strip()
        except Exception as ex:
            self.__bmc_mac = None

        try:
            self.__session = cfg_dict[driver_name][r"session"].strip()
        except Exception as ex:
            self.__session = None

    @property
    def ip(self):
        return self.__ip

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def image_name(self):
        return self.__image_name

    @property
    def image_path(self):
        return self.__image_path

    @property
    def image_name_bios(self):
        return self.__image_name_bios

    @property
    def image_path_bios(self):
        return self.__image_path_bios

    @property
    def image_name_cpld(self):
        return self.__image_name_cpld

    @property
    def image_path_cpld(self):
        return self.__image_path_cpld

    @property
    def blade(self):
        return self.__blade

    @property
    def safe_time(self):
        return self.__safe_time

    @property
    def chassis_username(self):
        return self.__chassis_username

    @property
    def chassis_password(self):
        return self.__chassis_password

    @property
    def chassis_server(self):
        return self.__chassis_server

    @property
    def chassis_port(self):
        return self.__chassis_port

    @property
    def system_username(self):
        return self.__system_username

    @property
    def system_password(self):
        return self.__system_password

    @property
    def system_server(self):
        return self.__system_server

    @property
    def system_port(self):
        return self.__system_port

    @property
    def bmc_type(self):
        if ((str(self.__bmc_type)).lower() in ["dell","idrac"]):
            self.__bmc_type = "idrac"
            return self.__bmc_type
        elif((str(self.__bmc_type)).lower() in ["hp", "ilo"]):
            self.__bmc_type = "ilo"
            return self.__bmc_type
        elif ((str(self.__bmc_type)).lower() in ["supermicron", "sm"]):
            self.__bmc_type = "sm"
            return self.__bmc_type
        elif ((str(self.__bmc_type)).lower() in ["aurora"]):
            self.__bmc_type = "aurora"
            return self.__bmc_type
        else:
            self.__bmc_type = "rvp"
            return self.__bmc_type

    @property
    def image_username(self):
        return self.__image_username

    @property
    def image_password(self):
        return self.__image_password

    @property
    def transferprotocol(self):
        return self.__transferprotocol

    @property
    def bmc_mac(self):
        return self.__bmc_mac

    @property
    def session(self):
        if ((str(self.__session)).lower() in ["no","false","disable"]):
            self.__session = False
        else:
            self.__session = True
        return self.__session
