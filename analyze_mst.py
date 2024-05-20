
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT 

from scipy.signal import find_peaks
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel,QSpinBox ,QWidget, QFileDialog
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
        default_file_name = f"/data_{current_datetime}.csv"
        try :
            with os.path.exists(media_dir):
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
    def __init__(self,parent=None,file_path_csv = None, window_size = 12,periods=2,fillter_x=500,limit_y=100):
        super().__init__(parent)
        self.window_size = window_size
        self.periods = periods
        self.fillter_x = fillter_x
        self.limit_y = limit_y
        self.file_path_csv = file_path_csv
        self.mst_a_b = []
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Analyze")
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax1 = self.figure.add_subplot(111)
        self.ax2 = self.ax1.twinx()  
        self.setGeometry(200, 200, 300, 150)
        layout = QVBoxLayout()
        self.label_1 = QLabel('Average window size : ')
        self.label_2 = QLabel('Rate of Change periods : ')
        self.label_3 = QLabel('Start Analyze of x : ')
        self.label_4 = QLabel('Limit of y : ')
        self.parameter_1 = QSpinBox()
        self.parameter_2 = QSpinBox()
        self.parameter_3 = QSpinBox()
        self.parameter_4 = QSpinBox()
        self.parameter_1.setValue(self.window_size)
        self.parameter_2.setValue(self.periods)
        self.parameter_3.setMaximum(1000)
        self.parameter_3.setValue(self.fillter_x)
        self.parameter_4.setMaximum(1000)
        self.parameter_4.setValue(self.limit_y)

        layout.addWidget(self.label_1)
        layout.addWidget(self.parameter_1)
        layout.addWidget(self.label_2)
        layout.addWidget(self.parameter_2)
        layout.addWidget(self.label_3)
        layout.addWidget(self.parameter_3)
        layout.addWidget(self.label_4)
        layout.addWidget(self.parameter_4)

        self.submit_button = QPushButton("Analyze MST", self)
        self.submit_button.clicked.connect(self.closeAndReturn_mst)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        pass

    def closeAndReturn_mst(self):
        self.window_size = self.parameter_1.value()
        self.periods = self.parameter_2.value()
        self.fillter_x = self.parameter_3.value()
        self.limit_y = self.parameter_4.value()
        self.Analyze_mst(self.file_path_csv)

        self.show_graph_window()
        #self.close()
        self.parent().showParameterValue(self.mst_a_b)
        self.parent().show_graph_in_main_window(self.ax1, self.ax2)
        pass

    
    def Analyze_mst(self, path_file_csv):
        df = pd.read_csv(path_file_csv)
        self.condition_mst(df)
        a, b = self.plot_mst(self.file_path)
        self.mst_a_b = [a,b]
        pass
    

    def condition_mst(self, data_file): 
        data_file['MValue_Mean'] = data_file['MValue'].rolling(window=self.window_size).mean()
        data_file['SValue_Mean'] = data_file['SValue'].rolling(window=self.window_size).mean()
        data_file['MValue_Analyze'] = abs(100*data_file['MValue_Mean'].diff(periods=self.periods).round(3))  # Rate of change for Data1
        data_file['SValue_Analyze'] = abs(100*data_file['SValue_Mean'].diff(periods=self.periods).round(3) )# Rate of change for Data2
        data_file['MValue_Analyze'] = data_file['MValue_Analyze'].where(data_file['MValue_Analyze'] <= self.limit_y)
        data_file['SValue_Analyze'] = data_file['SValue_Analyze'].where(data_file['SValue_Analyze'] <= self.limit_y) 
        #print(data_file)
        self.file_path = "~/mst_app/analyze/your_file.csv"
        self.counter = 0
        while os.path.exists(self.file_path):
            self.counter +=1
            self.file_path = f"~/mst_app/analyze/your_file{self.counter}.csv"
        data_file.to_csv(self.file_path, index=False)
        pass

    def select_two_tuples(self, grouped_data):
        two_tuples = [group for group in grouped_data if len(group) >= 2]
        return two_tuples

    def calculate_average(self, two_tuples):
        averages = []
        for group in two_tuples:
            avg = sum(group) / len(group)
            averages.append(avg)
        return averages
    def classify_into_groups(self, data):
        groups = {}
        for value in data:
            group = value // 10
            if group not in groups:
                groups[group] = []
            groups[group].append(value)
        return tuple(groups.values())
    
    def plot_mst(self, file_path):
        df = pd.read_csv(file_path)
        peaks_MValue_Analyze, _ = find_peaks(df['MValue_Analyze'].dropna(), height=0)
        peaks_MValue_Analyze = [peak for peak in peaks_MValue_Analyze if df['NO'].iloc[peak] > 500]
        top_peaks_MValue_Analyze = sorted(zip(peaks_MValue_Analyze, df['MValue_Analyze'].iloc[peaks_MValue_Analyze]), key=lambda x: x[1], reverse=True)[:5]

        peaks_SValue_Analyze, _ = find_peaks(df['SValue_Analyze'].dropna(), height=0)
        peaks_SValue_Analyze = [peak for peak in peaks_SValue_Analyze if df['NO'].iloc[peak] > 500]
        top_peaks_SValue_Analyze = sorted(zip(peaks_SValue_Analyze, df['SValue_Analyze'].iloc[peaks_SValue_Analyze]), key=lambda x: x[1], reverse=True)[:5]

        mst = []
   

        for idx, peak in enumerate(top_peaks_MValue_Analyze):
            mst.append(df['NO'].iloc[peak[0]])
        for idx, peak in enumerate(top_peaks_SValue_Analyze):
            mst.append(df['NO'].iloc[peak[0]])
     
        # Example data
        data_points = mst

        # Classify values into groups
        grouped_data = self.classify_into_groups(data_points)

        # Select two tuples with two members each
        two_tuples = self.select_two_tuples(grouped_data)

        # Calculate average for each tuple
        averages = self.calculate_average(two_tuples)

        # Print the averages
        print("Averages of selected tuples:", averages)

        return averages[0],averages[1]
    
    def show_graph_window(self):
        self.graph_window = GraphWindow(path=self.file_path)
        self.graph_window.show()

