import datetime
import time

from flask import Flask, jsonify, request
from requests import Session

app = Flask(__name__)
from utils import ProvisioningTask, Pool

def get_instrument_info(instrument_name, sut, infra, root):
    import json
    root = "http://10.239.219.248:5558"
    source = f"{root}/instruments"
    with Session() as s:
        json_data = dict(infrastructure=infra, sut=sut, instrument=instrument_name)
        resp = s.get(source, json=json_data, verify=False)
        try:
            return json.loads(resp.content)
        except json.decoder.JSONDecodeError as e:
            print(e)
            return resp.content

@app.route("/provisioning", methods=['GET'])
def provision():
    json_data = request.get_json()
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    instrument_name = json_data["instrument"]
    return jsonify(get_instrument_info(instrument_name=instrument_name, sut=sut, infra=infra, root="http://10.239.219.248:5558"))


@app.route("/provisioning", methods=['POST'])
def provision():
    json_data = request.get_json()
    target_os = json_data["target_os"]
    sut = json_data["sut"]
    infra = json_data["infrastructure"]
    bios = json_data["bios"]
    bmc = json_data["bmc"]
    cpld1 = json_data["cpld1"]
    cpld2 = json_data["cpld2"]
    ww = json_data["ww"]
    t = ProvisioningTask(hostname=r"simcloud0.intel.com", port="22",
                         username="czhao", password=r"80198789*m*", ww=ww)
    __start = datetime.datetime.now()
    while not t.container_ip and (datetime.datetime.now() - __start).seconds < 1800:
        time.sleep(5)
    task_list = list()
    try:
        for i in Pool.tasks:
            if i.is_stopped:
                i.join(timeout=30)
            else:
                task_list.append(i)
    except Exception as ex:
        print(ex)
    task_list.append(t)
    Pool.tasks = task_list
    return jsonify(dict(container_ip=t.container_ip))

app.run(host=r"0.0.0.0", port=5556)