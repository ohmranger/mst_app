
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 

from scipy.signal import find_peaks
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QSpinBox ,QWidget, QFileDialog, QMessageBox
import os
import time

class CustomNavigationToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent=None, coordinates=True):
        super().__init__(canvas, parent, coordinates)

    def save_figure(self):
        usb_drives = []
        media_dir = "/media/mst"
        current_datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        # Initial file name with date and time
        default_file_name = f"/data_{current_datetime}.png"
        try :
            if os.path.exists(media_dir):
                 entries = os.listdir(media_dir)
                 for entry in entries:
                     entry_path = os.path.join(media_dir, entry)
                     if os.path.ismount(entry_path):
                         usb_drives.append(entry_path)
            print(usb_drives[0])
            str_path = str(usb_drives[0])+default_file_name
        except Exception as e:
                print("parth error")
                str_path = f"data_{current_datetime}.png"
            
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Figure", str_path , 
                                                   "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)")
        if file_path:
            self.canvas.figure.savefig(file_path)
            
class AnalyzeError(Exception):
    pass
class Analyze_mst(QDialog):
    def __init__(self,parent=None,file_path_csv = None, window_size = 12,periods=2,fillter_x1=700,fillter_x2=1200,limit_y=100):
        super().__init__(parent)
        self.window_size = window_size
        self.periods = periods
        self.fillter_x1 = fillter_x1
        self.fillter_x2 = fillter_x2
        self.limit_y = 100
        self.file_path_csv = file_path_csv
        
        self.initUI()
        self.a1 = 0
        self.b1 = 0
        self.a2 = 0
        self.b2 = 0
    def initUI(self):
        self.setWindowTitle("Analyze")
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(111)
        self.ax2 = self.ax1.twinx()  
        self.setGeometry(200, 200, 300, 150)
        self.layout = QVBoxLayout()
        self.label_1 = QLabel('Average window size : ')
        self.label_2 = QLabel('Rate of Change periods : ')
        self.label_3 = QLabel('Start Analyze of x : ')
        self.label_4 = QLabel('Stop Analyze of x : ')
        self.parameter_1 = QSpinBox()
        self.parameter_2 = QSpinBox()
        self.parameter_3 = QSpinBox()
        self.parameter_4 = QSpinBox()
        self.parameter_3.setSingleStep(50)
        self.parameter_4.setSingleStep(50)
        self.parameter_1.setValue(self.window_size)
        self.parameter_2.setValue(self.periods)
        self.parameter_3.setMaximum(2000)
        self.parameter_3.setValue(self.fillter_x1)
        self.parameter_4.setMaximum(2000)
        self.parameter_4.setValue(self.fillter_x2)

        self.layout.addWidget(self.label_1)
        self.layout.addWidget(self.parameter_1)
        self.layout.addWidget(self.label_2)
        self.layout.addWidget(self.parameter_2)
        self.layout.addWidget(self.label_3)
        self.layout.addWidget(self.parameter_3)
        self.layout.addWidget(self.label_4)
        self.layout.addWidget(self.parameter_4)

        self.submit_button = QPushButton("Analyze MST", self)
        self.submit_button.clicked.connect(self.closeAndReturn_mst)
        self.layout.addWidget(self.submit_button)
        
        self.setLayout(self.layout)

        pass

    def closeAndReturn_mst(self):
        self.window_size = self.parameter_1.value()
        self.periods = self.parameter_2.value()
        self.fillter_x1 = self.parameter_3.value()
        self.fillter_x2 = self.parameter_4.value()
        self.Analyze_mst(self.file_path_csv)
        self.show_graph_window()

        
        pass


    
    def Analyze_mst(self, path_file_csv):
        df = pd.read_csv(path_file_csv)
        self.find_mst(df, self.fillter_x1, self.fillter_x2)

        pass
    

    def find_mst(self, data_file, start_x, stop_x): 
        data_file['MValue_Mean'] = data_file['MValue'].rolling(window=self.window_size).mean()
        data_file['SValue_Mean'] = data_file['SValue'].rolling(window=self.window_size).mean()
        data_file['MValue_Analyze'] = abs(data_file['MValue_Mean'].diff(periods=self.periods)) # Rate of change for Data1
        data_file['SValue_Analyze'] = abs(data_file['SValue_Mean'].diff(periods=self.periods))# Rate of change for Data2
        #filter data MValue_Mean start x to stop x
        filtered_df = data_file[(data_file['NO'] >= start_x) & (data_file['NO'] <= (start_x+200))]
        #Detect MST Poin AB of Capacitive
        max_value1 = filtered_df.loc[filtered_df['MValue_Mean'].idxmax()]
        print(f'The point A : {max_value1["NO"]} sec at  Max value : {max_value1["MValue_Mean"]}')   
        filtered_df1 = data_file[(data_file['NO'] >= max_value1["NO"]) & (data_file['NO']<= stop_x)]
        min_value = filtered_df1.loc[filtered_df1['MValue_Analyze'].idxmin()]
        min_value_row = filtered_df1[filtered_df1['MValue_Analyze'] == min_value["MValue_Analyze"]]
        # count occurrences of min
        min_value_count = min_value_row.shape[0]
        min_value_times = min_value_row['NO'].tolist()
        #print(f'Min value : {min_value["MValue_Analyze"]} at the time {min_value["NO"]} sec')
        #print(f'Min_value is {min_value["MValue_Analyze"]} occurs : {min_value_count}')
        point_b = self.find_start_of_longest_consecutive_sequence(min_value_times)
        point_b_value = data_file[data_file['NO']== point_b]
        print(f'the Point B : {point_b} sec  at value is {point_b_value["MValue"].values[0]}')

        #Detect MST Point AB of Tan0
        min_value2 = filtered_df.loc[filtered_df['SValue_Mean'].idxmin()]
        print(f'The point A2 : {min_value2["NO"]} sec at  Max value : {min_value2["SValue_Mean"]}') 
        filtered_df2 = data_file[(data_file['NO'] >= min_value2["NO"]) & (data_file['NO']<= stop_x)]
        min_value_dif2 = filtered_df2.loc[filtered_df2['SValue_Analyze'].idxmin()]
        min_value_row2 = filtered_df2[filtered_df2['SValue_Analyze'] == min_value_dif2["SValue_Analyze"]]
        min_value_coun2 = min_value_row2.shape[0]
        min_value_times2 = min_value_row2['NO'].tolist()
        point_b2 = self.find_start_of_longest_consecutive_sequence(min_value_times2)
        point_b_value2 = data_file[data_file['NO']== point_b2]
        print(f'the Point B2 : {point_b2} sec  at value is {point_b_value2["SValue"].values[0]}')
        #show on spingbox
        self.parent().showParameterValue(max_value1["NO"],point_b,min_value2["NO"],point_b2)
        self.a1 = int(max_value1["NO"])
        self.b1 = int(point_b)
        self.a2 = int(min_value2["NO"])
        self.b2 = int(point_b2)

        #print(data_file)
        self.file_path = "/home/mst/mst_app/analyze/your_file.csv"
        self.counter = 0
        while os.path.exists(self.file_path):
            self.counter +=1
            self.file_path = f"/home/mst/mst_app/analyze/your_file{self.counter}.csv"
        data_file.to_csv(self.file_path, index=False)
        pass

    def plot_mst(self, file_path):
        pass
    
    def show_graph_window(self):
        self.graph_window1 = GraphWindow(path=self.file_path, sellet ="cap",a= self.a1,b=self.b1)
        self.graph_window2 = GraphWindow(path=self.file_path, sellet="tan", a= self.a2,b=self.b2)
        self.graph_window2.show()
        self.graph_window1.show()

    def find_start_of_longest_consecutive_sequence(self, numbers):
        if not numbers:
            return None

        # Create a set from the list for O(1) look-ups
        num_set = set(numbers)
        longest_streak = 0
        start_number = None

        for num in numbers:
            # Only consider `num` as the start of a sequence if `num - 1` is not in the set
            if num - 1 not in num_set:
                current_num = num
                current_streak = 1

                # Count the length of the consecutive sequence starting from `num`
                while current_num + 1 in num_set:
                    current_num += 1
                    current_streak += 1

                # Update the longest streak and the corresponding start number
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    start_number = num

        return start_number

