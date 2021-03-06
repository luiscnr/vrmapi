import os.path

from apimain import APIVRM
from localacces import LocalGerbo
import json
from datetime import datetime as dt

import argparse
import configparser

parser = argparse.ArgumentParser(description="Retrieve data from Cerbo CX")
parser.add_argument("-v", "--verbose", help="Verbose mode.", action="store_true")
parser.add_argument("-a", "--access", help="Access.", choices=['api', 'local', 'checkth','copyseq'])
parser.add_argument("-p", "--path", help="Output path.")
parser.add_argument("-c", "--config_th", help="Configuration file for checking thresholds.")
parser.add_argument("-seq", "--sequence_tag", help="Optional sequence tag for log file")
args = parser.parse_args()


def main_api():
    if args.verbose:
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
    if args.verbose:
        print('Time: ', info['current_time'])
        print('Last_Connection: ', dt.fromtimestamp(info['last_timestamp']))
        # print(extrainfo)
        print('Voltage->', voltage)
        print('Current->', current)


def main_local():
    localG = LocalGerbo(True)
    dtnow = dt.utcnow().replace(second=0, microsecond=0)
    if args.verbose:
        print('Reading values')
    seq_info = 'UNKNOWN'
    if args.sequence_tag:
        seq_info = args.sequence_tag
    all_values, col_names, col_values = localG.read_values(seq_info)
    if all_values is None or col_names is None or col_values is None:
        print('[ERROR] Connection is not established...')
        return
    if args.path:
        file_last, file_log = get_local_file_names(dtnow)
        if args.verbose:
            print('Creating local file...')
        localG.create_last_file(file_last, dtnow, all_values)

        col_values.insert(0, dtnow.strftime('%Y-%m-%d %H:%M'))
        if not os.path.exists(file_log):
            if args.verbose:
                print('Start file log...')
            col_names.insert(0, 'Time Stamp [UTC]')
            localG.start_file_log(file_log, col_names, col_values)
        else:
            if args.verbose:
                print('Append file log...')
            localG.append_file_log(file_log, col_values)
        if args.verbose:
            print('Completed')


def get_local_file_names(dtnow):
    file_last = os.path.join(args.path, 'VRMInfoLast.txt')
    dtstr = dtnow.strftime('%Y%m%d')
    name_file = f'VRMLog_{dtstr}.csv'
    file_log = os.path.join(args.path, name_file)
    return file_last, file_log


def check_thersholds():
    if args.verbose:
        print('[STARTED]')
    if not args.config_th:
        print('[ERROR] Configuration file should be provided for option check_th')
        exit(4)
        return
    if args.verbose:
        print('[INFO]Reading configuration file...')
    options = configparser.ConfigParser()
    options.read(args.config_th)
    if args.verbose:
        print('[INFO]Connecting with Cerbo GX...')
    localG = LocalGerbo(True)
    if not localG.connection:
        print('[ERROR] Connection with Cerbo GX is unavailable')
        exit(3)
        return

    sections = ['UpThreshold', 'DownThreshold']
    output_res = 1
    for section in sections:
        if options.has_section(section):
            for param in localG.params_th:
                if options.has_option(section, param) and param in localG.params_th:
                    ths = options[section][param]
                    try:
                        th = float(ths.strip())
                    except ValueError:
                        print(f'[WARNING] Threshold: {ths} for param: {param} is not valid. Skipping....')
                        continue
                    paramHere = localG.params_th[param]
                    # print(param, reg, th)
                    # if args.verbose:
                    #     print(f'[INFO] Reading value for param: {param}')
                    info, inputRegister = localG.get_info_reg(paramHere['reg'], paramHere['unit'], True)
                    if info is not None and inputRegister is not None:
                        scale = 1
                        if 'scale' in info.keys():
                            scale = float(info['scale'])
                        val = localG.read_value(paramHere['reg'], inputRegister, info['type'], scale, info['units'])
                        if val is None:
                            print(f'[ERROR] Value for param {param} could not be read...')
                            output_res = -1
                        else:
                            if args.verbose:
                                print(f'[INFO] Param: {param} Value: {val} Threshold: {th} Type: {section}')
                            if section == 'UpThreshold' and val < th and output_res == 1:
                                output_res = 0
                            if section == 'DownThreshold' and val > th and output_res == 1:
                                output_res = 0
                    else:
                        print(f'[ERROR] Value for param {param} could not be read...')
                        output_res = -1

                    # print(info, inputRegister)

    if output_res == -1:
        exit(2)
    elif output_res == 0:
        if args.verbose:
            print(f'[INFO] Cerbo CX readings show poor light conditions. Hypstar sequence cancelled')
        exit(1)
    elif output_res == 1:
        if args.verbose:
            print(f'[INFO] Cerbo CX readings show good light conditions. Starting Hypstar sequence...')
        exit(0)

    return

def copy_sequence():
    cmd = 'scp hypernets@$(ssh - p 9022 hypstar@enhydra.naturalsciences.be "cat /home/hypstar/GAIT/GAIT_ip_address"):/home/hypernets_tools/DATA'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if args.access == 'api':
        main_api()
    elif args.access == 'local':
        main_local()
    elif args.access == 'checkth':
        check_thersholds()
    elif args.access == 'copycheck':
        copy_sequence()
