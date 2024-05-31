import serial
import sys
import time
import re

class SerialConnectionError(Exception):
    pass

class Serial_mst:
    def __init__(self, port= '/dev/mst/meter', baud_rate = 9600, para1st = 'FUNCtion: IMPA C', para2nd = 'FUNCtion: IMPB D',freq ='FREQuency 1000', sampling_rate='APERture SLOW', volt_lv='VOLTage 1.0'):
        
        self.set_data = [['C','FUNCtion: IMPA C'],['L','FUNCtion: IMPA L'],['R','FUNCtion: IMPA R']
                         ,['D','FUNCtion: IMPB D'],['Q','FUNCtion: IMPB Q'],['\u03F4','FUNCtion: IMPB RAD'],['ESR','FUNCtion: IMPB ESR']
                         ,['100Hz','FREQuency 100'],['1kHz','FREQuency 1000'],['10kHz','FREQuency 10000'],['100kHz','FREQuency 100000']]
        self.set_data_dic = dict(self.set_data)
        try:
            self.serial_port = serial.Serial(port, baud_rate)  # Change 'ttyUSB0' to your Arduino's serial port
            command = [para1st,para2nd,freq,sampling_rate,volt_lv]
            for var in command:
                self.serial_port.write((var + '\n').encode())
                time.sleep(0.1)
                

        except serial.SerialException as e:
            raise SerialConnectionError(f"Failed to connect to port {port}: {e}")

    def read_meter(self):
        command = 'FETCh?'
        self.serial_port.write((command + '\n').encode())
        recive_data = self.serial_port.readline().decode().strip()
        values = recive_data.split(",")
        rounded_values = []
        for value in values:
            try:
                rounded_values.append(float(value))
            except ValueError:
                pass #rounded_values.append(value)
        return rounded_values[0], rounded_values[1]

    def set_meter(self, data):
        if data in self.set_data_dic : 
            self.serial_port.write((self.set_data_dic[data] + '\n').encode())
        time.sleep(0.1)
        

    
    def close(self):
        self.serial_port.close()

    def parse_scientific_notation(self,scientific_str, digits=6):
        match = re.match(r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", scientific_str)
        if match:
            number = float(match.group(1))
            significand, exponent = "{:.{digits}e}".format(number, digits=digits).split("e")
            return significand #, int(exponent)
        else:
            return None, None
