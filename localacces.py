from pymodbus.constants import Defaults
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder


class LocalGerbo:

    def __init__(self):
        Defaults.Timeout = 25
        Defaults.Retries = 5
        self.client = ModbusClient('10.42.0.136', port='81')
        self.connection = self.client.connect()
        print(f'[Connection status: {self.connection}]')

        self.registers_system = {
            '800': {'include': True, 'description': 'Serial (System)', 'type': 'string[6]'},
            '806': {'include': True, 'description': 'CCGX Relay 1 state', 'type': 'uint16'},
            '807': {'include': True, 'description': 'CCGX Relay 2 state', 'type': 'uint16'},
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
            '826': {'include': True, 'description': 'Active input source', 'type': 'int16'},
            '840': {'include': True, 'description': 'Battery Voltage (System)', 'type': 'uint16', 'units': 'V DC',
                    'scale': '10'},
            '841': {'include': True, 'description': 'Battery Current (System)', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '842': {'include': True, 'description': 'Battery Power (System)', 'type': 'int16', 'units': 'W'},
            '843': {'include': True, 'description': 'Battery State of Charge (System)', 'type': 'uint16', 'units': '%'},
            '844': {'include': True, 'description': 'Battery state (System)', 'type': 'uint16'},
            '845': {'include': True, 'description': 'Battery Consumed Amphours (System)', 'type': 'uint16',
                    'units': 'Ah',
                    'scale': '-10'},
            '846': {'include': True, 'description': 'Battery Time to Go (System)', 'type': 'uint16', 'units': 's',
                    'scale': '0.01'},
            '850': {'include': True, 'description': 'PV-DC-couple power', 'type': 'uint16', 'units': 'W'},
            '851': {'include': True, 'description': 'PV-DC-couple current', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '855': {'include': True, 'description': 'Charge power', 'type': 'uint16', 'units': 'W'},
            '860': {'include': True, 'description': 'DC System Power', 'type': 'int16', 'units': 'W'},
            '865': {'include': True, 'description': 'VE.Bus charge current (System)', 'type': 'int16', 'units': 'A DC',
                    'scale': '10'},
            '866': {'include': True, 'description': 'VE.Bus charge power (System)', 'type': 'int16'}, 'units': 'W',
        }

    def read_value(self, result, type, scale):
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
        if type.startswith('string'):
            n = int(type[type.index('[') + 1:type.index(']')])
            val = decoder.decode_string(n)
        elif type == 'uint16':
            val = decoder.decode_16bit_uint()
            val = val * scale
        elif type == 'int16':
            val = decoder.decode_16bit_int()
            val = val * scale
        return val

    def read_values(self):
        if self.connection:
            for reg in self.registers_system:
                result = self.client.read_input_registers(int(reg), 1)
                type = self.registers_system[reg]['type']
                scale = 1
                if self.registers_system[reg]['scale']:
                    scale = float(self.registers_system[reg]['scale'])
                val = self.read_value(result, type, scale)
                print(self.registers_system[reg]['description'],'->',val)
                # decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
                # voltage = decoder.decode_16bit_uint()
                #
