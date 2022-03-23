#!/usr/bin/env python3

"""
@author: Guangyi
@since: 2021-07-08
"""

import argparse
import json
import os
import sys
from typing import List

from paramiko.client import SSHClient, AutoAddPolicy

CONF_FILE = '.upup.conf'


class Uploader(object):

    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            local_dir: str,
            remote_dir: str,
            ignore_link=True
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.local_dir = os.path.abspath(local_dir)
        assert os.path.exists(self.local_dir), f'{self.local_dir} not found.'
        self.remote_dir = remote_dir
        self.ignore_link = ignore_link

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy)
        self.ssh.connect(self.host, self.port, self.user, look_for_keys=True)
        self.sftp = self.ssh.open_sftp()

        self._exec(f'mkdir -p {self._escape(self.remote_dir)}')
        self.remote_dir = self._exec(f'cd {self._escape(self.remote_dir)}; pwd').strip()

    def __del__(self):
        if hasattr(self, 'sftp'):
            self.sftp.close()
        if hasattr(self, 'ssh'):
            self.ssh.close()

    def _exec(self, cmd):
        stdio = self.ssh.exec_command(cmd)
        err = stdio[2].read()
        if err:
            raise RuntimeError(err)
        return stdio[1].read().decode()

    def upload(self, path: str):
        path = os.path.abspath(path)
        assert os.path.exists(path), f'{path} not found.'
        if not path.startswith(self.local_dir):
            print(f' ERROR\t{path} is not in the project directory.', file=sys.stderr)
            return

        if os.path.islink(path) and self.ignore_link:
            print(f'IGNORE\t{path}')
            return

        if os.path.isdir(path):
            self._upload_dir(path)
        else:
            self._upload_file(path)

    def _upload_file(self, path: str):
        local_dir_path = os.path.dirname(path)
        rel_dir_path = os.path.relpath(local_dir_path, self.local_dir)
        remote_dir_path = os.path.join(self.remote_dir, rel_dir_path) if rel_dir_path != '.' else self.remote_dir
        self._exec(f'mkdir -p {self._escape(remote_dir_path)}')

        remote_file_path = os.path.join(remote_dir_path, os.path.basename(path))
        print(f'UPLOAD\t{path}\t->\t{remote_file_path}')
        self.sftp.put(path, remote_file_path)

    def _upload_dir(self, path: str):
        for local_dir_path, _, filenames in os.walk(path):
            rel_dir_path = os.path.relpath(local_dir_path, self.local_dir)
            remote_dir_path = os.path.join(self.remote_dir, rel_dir_path) if rel_dir_path != '.' else self.remote_dir
            print(f'CREATE\t{remote_dir_path}')
            self._exec(f'mkdir -p {self._escape(remote_dir_path)}')

            for filename in filenames:
                local_file_path = os.path.join(local_dir_path, filename)
                if os.path.islink(local_file_path) and self.ignore_link:
                    print(f'IGNORE\t{local_file_path}')
                else:
                    remote_file_path = os.path.join(remote_dir_path, filename)
                    print(f'UPLOAD\t{local_file_path}\t->\t{remote_file_path}')
                    self.sftp.put(local_file_path, remote_file_path)

    @staticmethod
    def _escape(path):
        return path.replace(' ', '\\ ')


def upload(doc: dict, path_list: List[str]):
    ip = doc['ip']
    ip = ip.split(':')
    port = '22'
    if len(ip) == 1:
        ip = ip[0]
    elif len(ip) == 2:
        ip, port = ip[0], ip[1]
    else:
        raise RuntimeError(f'Invalid address {ip}.')
    user = doc['user']
    path = doc['path']

    print(f'CONNECT\t{user}@{ip}:{path}')
    uploader = Uploader(ip, port, user, './', path)
    for path in path_list:
        uploader.upload(path)
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', type=int, help='The server index.')
    parser.add_argument('input', nargs='+', help='The files or folders you want to upload.')
    args = parser.parse_args()

    if not os.path.exists(CONF_FILE):
        doc = {
            'ip': input('Server IP: '),
            'user': input('User: '),
            'path': input('Remote path: ')
        }
        with open(CONF_FILE, 'wt') as f:
            json.dump([doc], f, indent=4)

    with open(CONF_FILE, 'rt') as f:
        docs = json.load(f)

    if isinstance(docs, list):
        if args.server is None:
            if len(docs) == 1:
                upload(docs[0], args.input)
            else:
                for i, doc in enumerate(docs):
                    ip = doc['ip']
                    user = doc['user']
                    path = doc['path']
                    print(f'[{i}] {user}@{ip}:{path}')
                print(f'[ ] all servers')
                server = input('Select server: ')
                print()
                if server:
                    upload(docs[int(server)], args.input)
                else:
                    for doc in docs:
                        upload(doc, args.input)
        else:
            upload(docs[args.server], args.input)
    elif isinstance(docs, dict):
        upload(docs, args.input)
    else:
        raise RuntimeError('Invalid config file.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
