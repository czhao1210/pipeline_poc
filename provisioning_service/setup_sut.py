import argparse
from requests.sessions import Session
import sys
parser = argparse.ArgumentParser()
parser.add_argument("--infra", type=str, help="specify the url of capi url", required=True)
parser.add_argument("--target", type=str, help="specify the sut/target name", required=False, default="na")
parser.add_argument("--ww", type=str, help="specify BKC ww", required=True)
parser.add_argument("--target_os", type=str, help="specify SUT OS", required=False, default="")
arg = parser.parse_args(sys.argv[1:])

def add_instrument(instrument_name, sut, infra, **kwargs):
    instrument_to_add = kwargs
    import json
    root = r"http://10.239.219.248:5555"
    source = f"{root}/instruments"
    with Session() as s:
        s.post(source, json=dict(instrument_data=instrument_to_add,
                                 sut=sut, infrastructure=infra,
                                 instrument=instrument_name))

def remove_instrument(instrument_name, sut, infra, seq_num):
    import json
    root = r"http://10.239.219.248:5555"
    source = f"{root}/instruments"
    with Session() as s:
        s.delete(source, json=dict(seq_num=seq_num,
                                 sut=sut, infrastructure=infra,
                                 instrument=instrument_name))

def provisioning(infra, sut, target_os, bios, bmc, cpld1, cpld2, ww):
    remove_instrument("simics", "na", "simcloud",0)
    import json
    root = r"http://10.239.219.248:5556"
    source = f"{root}/provisioning"
    with Session() as s:
        json_data = dict(infrastructure=infra, sut=sut, target_os=target_os,
                         bios=bios, bmc=bmc, cpld1=cpld1, cpld2=cpld2, ww=ww)
        resp = s.post(source, json=json_data, verify=False, timeout=600)
        data = json.loads(resp.content)
        print(data)
    add_instrument(instrument_name="simics", sut="na", infra="simcloud",
                   real_time="True", serial_port=2022, host_name=data["container_ip"], host_port="22",
                   host_username="czhao", host_password=r"80198789*m*", service_port=2023, os="centos_stream",
                   network_user="root", network_password="",
                   app=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{arg.ww}/simics",
                   project=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{arg.ww}",
                   script=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{arg.ww}/targets/birchstream/birchstream-ap.simics"
                   )

provisioning(infra=arg.infra, sut="na", target_os=arg.target_os,
             bios="bios", bmc="bmc", cpld1="cpld1", cpld2="cpld2", ww=arg.ww)