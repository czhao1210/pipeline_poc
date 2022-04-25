import abc
import json
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


class Ssh(DataModel):
    def __init__(self, data):
        super().__init__(data)

    @property
    def hostname(self):
        return self._get_property(name="hostname")

    @property
    def username(self):
        return self._get_property(name="username")

    @property
    def password(self):
        return self._get_property(name="password")

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
    def real_time(self):
        return self._get_property(name="real_time")
    
    @property
    def serial_port(self):
        return self._get_property(name="serial_port")
    
    @property
    def host_name(self):
        return self._get_property(name="host_name")
    
    @property
    def host_port(self):
        return self._get_property(name="host_port")
    
    @property
    def host_username(self):
        return self._get_property(name="host_username")
    
    @property
    def host_password(self):
        return self._get_property(name="host_password")
    
    @property
    def service_port(self):
        return self._get_property(name="service_port")
    
    @property
    def os(self):
        return self._get_property(name="os")
    
    @property
    def network_user(self):
        return self._get_property(name="network_user")
    
    @property
    def network_password(self):
        return self._get_property(name="network_password")
    
    @property
    def app(self):
        return self._get_property(name="app")
    
    @property
    def script(self):
        return self._get_property(name="script")
    
    @property
    def project(self):
        return self._get_property(name="project")

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("sut")
        json_data.pop("infra")
        json_data.pop("id")
        return json_data

class Impl(DataModel):
    def __init__(self, data):
        super().__init__(data)
        if isinstance(data.get("parameters"), dict):
            self._data["parameters"] = json.dumps(data.get("parameters"))

    @property
    def config_name(self):
        return self._get_property(name="config_name")

    @property
    def provider_name(self):
        return self._get_property(name="provider_name")

    @property
    def label(self):
        return self._get_property(name="label")

    @property
    def use(self):
        return self._get_property(name="use")

    @property
    def parameters(self):
        params = self._get_property(name="parameters")
        if params:
            import json
            return json.loads(params)

    @property
    def json_data(self):
        json_data = self._data.copy()
        json_data.pop("config_name")
        json_data.pop("infra")
        json_data.pop("id")
        json_data["parameters"] = self.parameters
        return json_data