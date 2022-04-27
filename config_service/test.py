import yaml
from requests.sessions import Session

cfg = """
flash:
    - 
        label: SX 
        use: banino
    - 
        label: CPLD  
        use: usbblaster
        
ac:
    use: pdu
"""
import yaml

cfg = yaml.safe_load(cfg)
print(cfg)

devices = yaml.safe_load(
"""
# PDU is mainly used for AC Power Control
# If only one PDU is attached, DTAF Core will use pdu by default.
# If multiple PDUs are attached, use "_<num>" as suffix. e.g. pdu_0, pdu_1
pdu:
    # provide one IP for access
    ip: <ip address>
    user: <user name>
    password: <password>
    port: <port number>
    # list all the outlets connected to SUT
    outlets:
        - <outlet number>
        - <outlet number>
    # PDU type. avaiable values: raritan, apc
    type: <pdu type>

""")


def dump_instruments(instrument_name):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/instruments"
    with Session() as s:
        json_data = dict(infrastructure="emr", sut="sut0", instrument=instrument_name)
        resp = s.get(source, json=json_data, verify=False)
        instrument_data = json.loads(resp.content)
        for item in instrument_data.items():
            print(item)

def get_instrument_info(instrument_name, sut, infra):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/instruments"
    with Session() as s:
        json_data = dict(infrastructure=infra, sut=sut, instrument=instrument_name)
        resp = s.get(source, json=json_data, verify=False)
        try:
            return json.loads(resp.content)
        except json.decoder.JSONDecodeError as e:
            return dict()

def update_instrument_info(infra, sut, instrument_name, instrument_data):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/instruments"
    with Session() as s:
        s.put(source, json=dict(instrument_data=instrument_data,
                                sut=sut, infrastructure=infra, instrument=instrument_name))
        print(f"data_to_update={instrument_data}")

def add_instrument(instrument_name, sut, infra, **kwargs):
    instrument_to_add = kwargs
    import json
    root = r"http://localhost:5555"
    source = f"{root}/instruments"
    with Session() as s:
        s.post(source, json=dict(instrument_data=instrument_to_add,
                                 sut=sut, infrastructure=infra,
                                 instrument=instrument_name))

def remove_instrument(instrument_name, sut, infra, seq_num):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/instruments"
    with Session() as s:
        s.delete(source, json=dict(seq_num=seq_num,
                                 sut=sut, infrastructure=infra,
                                 instrument=instrument_name))

def get_supported_instruments(sut, infra):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/supported_instruments"
    with Session() as s:
        json_data = dict(infrastructure=infra, sut=sut)
        resp = s.get(source, json=json_data, verify=False)
        return json.loads(resp.content)

def get_implements(infra, config_name):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/implements"
    with Session() as s:
        json_data = dict(infrastructure=infra, config_name=config_name)
        resp = s.get(source, json=json_data, verify=False)
        return json.loads(resp.content)

def get_provider_impl(provider_name, infra, config_name):
    ret_dict = get_implements(config_name=config_name, infra=infra)
    return ret_dict.get(provider_name) if provider_name in ret_dict.keys() else {}

def remove_implements(config_name, infra):
    import json
    root = r"http://localhost:5555"
    source = f"{root}/implements"
    with Session() as s:
        s.delete(source, json=dict(config_name=config_name,
                                   infrastructure=infra))

def cleanup_implements():
    import json
    root = r"http://localhost:5555"
    source = f"{root}/implements"
    with Session() as s:
        s.delete(source, json=dict())


def add_impl(**kwargs):
    impl_to_add = kwargs
    import json
    root = r"http://localhost:5555"
    source = f"{root}/implements"
    with Session() as s:
        s.post(source, json=dict(impl_data=impl_to_add))

def dump(table):
    import json
    root = r"http://10.239.219.248:5555"
    source = f"{root}/"
    with Session() as s:
        ret = s.get(source, json=dict(table=table))
        return json.loads(ret.content)


# add_impl(provider_name="ac", label="PDU", use="pdu", config_name="default", infra="emr")
# add_impl(provider_name="dc", label="", use="bmc", config_name="default", infra="emr")
# add_impl(provider_name="sut_os", label="", use="ssh", config_name="default", infra="emr")
# add_instrument(instrument_name="ssh", sut="sut0", infra="emr",
#                hostname="sut0_host",port="22",
#                username="username_ssh", password="password_ssh")
# add_instrument(instrument_name="pdu", sut="sut0", infra="emr",
#                ip="pdu.ip", username="pdu_username", password="password_pdu", port="22", outlets=[11,22], type="raritan")

"""
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    real_time text,
    serial_port int not null,
    host_name text,
    host_port text,
    host_username text,
    host_password text,
    service_port int,
    os,
    network_user text,
    network_password text,
    app text,
    project text,
    script text
"""
# add_instrument(instrument_name="simics", sut="na", infra="simcloud",
#                real_time="True", serial_port=2022, host_name=r"", host_port="22",
#                host_username="czhao", host_password=r"80198789*m*", service_port=2023, os="centos_stream",
#                network_user="root", network_password="",
#                app=r"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2022ww15.5/simics",
#                project=r"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2022ww15.5",
#                script=r"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/2022ww15.5/targets/birchstream/birchstream-ap.simics"
#                )
print(dump("simics"))
exit(0)
print(get_instrument_info("simics", "na", "simcloud"))
# remove_instrument("simics", "na", "simcloud",0)
# print("### dump impl ###")
# print(dump("impl"))
# print("### dump pdu ###")
# print(dump("pdu"))
# print("### dump bmc ###")
# print(dump("bmc"))
# print("### dump ssh ###")
# print(dump("ssh"))
print("### list supported instruments ###")
print(get_supported_instruments("sut0", "emr"))
print("### get instrument info ###")
print(get_instrument_info("pdu", "sut0", "emr"))
print(get_instrument_info("bmc", "sut0", "emr"))
print(get_instrument_info("ssh", "sut0", "emr"))
print("### get implement info ###")
print(f"ac impl={get_provider_impl('ac', 'emr', 'default')}")
print(f"dc impl={get_provider_impl('dc', 'emr', 'default')}")
print(f"sut_os impl={get_provider_impl('sut_os', 'emr', 'default')}")
# print(get_provider_impl("sut_os", "emr", "default"))
# remove_instrument(instrument_name="ssh", sut="sut0", infra="ssh", seq_num=0)
# remove_implements(config_name="default", infra=None)

# params = dict()
# add_impl(config_name="default", provider_name="ac", use="pdu", infra="emr",
#          label="", parameters=params)
# print(f"impl after add={get_implements('emr', 'default')}")
#
# print(get_provider_impl("ac",config_name="default", infra="emr"))
# remove_implements(config_name="default", infra="emr")
# print(f"impl after del={get_implements('emr', 'default')}")

# dump_instruments(instrument_name="pdu")
# instrument_data = get_instrument_info("pdu", "sut0", "emr")
# instrument_data["pdu_0"]["ip"] = r"pdu_0.ip"
# update_instrument_info("emr", "sut0", "pdu", instrument_data)
# dump_instruments(instrument_name="pdu")
# add_instrument("pdu", "sut0", "emr", ip="pdu.ip", outlets=[3,4,5], password="password0",
#                port="22", type="raritan", username="username0")
# print("after add")
# dump_instruments(instrument_name="pdu")
# remove_instrument("pdu", "sut0", "emr", 3)
# print("after remove")
# dump_instruments(instrument_name="pdu")
