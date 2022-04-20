import abc
class DataModel(object):
    def __init__(self, data):
        self._data = data


    @property
    def data(self):
        return self._data

    def _get_property(self, name):
        if name in self._data.keys():
            return self._data[name]
        else:
            return None

    def _set_property(self, name, value):
        self._data[name] = value

    @property
    def id(self):
        return self._get_property("id")

    @property
    def infrastructure(self):
        return self._get_property("infra")

    @property
    def sut(self):
        return self._get_property("sut")

    @property
    def json_data(self):
        raise NotImplementedError

class Bmc(DataModel):
    def __init__(self, data):
        super().__init__(data)

    @property
    def ip(self):
        return self._get_property(name="ip")

    @property
    def username(self):
        return self._get_property(name="username")

    @property
    def password(self):
        return self._get_property(name="password")

    @property
    def type(self):
        return self._get_property(name="type")

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("sut")
        json_data.pop("infra")
        json_data.pop("id")
        json_data.pop("seq_num")
        return json_data


class Pdu(DataModel):
    def __init__(self, data):
        super().__init__(data)
        if isinstance(data.get("outlets"), list):
            self._data["outlets"] = ",".join([str(o) for o in data["outlets"]])

    def update(self, cur):
        value_list = list()
        for k, v in self.data.items():
            if isinstance(v, str):
                value_list.append(f"{k}=\"{v}\"")
            else:
                value_list.append(f"{k}={v}")
        sql = f"""
        update pdu set {",".join(value_list)} where id = {self.id};
        """
        cur.execute(sql)

    @property
    def ip(self):
        return self._get_property(name="ip")

    @ip.setter
    def ip(self, value):
        self._set_property(name="ip", value=value)

    @property
    def port(self):
        return self._get_property(name="port")

    @port.setter
    def port(self, value):
        self._set_property(name="port", value=value)

    @property
    def username(self):
        return self._get_property(name="username")

    @username.setter
    def username(self, value):
        self._set_property(name="username", value=value)

    @property
    def password(self):
        return self._get_property(name="password")

    @password.setter
    def password(self, value):
        self._set_property(name="password", value=value)

    @property
    def outlets(self):
        return [int(v) for v in self._get_property(name="outlets").split(",")]

    @outlets.setter
    def outlets(self, values):
        outlet_value = ",".join([str(o) for o in values])
        self._set_property(name="outlets", value=outlet_value)


    @outlets.setter
    def type(self, value):
        self._set_property(name="type", value=value)

    @property
    def type(self):
        return self._get_property(name="type")

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("sut")
        json_data.pop("infra")
        json_data.pop("id")
        json_data.pop("seq_num")
        json_data["outlets"] = self.outlets
        return json_data


class Capi(DataModel):
    def __init__(self, data):
        super().__init__(data)

    @property
    def server(self):
        return self._get_property(name="server")

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("sut")
        json_data.pop("infra")
        json_data.pop("id")
        return json_data



class Simics(DataModel):
    def __init__(self, data):
        super().__init__(data)

    @property
    def host_address(self):
        return self._get_property(name="host_address")

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("sut")
        json_data.pop("infra")
        json_data.pop("id")
        return json_data