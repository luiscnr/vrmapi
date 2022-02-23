from pymodbus.constants import Defaults
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.exceptions import ModbusIOException
import csv


class LocalGerbo:

    def __init__(self, connect):
        Defaults.Timeout = 25
        Defaults.Retries = 5
        self.delimiter = ';'
        self.delimiter_last = '='

        self.client = ModbusClient('10.42.0.136', port='502')
        if connect:
            self.connection = self.client.connect()
            # print(f'[Connection status: {self.connection}]')
        else:
            self.connection = False

        self.registers_system = {
            '800': {'include': True, 'description': 'Serial (System)', 'type': 'string[6]', 'units': ''},
            '806': {'include': True, 'description': 'CCGX Relay 1 state', 'type': 'uint16', 'units': 'Options'},
            '807': {'include': True, 'description': 'CCGX Relay 2 state', 'type': 'uint16', 'units': 'Options'},
            '808': {'include': True, 'description': 'PV-AC-coupled on output L1', 'type': 'uint16', 'units': 'W'},
            '809': {'include': True, 'description': 'PV-AC-coupled on output L2', 'type': 'uint16', 'units': 'W'},
            '810': {'include': True, 'description': 'PV-AC-coupled on output L3', 'type': 'uint16', 'units': 'W'},
            '811': {'include': True, 'description': 'PV-AC-coupled on input L1', 'type': 'uint16', 'units': 'W'},
            '812': {'include': True, 'description': 'PV-AC-coupled on input L2', 'type': 'uint16', 'units': 'W'},
            '813': {'include': True, 'description': 'PV-AC-coupled on input L3', 'type': 'uint16', 'units': 'W'},
            '814': {'include': True, 'description': 'PV-AC-coupled on generator L1', 'type': 'uint16', 'units': 'W'},
            '815': {'include': True, 'description': 'PV-AC-coupled on generator L2', 'type': 'uint16', 'units': 'W'},
            '816': {'include': True, 'description': 'PV-AC-coupled on generator L3', 'type': 'uint16', 'units': 'W'},
            '817': {'include': True, 'description': 'AC Consumption L1', 'type': 'uint16', 'units': 'W'},
            '818': {'include': True, 'description': 'AC Consumption L2', 'type': 'uint16', 'units': 'W'},
            '819': {'include': True, 'description': 'AC Consumption L3', 'type': 'uint16', 'units': 'W'},
            '820': {'include': True, 'description': 'Grid L1', 'type': 'int16', 'units': 'W'},
            '821': {'include': True, 'description': 'Grid L2', 'type': 'int16', 'units': 'W'},
            '822': {'include': True, 'description': 'Grid L3', 'type': 'int16', 'units': 'W'},
            '823': {'include': True, 'description': 'Genset L1', 'type': 'int16', 'units': 'W'},
            '824': {'include': True, 'description': 'Genset L2', 'type': 'int16', 'units': 'W'},
            '825': {'include': True, 'description': 'Genset L3', 'type': 'int16', 'units': 'W'},
            '826': {'include': True, 'description': 'Active input source', 'type': 'int16', 'units': 'Options'},
            '840': {'include': True, 'description': 'Battery Voltage (System)', 'type': 'uint16', 'units': 'V DC',
                    'scale': '10'},
            '841': {'include': True, 'description': 'Battery Current (System)', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '842': {'include': True, 'description': 'Battery Power (System)', 'type': 'int16', 'units': 'W'},
            '843': {'include': True, 'description': 'Battery State of Charge (System)', 'type': 'uint16', 'units': '%'},
            '844': {'include': True, 'description': 'Battery state (System)', 'type': 'uint16', 'units': 'Options'},
            '845': {'include': True, 'description': 'Battery Consumed Amphours (System)', 'type': 'uint16',
                    'units': 'Ah', 'scale': '-10'},
            '846': {'include': True, 'description': 'Battery Time to Go (System)', 'type': 'uint16', 'units': 's',
                    'scale': '0.01'},
            '850': {'include': True, 'description': 'PV-DC-couple power', 'type': 'uint16', 'units': 'W'},
            '851': {'include': True, 'description': 'PV-DC-couple current', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '855': {'include': True, 'description': 'Charge power', 'type': 'uint16', 'units': 'W'},
            '860': {'include': True, 'description': 'DC System Power', 'type': 'int16', 'units': 'W'},
            '865': {'include': True, 'description': 'VE.Bus charge current (System)', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '866': {'include': True, 'description': 'VE.Bus charge power (System)', 'type': 'int16', 'units': 'W'}
        }

        self.registers_solarcharger = {
            '771': {'include': True, 'description': 'Battery Voltage', 'type': 'uint16', 'units': 'V DC',
                    'scale': '100'},
            '772': {'include': True, 'description': 'Battery Current', 'type': 'int16', 'units': 'A DC', 'scale': '10'},
            '773': {'include': True, 'description': 'Battery Temperature', 'type': 'int16', 'units': 'Degrees celsius',
                    'scale': '10'},
            '774': {'include': True, 'description': 'Charger on/off', 'type': 'uint16', 'units': 'Options'},
            '775': {'include': True, 'description': 'Charger state', 'type': 'uint16', 'units': 'Options'},
            '776': {'include': True, 'description': 'PV Voltage', 'type': 'uint16', 'units': 'V DC', 'scale': '100'},
            '777': {'include': True, 'description': 'PV Current', 'type': 'int16', 'units': 'A DC', 'scale': '10'},
            '778': {'include': True, 'description': 'Equalization pending', 'type': 'uint16', 'units': 'Options'},
            '779': {'include': True, 'description': 'Equalization time remaining', 'type': 'uint16', 'units': 'seconds',
                    'scale': '10'},
            '780': {'include': True, 'description': 'Relay on the charger', 'type': 'uint16', 'units': 'Options'},
            '782': {'include': True, 'description': 'Low batt. voltage alarm', 'type': 'uint16', 'units': 'Options'},
            '783': {'include': True, 'description': 'High batt. voltage alarm', 'type': 'uint16', 'units': 'Options'},
            '784': {'include': True, 'description': 'Yield today', 'type': 'uint16', 'units': 'kWh', 'scale': '10'},
            '785': {'include': True, 'description': 'Maximum charge power today', 'type': 'uint16', 'units': 'W'},
            '786': {'include': True, 'description': 'Yield yesterday', 'type': 'uint16', 'units': 'kWh', 'scale': '10'},
            '787': {'include': True, 'description': 'Maximum charge power yesterday', 'type': 'uint16', 'units': 'W'},
            '788': {'include': True, 'description': 'Error code', 'type': 'uint16', 'units': 'Errors'},
            '789': {'include': True, 'description': 'PV power', 'type': 'uint16', 'units': 'W', 'scale': '10'},
            '790': {'include': True, 'description': 'User yield', 'type': 'uint16', 'units': 'kWh', 'scale': '10'},
            '791': {'include': True, 'description': 'MPP Operation model', 'type': 'uint16', 'units': 'Options'},
            '3700': {'include': True, 'description': 'PV voltage for tracker 0', 'type': 'uint16', 'units': 'V DC',
                     'scale': '100'},
            '3701': {'include': True, 'description': 'PV voltage for tracker 1', 'type': 'uint16', 'units': 'V DC',
                     'scale': '100'},
            '3702': {'include': True, 'description': 'PV voltage for tracker 2', 'type': 'uint16', 'units': 'V DC',
                     'scale': '100'},
            '3703': {'include': True, 'description': 'PV voltage for tracker 3', 'type': 'uint16', 'units': 'V DC',
                     'scale': '100'},
            '3704': {'include': True, 'description': 'PV current for tracker 0', 'type': 'int16', 'units': 'A DC',
                     'scale': '10'},
            '3705': {'include': True, 'description': 'PV current for tracker 1', 'type': 'int16', 'units': 'A DC',
                     'scale': '10'},
            '3706': {'include': True, 'description': 'PV current for tracker 2', 'type': 'int16', 'units': 'A DC',
                     'scale': '10'},
            '3707': {'include': True, 'description': 'PV current for tracker 3', 'type': 'int16', 'units': 'A DC',
                     'scale': '10'},
            '3708': {'include': True, 'description': 'Yield today for tracker 0', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3709': {'include': True, 'description': 'Yield today for tracker 1', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3710': {'include': True, 'description': 'Yield today for tracker 2', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3711': {'include': True, 'description': 'Yield today for tracker 3', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3712': {'include': True, 'description': 'Yield yesterday for tracker 0', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3713': {'include': True, 'description': 'Yield yesterday for tracker 1', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3714': {'include': True, 'description': 'Yield yesterday for tracker 2', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3715': {'include': True, 'description': 'Yield yesterday for tracker 3', 'type': 'uint16', 'units': 'kWh',
                     'scale': '10'},
            '3716': {'include': True, 'description': 'Maximum charge power today for tracker 0', 'type': 'uint16',
                     'units': 'W'},
            '3719': {'include': True, 'description': 'Maximum charge power today for tracker 1', 'type': 'uint16',
                     'units': 'W'},
            '3718': {'include': True, 'description': 'Maximum charge power today for tracker 2', 'type': 'uint16',
                     'units': 'W'},
            '3719': {'include': True, 'description': 'Maximum charge power today for tracker 3', 'type': 'uint16',
                     'units': 'W'},
            '3720': {'include': True, 'description': 'Maximum charge power yesterday for tracker 0', 'type': 'uint16',
                     'units': 'W'},
            '3721': {'include': True, 'description': 'Maximum charge power yesterday for tracker 1', 'type': 'uint16',
                     'units': 'W'},
            '3722': {'include': True, 'description': 'Maximum charge power yesterday for tracker 2', 'type': 'uint16',
                     'units': 'W'},
            '3723': {'include': True, 'description': 'Maximum charge power yesterday for tracker 3', 'type': 'uint16',
                     'units': 'W'}
        }

        self.solarcharger_unit = 226

        self.options = {
            '806': {'0': 'open', '1': 'close'},
            '807': {'0': 'open', '1': 'close'},
            '826': {'0': 'Not available', '1': 'Grid', '2': 'Generator', '3': 'Shore power', '240': 'Not connected'},
            '844': {'0': 'idle', '1': 'charging', '2': 'discharging'},
            '774': {'1': 'On', '4': 'Off'},
            '775': {'0': 'Off', '2': 'Fault', '3': 'Bulk', '4': 'Absorption', '5': 'Float', '6': 'Storage',
                    '7': 'Equalize', '11': 'Other(Hub - 1)', '252': 'External control'},
            '778': {'0': 'No', '1': 'Yes', '2': 'Error', '3': 'Unavailable - Unknown'},
            '780': {'0': 'Open', '1': 'Closed'},
            '782': {'0': 'No alarm', '2': 'Alarm'},
            '783': {'0': 'No alarm', '2': 'Alarm'},
            '791': {'0': 'Off', '1': 'Voltage/current limited', '2': 'MPPT active', '255': 'Not available'}
        }

        self.errors = {
            '0': 'No error',
            '1': 'Battery temperature too high',
            '2': 'Battery voltage too high',
            '3': 'Battery temperature sensor miswired (+)',
            '4': 'Battery temperature sensor miswired (-)',
            '5': 'Battery temperature sensor disconnected',
            '6': 'Battery voltage sense miswired (+)',
            '7': 'Battery voltage sense miswired (-)',
            '8': 'Battery voltage sense disconnected',
            '9': 'Battery voltage wire losses too high',
            '17': 'Charger temperature too high',
            '18': 'Charger over-current',
            '19': 'Charger current polarity reversed',
            '20': 'Bulk time limit reached',
            '22': 'Charger temperature sensor miswired',
            '23': 'Charger temperature sensor disconnected',
            '34': 'Input current too high'
        }

        self.col_names_default = ['840', '841', '842', '843', '844', '845', '846', '850', '851', '855', '860']
        for i in range(771, 792):
            if i == 781:
                continue
            self.col_names_default.append(str(i))

        self.params_th = {
            'Battery Voltage (System)': {
                'reg': '840',
                'unit': None
            },
            'Battery Current (System)': {
                'reg': '841',
                'unit': None
            },
            'Battery Power (System)': {
                'reg': '842',
                'unit': None
            },
            'Battery Voltage': {
                'reg': '771',
                'unit': self.solarcharger_unit
            },
            'Battery Current': {
                'reg': '772',
                'unit': self.solarcharger_unit
            },
            'PV Voltage': {
                'reg': '776',
                'unit': self.solarcharger_unit
            },
            'PV Current': {
                'reg': '777',
                'unit': self.solarcharger_unit
            },
            'Charger state': {
                'reg': '775',
                'unit': self.solarcharger_unit
            }
        }

    def read_value(self, reg, result, type, scale, unit):
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
        if not isinstance(decoder, BinaryPayloadDecoder):
            return None
        if type.startswith('string'):
            n = int(type[type.index('[') + 1:type.index(']')])
            val = decoder.decode_string(n)
        elif type == 'uint16':
            val = decoder.decode_16bit_uint()
            val = val / scale
        elif type == 'int16':
            val = decoder.decode_16bit_int()
            val = val / scale

        if unit == 'Options':
            vals = f'{val:0.0f}'
            val = self.options[reg][vals]

        if unit == 'Errors':
            vals = f'{val:0.0f}'
            val = self.errors[vals]

        return val

    def read_values(self,seq_info):
        if not self.connection:
            return None, None, None

        all_values = {}
        col_names = []
        col_values = []

        col_names.append('SEQ_INFO')
        col_values.append(seq_info)

        for reg in self.registers_system:
            if not self.registers_system[reg]['include']:
                continue
            result = self.client.read_input_registers(int(reg), 1)
            if isinstance(result, ModbusIOException):
                continue
            type = self.registers_system[reg]['type']
            unit = self.registers_system[reg]['units']
            scale = 1
            if 'scale' in self.registers_system[reg].keys():
                scale = float(self.registers_system[reg]['scale'])
            val = self.read_value(reg, result, type, scale, unit)
            desc = self.registers_system[reg]['description']
            col_name = f'{desc}[{unit}]'
            all_values[reg] = {
                'ref': col_name,
                'value': val
            }
            if reg in self.col_names_default:
                col_names.append(col_name)
                col_values.append(val)

            # print(self.registers_system[reg]['description'], '->', val)

        for reg in self.registers_solarcharger:
            if not self.registers_solarcharger[reg]['include']:
                continue
            result = self.client.read_input_registers(int(reg), count=1, unit=self.solarcharger_unit)
            if isinstance(result, ModbusIOException):
                continue
            type = self.registers_solarcharger[reg]['type']
            unit = self.registers_solarcharger[reg]['units']
            scale = 1
            if 'scale' in self.registers_solarcharger[reg].keys():
                scale = float(self.registers_solarcharger[reg]['scale'])
            val = self.read_value(reg, result, type, scale, unit)

            desc = self.registers_solarcharger[reg]['description']
            col_name = f'{desc}[{unit}]'
            all_values[reg] = {
                'ref': col_name,
                'value': val
            }
            if reg in self.col_names_default:
                col_names.append(col_name)
                col_values.append(val)

            print(self.registers_solarcharger[reg]['description'], '->', val)

        return all_values, col_names, col_values

    def start_file_log(self, file_log, col_names, col_values):
        with open(file_log, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            # write the header
            writer.writerow(col_names)
            # write the data
            writer.writerow(col_values)

    def append_file_log(self, file_log, col_values):
        with open(file_log, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            # write the data
            writer.writerow(col_values)

    def create_last_file(self, file_last, dtnow, all_values):
        with open(file_last, 'w') as f:
            writer = csv.writer(f, delimiter=self.delimiter_last)
            row = ['Time stamp [UTC]', dtnow.strftime('%Y-%m-%d %H:%M')]
            writer.writerow(row)
            for reg in all_values:
                ref = all_values[reg]['ref']
                val = all_values[reg]['value']
                row = [f'[{reg}]{ref}', val]
                writer.writerow(row)

    def get_info_reg(self, reg, unitv, retrieveInputRegister):
        if isinstance(reg, str):
            regs = reg
        elif isinstance(reg, int):
            regs = str(reg)
        else:
            return None
        info = None
        if regs in self.registers_system.keys():
            info = self.registers_system[regs]
        if regs in self.registers_solarcharger.keys():
            info = self.registers_solarcharger[regs]
        inputRegister = None
        if retrieveInputRegister:
            inputRegister = self.get_input_register(reg,unitv)

        return info, inputRegister

    def get_input_register(self, reg, unitv):
        if not self.connection:
            return None
        if isinstance(reg, str):
            regi = int(reg)
        elif isinstance(reg, int):
            regi = reg
        else:
            return None

        if unitv is None:
            result = self.client.read_input_registers(regi, 1)
        else:
            result = self.client.read_input_registers(regi, 1, unit=unitv)

        if isinstance(result, ModbusIOException):
            return None
        else:
            return result
