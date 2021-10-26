#!/usr/bin/env python3

"""
@author: Guangyi
@since: 2021-07-08
"""

import argparse
import json
import os
import subprocess

CONF_FILE = '.upup.conf'


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
                server = 0
            else:
                for i, doc in enumerate(docs):
                    ip = doc['ip']
                    user = doc['user']
                    path = doc['path']
                    print(f'[{i}] {user}@{ip}:{path}')
                server = int(input('Select server: '))
        else:
            server = args.server
        doc = docs[server]
    elif isinstance(docs, dict):
        doc = docs
    else:
        raise RuntimeError('Invalid config file.')

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
    subprocess.call(['ssh', '-p', port, f'{user}@{ip}', f'mkdir -p {path}'])
    subprocess.call(['scp', '-P', port, '-r', *args.input, f'{user}@{ip}:{path}'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
