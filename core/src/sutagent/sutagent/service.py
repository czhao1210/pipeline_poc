#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 3/26/2020 3:24 PM
# @Author : xianxiaoyin

import os
import psutil
import sys
import subprocess
import time
import platform
import datetime

service_base_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
service_py_name = 'sut_agent.py'
python_path = sys.executable
py_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), service_py_name)
os_service_name = 'sutagent'

print('service_base_name:', service_base_name)
print('service_py_name:', service_py_name)
print('python_path:', python_path)
print('py_file:', py_file)


def __is_linux_host():
    return platform.system().lower() == 'linux'


def __is_windows_host():
    return platform.system().lower() == 'windows'


def __host_platform():
    return platform.system()


def __linux_cmd(cmd):
    try:
        print('RUN CMD >>: {0}'.format(cmd))
        ret = os.system(cmd)
        if ret != 0:
            return False
        return True
    except Exception as ex:
        print(ex)
        return False


def __linux_copy(src, dst):
    cmd = ''
    if not os.path.exists(src):
        return False

    if os.path.isfile(src):
        cmd = 'cp -f "{0}" "{1}"'.format(src, dst)
    elif os.path.isdir(src):
        cmd = 'cp -rf "{0}" "{1}"'.format(src, dst)

    if cmd:
        if __linux_cmd(cmd):
            return os.path.exists(dst)
    else:
        return False


def __check_python_process(proc_name):
    proc_namex = proc_name.split(os.sep)
    if not proc_namex:
        return False

    if proc_namex[-1].lower() in ['python', 'python.exe', 'python2', 'python3']:
        return True
    else:
        return False


def __have_python(arg_list):
    for x in arg_list:
        if __check_python_process(x):
            return True

    return False


def __scan_service():
    try:
        py_key = service_base_name + os.sep + service_py_name
        print('SERVER KEY py_key>>>: {0}'.format(py_key))
        ids = psutil.pids()
        id_list = []
        for idx in ids:
            try:
                px = psutil.Process(idx)

                if not __have_python([px.name()] + px.cmdline()):
                    continue

                print(px.name(), px.cmdline())

                for cmd in px.cmdline():
                    if py_key in cmd:
                        id_list.append(idx)
            except Exception as ex:
                print(ex)

        return id_list
    except Exception as ex:
        raise(ex)


def _check_os():
    try:
        if not os.path.exists('/etc/redhat-release'):
            return ''

        proc = subprocess.Popen('cat /etc/redhat-release', shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        print(out)
        for line in out.split(os.linesep):
            if 'fedora' in line.lower():
                return 'fedora'

        return ''
    except Exception as ex:
        print(ex)
        return ''


def __write_rc_service():
    try:
        rc_file = '/usr/lib/systemd/system/rc-local.service'
        if not os.path.exists(rc_file):
            print("rc file not exists {0}".format(rc_file))
            return
        f = open(rc_file, 'r')
        lines = f.readlines()
        flag = False
        for line in lines:
            line = line.replace(' ', '').lower()
            if '[Install]'.lower() in line:
                flag = True
                break

        f.close()
        if flag:
            return

        f = open(rc_file, 'a')
        f.write('\n[Install]\n')
        f.write('WantedBy=multi-user.target\n')
        f.flush()
        f.close()
        os.system('systemctl enable rc-local.service')
        os.system('systemctl start rc-local.service')
        os.system('systemctl status rc-local.service')
    except Exception as ex:
        print(ex)


def _check_des():
    try:
        rc_file = '/etc/rc.d/rc.local'
        f = open(rc_file, 'r')
        lines = f.readlines()
        flag = False
        for line in lines:
            line = line.replace(' ', '').lower()
            if '#!/bin/sh'.lower() in line:
                flag = True
                break

            if '#/bin/sh'.lower() in line:
                flag = True
                break

            if '#/bin/bash'.lower() in line:
                flag = True
                break

            if '#!/bin/bash'.lower() in line:
                flag = True
                break

        f.close()

        return flag
    except Exception as ex:
        print(ex)

    return True


def __write_profile(write):
    bkfile = None
    srcfile = '/etc/rc.local'
    if not os.path.exists(srcfile):
        print('src file {0} not found in host...'.format(srcfile))
        srcfile = ""
    des_flag = False
    if not srcfile:
        srcfile = '/etc/rc.d/rc.local'
        if not os.path.exists('/etc/rc.d/rc.local'):
            print('src file not found in host...')
            return False

        if _check_os() == 'fedora':
            __write_rc_service()
            if not _check_des():
                des_flag = True

    os.system('chmod +x "{0}"'.format(srcfile))

    try:
        bkfile = srcfile + '_{0}.bak'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        os.system('cp {0} {1}'.format(srcfile, bkfile))
        auto_start_line = 'nohup \"{0}\" \"{1}\" >\"{2}\" &'.format(python_path, py_file, os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'service.log'))
        fsrc = open(srcfile, 'w')
        fbak = open(bkfile, 'r')
        start_line = '## auto run cluster agent #############################'
        end_line = '## end auto run cluster agent #############################'
        if write:
            if des_flag:
                fsrc.write('#!/bin/sh' + os.linesep)

            start_flag = False
            while True:
                data = fbak.readline()
                if not data:
                    break

                if start_line in data:
                    start_flag = True
                    continue

                if end_line in data:
                    fsrc.write(start_line + os.linesep)
                    fsrc.write(auto_start_line + os.linesep)
                    fsrc.write(end_line + os.linesep)
                    continue

                fsrc.write(data)
            if not start_flag:
                fsrc.write(start_line + os.linesep)
                fsrc.write(auto_start_line + os.linesep)
                fsrc.write(end_line + os.linesep)
        else:
            start_flag = False
            while True:
                data = fbak.readline()
                if not data:
                    break

                if start_line in data:
                    start_flag = True
                    continue

                if end_line in data:
                    start_flag = False
                    continue

                if not start_flag:
                    fsrc.write(data)

        fsrc.close()
        fbak.close()
        print('write auto start success.......')
    except Exception as ex:
        print('write profile error {0}'.format(ex))
        if os.path.exists(bkfile):
            os.system('cp {0} {1}'.format(bkfile, srcfile))
        print('write auto start fail.......')
        return False


