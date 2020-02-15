import argparse
import json
import os
import re
import sh
import time

from datetime import datetime, timedelta
from dateutil import parser as dateparser

interface = 'wlp2s0'
ssids = ['Tryolabs']
ssid_re = re.compile('ESSID:\"(.*)\"', re.MULTILINE)
folder = os.path.expanduser('~/work_time')

def run_daemon():
    if not os.path.isdir(folder):
        os.mkdir(folder)


    while True:
        output = sh.iwconfig(interface).stdout.decode('utf-8')
        match = ssid_re.search(output)
        if match is not None:
            ssid = match.groups()[0]
            if ssid in ssids:
                print('conected')
                now = datetime.now()
                file_path = os.path.join(folder, now.date().isoformat())
                if not os.path.isfile(file_path):
                    with open(file_path, 'w') as f:
                        json.dump({'start': now.isoformat(), 'last': now.isoformat()}, f)
                else:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    data['last'] = now.isoformat()
                    with open(file_path, 'w') as f:
                        json.dump(data, f)
        else:
            print('no match')
        time.sleep(10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='It tracks time.')

    parser.add_argument('--daemon', '-d', action='store_true')
    parser.add_argument('days', type=int, nargs='?', default=0)
    args = parser.parse_args()
    if args.daemon:
        run_daemon()
    else:
        now = datetime.now() - timedelta(days=args.days)
        file_path = os.path.join(folder, now.date().isoformat())
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(now.date().isoformat())
        print(dateparser.parse(data['last']) - dateparser.parse(data['start']))
