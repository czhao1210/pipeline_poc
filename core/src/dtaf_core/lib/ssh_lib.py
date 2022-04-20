import os
import time

import paramiko


class SSHlib(object):
    """Upload and download files and folders through SSH."""

    def __init__(self, ip, port, username, password):
        # type: (str,int,str,str) -> None

        try:
            self.__ip = ip
            self.__port = port
            self.__username = username
            self.__password = password
            self.__transport = paramiko.Transport(self.__ip, self.__port)
            self.__transport.connect(username=self.__username, password=self.__password)
            self.sftp = paramiko.SFTPClient.from_transport(self.__transport)

            self.__ssh = paramiko.SSHClient()
            self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh.connect(hostname=self.__ip, port=self.__port, username=self.__username, password=self.__password)
        except Exception as e:
            raise e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def upload(self, localhost_path, server_path):
        # type: (str,str) -> None
        """upload file or folder"""

        if os.path.isdir(localhost_path):
            stdin, stdout, stderr = self.__ssh.exec_command('cd %s' % (server_path))
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            path_add = ''
            if not result:
                path_add = localhost_path.replace('\\', '/').split('/')[-1]
            if server_path.endswith('/'):
                server_path = server_path[:-1]
            server_path = server_path + '/' + path_add
            self.__upload_directory(localhost_path, server_path)
        else:
            self.__upload_file(localhost_path, server_path)

    def download(self, server_path, localhost_path):
        # type: (str,str) -> None
        """download file or folder"""

        stdin, stdout, stderr = self.__ssh.exec_command('cd %s' % (server_path))
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        if result:
            self.__download_file(server_path, localhost_path)
        else:
            path_add = ''
            if os.path.exists(localhost_path):
                if os.path.isdir(localhost_path):
                    path_add = server_path.replace('\\', '/').split('/')[-1]
                localhost_path = os.path.join(localhost_path, path_add)
            self.__download_directory(server_path, localhost_path)

    def close(self):
        """Close connect"""
        self.__transport.close()
        self.__ssh.close()

    def __upload_file(self, localhost_file, server_file):
        """upload file"""

        self.sftp.put(localhost_file, server_file)

    def __download_file(self, server_file, localhost_file):
        """download file"""

        self.sftp.get(server_file, localhost_file)

    def __upload_directory(self, localhost_dir, server_dir):
        """Upload folder and files in folder"""

        def upload_func(path, server_path):
            dir_list = os.listdir(path)
            self.__ssh.exec_command('mkdir %s' % (server_path))
            time.sleep(0.5)
            for i in dir_list:
                new_path = os.path.join(path, i)
                new_server_path = server_path + '/' + i
                if not os.path.isdir(new_path):
                    self.__upload_file(new_path, new_server_path)
                else:
                    upload_func(new_path, new_server_path)

        upload_func(localhost_dir, server_dir)

    def __download_directory(self, server_dir, localhost_dir):
        """Download folder and files in folder"""

        def download_func(server_path, path):
            stdin, stdout, stderr = self.__ssh.exec_command('ls %s' % (server_path))
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            dir_list = result.decode().split('\n')[:-1]
            if not os.path.exists(path):
                os.mkdir(path)
            for i in dir_list:
                new_path = os.path.join(path, i)
                if server_path.endswith('/'):
                    server_path = server_path[:-1]
                new_server_path = server_path + '/' + i
                stdin, stdout, stderr = self.__ssh.exec_command('cd %s' % (new_server_path))
                res, err = stdout.read(), stderr.read()
                result = res if res else err
                if result:
                    self.__download_file(new_server_path, new_path)
                else:
                    download_func(new_server_path, new_path)

        download_func(server_dir, localhost_dir)
