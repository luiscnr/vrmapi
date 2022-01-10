from pymodbus.constants import Defaults
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder


class LocalGerbo:

    def __init__(self):
        Defaults.Timeout = 25
        Defaults.Retries = 5
        self.client = ModbusClient('10.42.0.136', port='502')
        self.connection = self.client.connect()
        print(f'[Connection status: {self.connection}]')
        # try:
        #
        #     self.client.
        # except pymodbus.exceptions.ConnectionException:
        #     print('Connection error')
        #     self.connection = False

    def read_voltage(self):
        voltage = None
        if self.connection:
            result = self.client.read_input_registers(840, 2)
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
            voltage = decoder.decode_16bit_uint()
        return voltage

