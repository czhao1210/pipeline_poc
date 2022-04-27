import yaml
from requests.sessions import Session


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


_ww = r"2022ww15.5"
def provisioning(infra, sut, target_os, bios, bmc, cpld1, cpld2, ww):
    remove_instrument("simics", "na", "simcloud",0)
    import json
    root = r"http://localhost:5556"
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
                   app=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{_ww}/simics",
                   project=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{_ww}",
                   script=f"/nfs/site/disks/simcloud_users/czhao/workarea/projects/gnr-6.0/{_ww}/targets/birchstream/birchstream-ap.simics"
                   )

provisioning(infra="simcloud", sut="na", target_os="centos_stream",
             bios="bios", bmc="bmc", cpld1="cpld1", cpld2="cpld2", ww=_ww)

