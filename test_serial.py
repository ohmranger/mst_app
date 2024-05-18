import serial
from serial_mst import Serial_mst, SerialConnectionError
import time
import csv
import os
class mst:
    def __init__(self) -> None:
        self.s = Serial_mst(port='/dev/ttyUSB0')
        #self.data = []
        self.counter = 0
        self.open = 0
        self.filename = "data/output.csv"
        while os.path.exists(self.filename):
            self.counter += 1
            self.filename = f"data/output{self.counter}.csv"
        
        
        for a in range(100):
            self.data = self.s.read_meter()
            time.sleep(0.1)
        #print(type(data))
            print(a)
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not self.open:
                    writer.writerow(['NO', 'Par1st', 'Para2nd'])
                    self.open = 1
                writer.writerow([a, "{:.2f}".format(self.data[0]),"{:.2f}".format(self.data[1])])
            
        print(f"CSV file '{self.filename}' generated successfully!")
        length = len(self.data)
        pass
    def test(self):
        pass
   


if __name__ == '__main__':
    a = mst()
    a.test()