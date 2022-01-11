import os.path

from apimain import APIVRM
from localacces import LocalGerbo
import json
from datetime import datetime as dt

import argparse

parser = argparse.ArgumentParser(description="Retrieve data from Cerbo CX")
parser.add_argument("-d", "--debug", help="Debugging mode.", action="store_true")
parser.add_argument("-v", "--verbose", help="Verbose mode.", action="store_true")
parser.add_argument("-a", "--access", help="Access.", choices=['api', 'local'])
parser.add_argument("-p", "--output-path", help="Output path")
args = parser.parse_args()


def main_api():
    print('[API ACCESS]')
    amain = APIVRM()
    info = amain.get_info_installation('Garda')

    for key in info:
        if key == 'extended':
            extrainfo = info[key]
            for extra in extrainfo:
                if extra['idDataAttribute'] == 143:
                    voltage = extra['formattedValue']
                if extra['idDataAttribute'] == 147:
                    current = extra['formattedValue']

                # print(extra['idDataAttribute'], extra['description'], '->', extra['formattedValue'])
        # else:
        #     print(key, '->', info[key])

    # devices = amain.get_devices_installation(None, info['idSite'])
    # for device in devices:
    #     print(device)

    # diagnose = amain.get_diagnose_installation(None, info['idSite'])
    # for d in diagnose:
    #     if d['description'] in ['Voltage', 'Current', 'Battery Power']:
    #         print(d['description'], datetime.datetime.fromtimestamp(d['timestamp']), '->', d['formattedValue'])
    # print(len(diagnose))
    print('Time: ', info['current_time'])
    print('Last_Connection: ', dt.fromtimestamp(info['last_timestamp']))
    # print(extrainfo)
    print('Voltage->', voltage)
    print('Current->', current)


def main_local():
    localG = LocalGerbo()
    dtnow = dt.utcnow().replace(second=0, microsecond=0)
    print('Reading values')
    all_values, col_names, col_values = localG.read_values()
    if args.output - path:
        file_last, file_log = get_local_file_names(dtnow)
        print('Creating local file...')
        localG.create_last_file(file_last, dtnow, all_values)
        col_values.insert(0,dtnow.strftime('%Y-%m-%d %H:%M'))
        if not os.path.exists(file_log):
            print('Start file log...')
            col_names.insert(0,'Time Stamp [UTC]')
            localG.start_file_log(file_log, dtnow, col_names, col_values)
        else:
            print('Append file log...')
            localG.append_file_log(file_log, dtnow, col_values)


def get_local_file_names(dtnow):
    file_last = os.path.join(args.output - path, 'VRMInfoLast.txt')
    dtstr = dtnow.strftime('%Y%m%d')
    name_file = f'VRMLog_{dtstr}.csv'
    file_log = os.path.join(args.output - path, name_file)
    return file_last, file_log


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if args.access == 'api':
        main_api()
    elif args.access == 'local':
        main_local()