def __stop_service():
    try:
        print('stop service')
        for i in range(3):
            ids = __scan_service()
            if not ids:
                return True
            for x in ids:
                try:
                    th = psutil.Process(x)
                    print('task kill: ', x, th.name(), th.cmdline())
                    th.kill()
                except Exception as ex:
                    print(ex)
            time.sleep(10)

        print('stop service fail ... ')
        return False
    except Exception as ex:
        print(ex)
        return False


def __start_service():
    print('start_service')
    if not os.path.exists(python_path):
        print('python_path {0} not exist'.format(python_path))
        return

    if not os.path.exists(py_file):
        print('python_path {0} not exist'.format(py_file))
        return

    if __is_windows_host():
        cmd = 'start /D \"{0}\" {1} \"{2}\"'.format(os.path.dirname(python_path), os.path.basename(python_path), py_file)
    elif __is_linux_host():
        if __check_gnome_desktop():
            cmd = "gnome-terminal --geometry=120x25+200+10 -x bash -c \"{0}\"".format(
                "\"{0}\" \"{1}\"".format(python_path, py_file)
            )
        else:
            cmd = 'nohup \'{0}\' \'{1}\' >\'{2}\' &'.format(python_path, py_file, os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'service.log'))
    else:
        print('start fail os not config {0}'.format(__host_platform()))
        return

    print('cmd', cmd)
    os.system(cmd)

    ids = __scan_service()
    if ids:
        print('start_service SUCCESS pid is {0}'.format(ids))
    else:
        print('start service fail...')

    print('start_service end')


def __remove_service():
    try:
        print('remove service')
        if __is_linux_host():
            if __check_gnome_desktop():
                print('gnome desktop env')
                if os.path.exists(os.path.join('/root/.config/autostart', '{0}.desktop'.format(os_service_name))):
                    os.remove(os.path.join('/root/.config/autostart', '{0}.desktop'.format(os_service_name)))
            else:
                print('not gnome desktop env')
                __write_profile(False)
        else:
            print('del auto start in windows'.format(os_service_name))
            os.system(r'reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "{0}" /f 2> nul'.format(os_service_name))
            print('del auto start in windows done.'.format(os_service_name))
        print('remove service end')
    except Exception as ex:
        print(ex)
        print('remove service fail')
        return


def __check_gnome_desktop():
    proc = subprocess.Popen('ps -A | egrep -i "gnome|kde|mate|cinnamon|lx|xfce|jwm"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    for line in out.split(os.linesep):
        if 'gnome-session' in line.lower():
            return True

    return False


def __install_service():
    try:
        print('install auto start service')
        if __is_linux_host():
            if __check_gnome_desktop():
                print('gnome desktop env')
                if os.path.exists(os.path.join('/root/.config/autostart', '{0}.desktop'.format(os_service_name))):
                    os.remove(os.path.join('/root/.config/autostart', '{0}.desktop'.format(os_service_name)))
                os.system('[ ! -d /root/.config/autostart ] && mkdir -p /root/.config/autostart')
                os.system(
                    'echo -e "[Desktop Entry]\nType=Application\nExec={0}\nX-GNOME-Autostart-enabled=true" > /root/.config/autostart/{1}.desktop'.format(
                        '{0} "{1}" start'.format(python_path, os.path.abspath(__file__)), os_service_name))
                if not os.path.exists(os.path.join('/root/.config/autostart', '{0}.desktop'.format(os_service_name))):
                    print('install auto start service Failed....')
                else:
                    print('install auto start service success....')
            else:
                print('not gnome desktop env')
                __write_profile(True)
                pass
        else:
            print('add auto key')
            os.system(
                'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "{0}" /t REG_SZ /d "{1}" /f'.format(
                    os_service_name,
                    'python \\\"{0}\\\" start'.format(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'service.py'))
                ))
            print('add auto key done.')
    except Exception as ex:
        print(ex)
        print('install service fail')
        return

    print('install service end')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print('no option input')
        exit(0)

    if args[0].lower() == 'start':
        srv = __scan_service()
        if srv:
            print('service is running ...')
            try:
                print(srv[0], psutil.Process(srv[0]).name(), psutil.Process(srv[0]).cmdline())
            except BaseException:
                pass
        else:
            __start_service()
            if not __scan_service():
                raise Exception('start service fail...')
            else:
                print('start service done.')
    elif args[0].lower() == 'stop':
        __stop_service()
    elif args[0].lower() == 'restart':
        __stop_service()
        __start_service()
    elif args[0].lower() in ['remove', 'uninstall']:
        __stop_service()
        __remove_service()
    elif args[0].lower() == 'install':
        __stop_service()
        __remove_service()
        __install_service()
    elif args[0].lower() in ['state', 'status']:
        ret = __scan_service()
        if ret:
            print('service is running', ret)
        else:
            print('service is stopped')
    else:
        print('no option input not support {0}'.format(args[0]))
        exit(0)
