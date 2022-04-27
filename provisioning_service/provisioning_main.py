import datetime
import time

from flask import Flask, jsonify, request
app = Flask(__name__)
from utils import ProvisioningTask, Pool
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