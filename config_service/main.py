from flask import Flask, jsonify, request
from db_untils.models.common import Connection
from db_untils.models.data_model import Pdu, Bmc, Ssh, Impl, Simics
app = Flask(__name__)

def to_yaml_dict(data_list, device_name):
    ret_dict = dict()
    if len(data_list) == 1:
        ret_dict[device_name] = data_list[0]
    elif len(data_list) > 1:
        for i in range(0, len(data_list)):
            ret_dict[f"{device_name}_{i}"] = data_list[i]
    return ret_dict



@app.route("/supported_instruments", methods=['GET'])
def get_supported_instruments():
    json_data = request.get_json()
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    supported = list()
    with Connection() as conn:
        if conn.filter_device(infra=infra, sut=sut, device="pdu"):
            supported.append("pdu")
        if conn.filter_device(infra=infra, sut=sut, device="bmc"):
            supported.append("bmc")
        if conn.filter_device(infra=infra, sut=sut, device="ssh"):
            supported.append("ssh")
        if conn.filter_device(infra=infra, sut=sut, device="simics"):
            supported.append("simics")
    return jsonify(supported)

@app.route("/instruments", methods=['GET'])
def get_instruments():
    json_data = request.get_json()
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    instrument_name = json_data["instrument"]
    instrument_list = list()
    with Connection() as conn:
        # bmc = conn.filter_device(infra=infra, sut=sut, device="bmc")
        instruments = conn.filter_device(infra=infra, sut=sut, device=instrument_name)
        # bmc_list = [Bmc(b).json_data for b in bmc]
        if instrument_name == "pdu":
            instrument_list = [Pdu(p).json_data for p in instruments]
        elif instrument_name == "bmc":
            instrument_list = [Bmc(p).json_data for p in instruments]
        elif instrument_name == "ssh":
            instrument_list = [Ssh(p).json_data for p in instruments]
        elif instrument_name == "simics":
            instrument_list = [Simics(p).json_data for p in instruments]

    ret_dict = dict()
    ret_dict.update(to_yaml_dict(instrument_list, instrument_name))
    return jsonify(ret_dict)


@app.route("/implements", methods=['GET'])
def get_impl():
    json_data = request.get_json()
    config_name = json_data["config_name"]
    infra = json_data["infrastructure"]
    impl_dict = dict()
    with Connection() as conn:
        impl = conn.filter_impl(config_name=config_name, infra=infra)
        for i in impl:
            provider_name = i["provider_name"]
            provider_impl = Impl(i).json_data
            provider_impl.pop("provider_name")
            if provider_name in impl_dict.keys():
                impl_dict[provider_name].append(provider_impl)
            else:
                impl_dict[provider_name] = [provider_impl]
    for k in impl_dict.keys():
        if isinstance(impl_dict[k], list) and len(impl_dict[k]) == 1:
            impl_dict[k] = impl_dict[k][0]
    return jsonify(impl_dict)


@app.route("/implements", methods=['DELETE'])
def remove_impl():
    json_data = request.get_json()
    config_name = json_data.get("config_name")
    infra = json_data.get("infrastructure")

    with Connection() as conn:
        if config_name and infra:
            conn.remove_generic("impl", config_name=config_name, infra=infra)
        elif config_name:
            conn.remove_generic("impl", config_name=config_name)
        elif infra:
            conn.remove_generic("impl", infra=infra)
        else:
            conn.remove_generic("impl")

        conn.commit()
    return jsonify(dict())

@app.route("/", methods=['GET'])
def dump():
    json_data = request.get_json()
    table = json_data["table"]
    pdus = list()
    with Connection() as conn:
        ret = conn.query(f"select * from {table};")
        return jsonify(ret)

