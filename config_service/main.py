from flask import Flask, jsonify, request
from db_untils.models.common import Connection
from db_untils.models.data_model import Pdu, Bmc
app = Flask(__name__)

def to_yaml_dict(data_list, device_name):
    ret_dict = dict()
    if len(data_list) == 1:
        ret_dict[device_name] = data_list[0]
    elif len(data_list) > 1:
        for i in range(0, len(data_list)):
            ret_dict[f"{device_name}_{i}"] = data_list[i]
    return ret_dict

@app.route("/pdu", methods=['GET'])
def get_pdu():
    json_data = request.get_json()
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    pdus = list()
    with Connection() as conn:
        bmc = conn.filter_device(infra=infra, sut=sut, device="bmc")
        pdus = conn.filter_device(infra=infra, sut=sut, device="pdu")
        bmc_list = [Bmc(b).json_data for b in bmc]
        pdu_list = [Pdu(p).json_data for p in pdus]
    ret_dict = dict()
    ret_dict.update(to_yaml_dict(pdu_list, r"pdu"))
    #ret_dict.update(to_yaml_dict(bmc_list, r"bmc"))
    return jsonify(ret_dict)


@app.route("/", methods=['GET'])
def dump():
    json_data = request.get_json()
    table = json_data["table"]
    pdus = list()
    with Connection() as conn:
        ret = conn.query(f"select * from {table};")
        return jsonify(ret)

@app.route("/pdu", methods=['PUT'])
def update_pdu():
    json_data = request.get_json()
    pdu_to_update = json_data["pdu_data"]
    num_of_pdu = len(list(pdu_to_update.values()))
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    with Connection() as conn:
        pdus = conn.filter_device(infra=infra, sut=sut, device="pdu")
        for k, v in pdu_to_update.items():
            if "pdu" == k:
                pdus[0].update(pdu_to_update["pdu"])
            else:
                import re
                m = re.match("pdu_(\d+)", k)
                idx = int(m.groups()[0])
                pdus[idx].update(v)
        pdu_list = [Pdu(p) for p in pdus]
        for p in pdu_list:
            conn.update(p)
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)


@app.route("/pdu", methods=['POST'])
def new_pdu():
    json_data = request.get_json()
    pdu_to_add = json_data["pdu_data"]
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    id = 1
    seq_num = 0
    with Connection() as conn:
        pdus = conn.filter_device(infra=infra, sut=sut, device="pdu")
        if pdus:
            id = pdus[-1]["id"] + 1
            seq_num = pdus[-1]["seq_num"] + 1
        pdu_to_add["id"] = id
        pdu_to_add["seq_num"] = seq_num
        pdu_to_add["sut"] = sut
        pdu_to_add["infra"] = infra
        conn.add(Pdu(pdu_to_add))
        conn.commit()
    ret_dict = dict()
    return jsonify(ret_dict)


@app.route("/pdu", methods=['DELETE'])
def remove_pdu():
    json_data = request.get_json()
    pdu_id_to_remove = json_data["id"]
    with Connection() as conn:
        conn.remove(Pdu(dict(id=pdu_id_to_remove)))
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