class GraphWindow(QDialog):
    def __init__(self,path):
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
        self.generate_plot(self.path)

    def generate_plot(self, file_path):
        # Generate random time series data
        df = pd.read_csv(file_path)
        peaks_MValue_Analyze, _ = find_peaks(df['MValue_Analyze'].dropna(), height=0)
        peaks_MValue_Analyze = [peak for peak in peaks_MValue_Analyze if df['NO'].iloc[peak] > 500]
        top_peaks_MValue_Analyze = sorted(zip(peaks_MValue_Analyze, df['MValue_Analyze'].iloc[peaks_MValue_Analyze]), key=lambda x: x[1], reverse=True)[:5]

        peaks_SValue_Analyze, _ = find_peaks(df['SValue_Analyze'].dropna(), height=0)
        peaks_SValue_Analyze = [peak for peak in peaks_SValue_Analyze if df['NO'].iloc[peak] > 500]
        top_peaks_SValue_Analyze = sorted(zip(peaks_SValue_Analyze, df['SValue_Analyze'].iloc[peaks_SValue_Analyze]), key=lambda x: x[1], reverse=True)[:5]

        mst = []
   


        # Plot the time series data
        self.ax1 = self.figure.add_subplot(111)
       
        self.ax1.set_xlabel('Sec.')
        self.ax1.set_ylabel('Cap', color='tab:red')
        self.ax1.plot(df['NO'], df['MValue_Mean'], color='red', label='C')
        self.ax1.plot(df['NO'], df['MValue_Analyze'], color='orange', label='change rate')
        self.ax1.tick_params(axis='y', labelcolor='tab:red')

        for idx, peak in enumerate(top_peaks_MValue_Analyze):
            #self.ax1.plot(df['NO'].iloc[peak[0]], peak[1], 'go', label=f'Peak{idx+1}')
            self.ax1.text(df['NO'].iloc[peak[0]], peak[1], f"NO: {df['NO'].iloc[peak[0]]}", fontsize=8, verticalalignment='bottom')
            self.ax1.axvline(x=df['NO'].iloc[peak[0]], ymin=0, ymax=100, color='gray', linestyle='--')
            mst.append(df['NO'].iloc[peak[0]])
        for idx, peak in enumerate(top_peaks_SValue_Analyze):
            #self.ax1.plot(df['NO'].iloc[peak[0]], peak[1], 'go', label=f'Peak{idx+1}')
            self.ax1.text(df['NO'].iloc[peak[0]], peak[1], f"NO: {df['NO'].iloc[peak[0]]}", fontsize=8, verticalalignment='bottom')
            self.ax1.axvline(x=df['NO'].iloc[peak[0]], ymin=0, ymax=100, color='pink', linestyle='--')
            mst.append(df['NO'].iloc[peak[0]])
        print(mst)
        self.ax2 = self.ax1.twinx()  # Create a new y-axis for Data2 and Data4
        color = 'blue'
        self.ax2.set_ylabel('tan \u03F4', color=color)
        self.ax2.plot(df['NO'], df['SValue_Mean'], color=color, label='tan \u03F4')
        self.ax2.plot(df['NO'], df['SValue_Analyze'], color='purple', label='SValue_Analyze')
        self.ax2.tick_params(axis='y', labelcolor=color)
        self.ax2.set_ylim(0, 3)
        