class GraphWindow(QDialog):
    def __init__(self,path,sellet,a,b):
        super().__init__()
        self.path = path
        self.setWindowTitle("Graph Window")
        self.setGeometry(500, 100, 600, 400)

        self.central_widget = QWidget()
        #self.setCentralWidget(self.central_widget)

        self.layout2 = QVBoxLayout()
        self.central_widget.setLayout(self.layout2)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = CustomNavigationToolbar(self.canvas, self)
        self.layout2.addWidget(self.canvas)
        self.layout2.addWidget(self.toolbar)
        self.setLayout(self.layout2)
        if sellet == "cap" :
            self.generate_plot1(self.path,a,b)
        if sellet == "tan":
            self.generate_plot2(self.path,a,b)

    def generate_plot1(self, file_path,a,b):
        # Generate random time series data
        df = pd.read_csv(file_path)
        point_a = df[df['NO']== a]
        point_b = df[df['NO']== b]
        # Plot the time series data
        ax1 = self.figure.add_subplot(111)
       
        ax1.set_xlabel('Sec.')
        ax1.set_ylabel('Cap', color='tab:red')
        ax1.plot(df['NO'], df['MValue'], color='red', label='Capacitive')
        ax1.plot(df['NO'], df['MValue_Analyze'], color='orange', label='Dif Change')
        ax1.annotate(f"A = {a}", xy=(a, point_a["MValue"].values[0]), xytext=(-10, 10), textcoords='offset points', ha='right')
        ax1.annotate(f"B = {b}", xy=(b, point_b["MValue"].values[0]), xytext=(-10, 10), textcoords='offset points', ha='left')
        ax1.scatter([a,b], (point_a["MValue"].values[0],point_b["MValue"].values[0]), color='red', s=50, zorder=5,alpha=0.4)
        ax1.axvline(x=a, ymin=0, ymax=100, color='gray', linestyle='--')
        ax1.axvline(x=b, ymin=0, ymax=100, color='gray', linestyle='--')
        #ax1.tick_params(axis='y', labelcolor='tab:red')

    def generate_plot2(self, file_path,a,b):
        # Generate random time series data
        df = pd.read_csv(file_path)
        point_a = df[df['NO']== a]
        point_b = df[df['NO']== b]
        # Plot the time series data
        ax1 = self.figure.add_subplot(111)
       
        ax1.set_xlabel('Sec.')
        ax1.set_ylabel('tan\u03F4', color='tab:blue')
        ax1.plot(df['NO'], df['SValue'], color='blue', label='tan\u03F4')
        ax1.plot(df['NO'], df['SValue_Analyze'], color='purple', label='Dif Change')
        ax1.annotate(f"A = {a}", xy=(a, point_a["SValue"].values[0]), xytext=(-10, 10), textcoords='offset points', ha='right')
        ax1.annotate(f"B = {b}", xy=(b, point_b["SValue"].values[0]), xytext=(-10, 10), textcoords='offset points', ha='left')
        ax1.scatter([a,b], (point_a["SValue"].values[0],point_b["SValue"].values[0]), color='red', s=50, zorder=5,alpha=0.4)
        ax1.axvline(x=a, ymin=0, ymax=point_a["SValue"].values[0], color='gray', linestyle='--')
        ax1.axvline(x=b, ymin=0, ymax=point_b["SValue"].values[0], color='gray', linestyle='--')
    