@app.route("/instruments", methods=['PUT'])
def update_instruments():
    json_data = request.get_json()
    instrument_to_update = json_data["instrument_data"]
    num_of_instrument = len(list(instrument_to_update.values()))
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    instrument_name = json_data["instrument"]
    with Connection() as conn:
        instruments = conn.filter_device(infra=infra, sut=sut, device=instrument_name)
        for k, v in instrument_to_update.items():
            if instrument_name == k:
                instruments[0].update(instrument_to_update[instrument_name])
            else:
                import re
                m = re.match(f"{instrument_name}_(\d+)", k)
                idx = int(m.groups()[0])
                instruments[idx].update(v)
        pdu_list = [Pdu(p) for p in instruments]
        for p in pdu_list:
            conn.update(p)
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)


@app.route("/instruments", methods=['POST'])
def new_instrument():
    json_data = request.get_json()
    instrument_to_add = json_data["instrument_data"]
    instrument_name = json_data["instrument"]
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    id = 1
    seq_num = 0
    with Connection() as conn:
        instruments = conn.filter_device(infra=infra, sut=sut, device=instrument_name)
        id = conn.suggest_id(instrument_name)
        instrument_to_add["id"] = id
        instrument_to_add["seq_num"] = len(instruments)
        instrument_to_add["sut"] = sut
        instrument_to_add["infra"] = infra
        if instrument_name == "pdu":
            conn.add(Pdu(instrument_to_add))
        elif instrument_name == "bmc":
            conn.add(Bmc(instrument_to_add))
        elif instrument_name == "ssh":
            conn.add(Ssh(instrument_to_add))
        elif instrument_name == "simics":
            conn.add(Simics(instrument_to_add))
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)


@app.route("/implements", methods=['POST'])
def new_implement():
    json_data = request.get_json()
    impl_to_add = json_data["impl_data"]
    id = 1
    with Connection() as conn:
        impl_to_add["id"] = conn.suggest_id(table_name="impl")
        conn.add(Impl(impl_to_add))
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)


@app.route("/instruments", methods=['DELETE'])
def remove_instrument():
    json_data = request.get_json()
    instrument_name = json_data["instrument"]
    instrument_seq_to_remove = json_data["seq_num"]
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    with Connection() as conn:
        instruments = conn.filter_device(infra=infra, sut=sut, device=instrument_name)
        seq_num = 0
        for i in instruments:
            if instrument_seq_to_remove != i["seq_num"]:
                i["seq_num"] = seq_num
                seq_num += 1
                if instrument_name == "pdu":
                    conn.update(Pdu(i))
                elif instrument_name == "bmc":
                    conn.update(Bmc(i))
                elif instrument_name == "ssh":
                    conn.update(Ssh(i))
                elif instrument_name == "simics":
                    conn.update(Simics(i))
            else:
                if instrument_name == "pdu":
                    conn.remove(Pdu(i))
                elif instrument_name == "bmc":
                    conn.remove(Bmc(i))
                elif instrument_name == "ssh":
                    conn.remove(Ssh(i))
                elif instrument_name == "simics":
                    conn.remove(Simics(i))
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)




test="""
pdu_0:
    # provide one IP for access
    ip: <ip address>
    username: <user name>
    password: <password>
    port: <port number>
    # list all the outlets connected to SUT
    outlets:
        - <outlet number>
        - <outlet number>
    # PDU type. avaiable values: raritan, apc
    type: <pdu type>
pdu_1:
    # provide one IP for access
    ip: <ip address>
    username: <user name>
    password: <password>
    port: <port number>
    # list all the outlets connected to SUT
    outlets:
        - <outlet number>
        - <outlet number>
    # PDU type. avaiable values: raritan, apc
    type: <pdu type>
bmc:
# Device Information
    # Required. Or simply use the name "ip", if you only want one IP visible to the user.
    # if multiple ip configured, please use "_<num> as the suffix. e.g. ip_0, ip_1
    ip: <ip address>
    # Required. Please provide the credential of the administrator privilege.(for redfish / IPMI access)
    username: <user name>
    password: <password>
    # Required. The available values: dell, hp, intel idrac(=>dell), ilo (=>hp), rvp (=>intel) (reference validation platform)
    type: <bmc type>
"""
import yaml
print(yaml.safe_load(test))

app.run(host=r"0.0.0.0", port=5555)


# with Connection() as conn:
#     ret = conn.query("select * from pdu;")
#     print(ret)