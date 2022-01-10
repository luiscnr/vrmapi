from apimain import APIVRM
from localacces import LocalGerbo
import json
import datetime

import argparse

parser = argparse.ArgumentParser(description="Retrieve data from Cerbo CX")
parser.add_argument("-d", "--debug", help="Debugging mode.", action="store_true")
parser.add_argument("-v", "--verbose", help="Verbose mode.", action="store_true")
parser.add_argument("-a", "--access", help="Access.", choices=['api', 'local'])
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
    print('Last_Connection: ', datetime.datetime.fromtimestamp(info['last_timestamp']))
    # print(extrainfo)
    print('Voltage->', voltage)
    print('Current->', current)


def main_local():
    localG = LocalGerbo()
    voltage = localG.read_voltage()
    if not voltage is None:
        print("Battery voltage: {0:.2f}V".format(voltage / 10.0))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if args.access == 'api':
        main_api()
    elif args.access == 'local':
        main_local()
