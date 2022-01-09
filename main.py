from apimain import APIVRM
import json
import datetime

from pymodbus.constants import Defaults
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder


def main():
    print('STARTED')
    amain = APIVRM()
    info = amain.get_info_installation('Garda')

    for key in info:
        if key == 'extended':
            extrainfo = info[key]
            for extra in extrainfo:
                print(extra['idDataAttribute'], extra['description'], '->', extra['formattedValue'])
        else:
            print(key, '->', info[key])

    devices = amain.get_devices_installation(None, info['idSite'])
    for device in devices:
        print(device)

    diagnose = amain.get_diagnose_installation(None, info['idSite'])
    for d in diagnose:
        if d['description'] in ['Voltage', 'Current', 'Battery Power']:
            print(d['description'], datetime.datetime.fromtimestamp(d['timestamp']), '->', d['formattedValue'])
    print(len(diagnose))


def test_dbus():
    Defaults.Timeout = 25
    Defaults.Retries = 5
    client = ModbusClient('ipaddress.of.venus', port='502')
    result = client.read_input_registers(840, 2)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
    voltage = decoder.decode_16bit_uint()
    print("Battery voltage: {0:.2f}V".format(voltage / 10.0))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
