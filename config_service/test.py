import yaml
from requests.sessions import Session

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
import json
root = r"http://localhost:5555"
source = f"{root}/pdu"
with Session() as s:
    # dump
    resp = s.get(root, json=dict(table="pdu"))
    print(json.loads(resp.content))
    #
    pdu_data_to_remove = dict(id=3)
    resp = s.delete(source, json=pdu_data_to_remove, verify=False)
    #
    json_data = dict(infrastructure="emr", sut="sut0")
    resp = s.get(source, json=json_data, verify=False)
    pdu_data = json.loads(resp.content)
    #
    pdu_data["pdu_1"]["ip"]=r"pdu_1.ip"
    s.put(source, json=dict(pdu_data=pdu_data, sut="sut0", infrastructure="emr"))
    print(f"data_to_update={pdu_data}")
    #
    json_data = dict(infrastructure="emr", sut="sut0")
    resp = s.get(source, json=json_data, verify=False)
    pdu_data = json.loads(resp.content)
    print(f"data_after_update={pdu_data}")
    #
    pdu_to_add = pdu_data["pdu_0"]
    s.post(source, json=dict(pdu_data=pdu_to_add, sut="sut0", infrastructure="emr"))

    #
    json_data = dict(infrastructure="emr", sut="sut0")
    resp = s.get(source, json=json_data, verify=False)
    pdu_data = json.loads(resp.content)
    print(f"data_after_add={pdu_data}")