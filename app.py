#!/usr/bin/env python

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib
matplotlib.use('Agg')  # Specify the backend explicitly
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
from serial_mst import Serial_mst, SerialConnectionError
from analyze_mst import Analyze_mst, AnalyzeError
import time
import csv
import os


state = False
class WidgetGallery(QWidget):
        
    def __init__(self):
        
        
        super().__init__()
        self.initUI()
        self.s = Serial_mst(port='/dev/mst/meter') #'/dev/mst/meter' แก้ไขก่อนส่ง######################
        self.file_path = "/home/mst/mst_app/data/output.csv"
        self.picture_path ="/home/mst/mst_app/data/output.jpg"
        self.str1 = 'C'
        self.str2 = 'D'
        self.str3 = '1kHz'
        self.str1_1 = "F"
        self.str2_1 = ""
    def initUI(self):
        self.timer=QTimer(self)
        self.timer_readSerial = QTimer(self)
        self.hz_value = 1000
        self.sum_time = 0
        self.interval_time = 1
        self.frist_time = 0
        self.show_time = 0
        self.set_fixHight = 165
        self.time_end = 99999

        self.timer_readSerial.timeout.connect(self.read_serial)
        self.timer_readSerial.start(self.hz_value)

        self.setFixedSize(QSize(800,480))
        self.setStyle(QStyleFactory.create('Fusion'))
        


        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()
        self.InitialState()

        mainLayout = QGridLayout()
        
        mainLayout.addWidget(self.topLeftGroupBox, 0, 0)
        mainLayout.addWidget(self.topRightGroupBox, 0, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 1, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 1, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("โปรแกรมวัดค่าความเสถียรของน้ำยาด้วยคุณสมบัติทางไฟฟ้า")
        self.setWindowState(Qt.WindowMaximized)
        #self.changeStyle('Fusion')


    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("กราฟแสดงค่าการวัด")

        layout = QVBoxLayout()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)
        #layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)
        

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("การตั้งค่าการวัด ความเสถียรของยาง")
        self.topRightGroupBox.setFixedWidth(300)
        defaultPushButton = QPushButton("Default Push Button")
        defaultPushButton.setDefault(True)
        H_W_ME = QWidget()
        H_H_ME = QWidget()
        h_w_me = QHBoxLayout(H_W_ME)
        self.h_comboBox_select_time = QHBoxLayout(H_H_ME)
        self.st_start_stopButton = QPushButton("START/STOP")
        self.comboBox_selected_time = QComboBox(self)
        self.Label_select_time = QLabel("เลือกระยะเวลา")
        self.comboBox_selected_time.addItems(["None","1000sec","1200sec","1500sec","1800sec"])
        self.comboBox_selected_time.setCurrentIndex(0)
        self.comboBox_selected_time.currentIndexChanged.connect(self.time_selected)
        self.h_comboBox_select_time.addWidget(self.Label_select_time)
        self.h_comboBox_select_time.addWidget(self.comboBox_selected_time)

        #self.calibrate_Button.clicked.connect()
        self.sampling_label = QLabel("Sampling")
        #self.sampling_label.setStyleSheet("font-size: 10px")
        
        
        

        self.sampling_select = QComboBox(self)
        fq = ['1Hz','2Hz','1/2Hz']
        self.sampling_select.addItems(fq)
        self.sampling_select.currentIndexChanged.connect(self.Sampling_selected)
        
        
        self.sampling_label.setAlignment(Qt.AlignRight)

        h_w_me.addWidget(self.sampling_label)
        h_w_me.addWidget(self.sampling_select)
        h_w_me.addWidget(self.st_start_stopButton)
      
        self.st_start_stopButton.setStyleSheet("background-color: green")
        self.st_start_stopButton.setCheckable(True)
        self.st_start_stopButton.setChecked(True)
        self.st_start_stopButton.clicked.connect(self.bt_start_stop)
        self.st_start_stopButton.setFixedSize(100,25)

        M_F = QGroupBox("C/L/R")
        M_S = QGroupBox("D/Q/\u03F4/ESR")
        M_Hz = QGroupBox("Hz")
        Fm1 = QVBoxLayout()
        Ms2 = QVBoxLayout()
        Mhz = QVBoxLayout()
        # First set of comboboxes
        self.comboBox1 = QComboBox(self)
        self.comboBox1.addItems(["C", "L", "R"])
        self.comboBox1.currentIndexChanged.connect(self.set_data)
        Fm1.addWidget(self.comboBox1)

        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItems(["D", "Q", "\u03F4","ESR"])
        self.comboBox2.currentIndexChanged.connect(self.set_data)
        Ms2.addWidget(self.comboBox2)
        self.comboBox3 = QComboBox(self)
        self.comboBox3.addItems(["100Hz", "1kHz", "10kHz","100kHz"])
        self.comboBox3.setCurrentIndex(1)
        self.comboBox3.currentIndexChanged.connect(self.set_data)
        Mhz.addWidget(self.comboBox3)

        M_F.setLayout(Fm1)
        M_S.setLayout(Ms2)
        M_Hz.setLayout(Mhz)


        layout = QVBoxLayout()
        horizontal_widget = QWidget()
        hlayout = QHBoxLayout(horizontal_widget)
        horizontal_widget.setFixedHeight(130)
        
        hlayout.addWidget(M_F)
        hlayout.addWidget(M_S)
        hlayout.addWidget(M_Hz)
        layout.addWidget(horizontal_widget)
        #layout.addWidget(defaultPushButton)
        layout.addWidget(H_H_ME)
        layout.addWidget(H_W_ME)
        #layout.addWidget(flatPushButton)
        layout.addStretch(5)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setFixedHeight(self.set_fixHight)
        #self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Ignored)

        tab11 = QWidget()
        tab1 = QGridLayout()
        aaaa = QWidget()
        self.measure_1 = QLabel("C : ")
        self.measure_2 = QLabel("D : ")
        self.measure_Feq = QLabel("Feq :")
        self.measure_time = QLabel("Lev :")
        self.measure_process = QLabel("Proc:")
        self.measure_1.setObjectName("Digital_meter")
        self.measure_2.setObjectName("Digital_meter")
        self.measure_Feq.setObjectName("Digital_meter2")
        self.measure_time.setObjectName("Digital_meter2")
        self.measure_process.setObjectName("Digital_meter2")
        self.measure_Feq.setFixedHeight(25)
        self.measure_time.setFixedHeight(25)
        self.measure_process.setFixedHeight(25)
        tab1Hbox = QHBoxLayout(aaaa)
        #tab1Vbox.setContentsMargins(5, 5, 5, 5)
        tab1Hbox.addWidget(self.measure_Feq)
        tab1Hbox.addWidget(self.measure_time)
        tab1Hbox.addWidget(self.measure_process)
        tab1.addWidget(aaaa,0,0)
        tab1.addWidget(self.measure_1,1,0,)
        tab1.addWidget(self.measure_2,2,0)
        tab11.setLayout(tab1)

        tab2 = QWidget()
        self.textEdit = QTextEdit()
        self.textEdit.scrollContentsBy
        self.textEdit.setPlainText("null")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomLeftTabWidget.addTab(tab11, "Measure")
        self.bottomLeftTabWidget.addTab(tab2, "Table")

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox()
        self.bottomRightGroupBox.setFixedHeight(self.set_fixHight)
        self.bottomRightGroupBox.setFixedWidth(300)
        label_a = QLabel("MST (sec.):")
        label_b = QLabel("B :")
        self.label_a_Cap = QLabel("Capacitive")
        self.label_b_Tan = QLabel("tan \u03F4")
        self.label_a_Cap.setObjectName("Show")
        self.label_b_Tan.setObjectName("Show")
        self.MST_Cap = QSpinBox()
        
        self.MST_Tan = QSpinBox()
        self.label_PSU = QLabel("ม.สงขลานครินทร์ วิทยาเขตสุราษฎร์ธานี")
        self.MST_Cap.setMaximum(2000)
        self.MST_Tan.setMaximum(2000)

        A_B = QWidget()

        Analiz_layout1 = QHBoxLayout(A_B)
       
        #Analiz_layout.setSpacing(30)
        
        self.analiz_mst_ntn = QPushButton("Analyze")
        save_mst_btn = QPushButton("SAVE")
        self.load_mst_btn = QPushButton("Load")
        Analiz_layout1.addWidget(self.load_mst_btn,1)
        Analiz_layout1.addWidget(self.analiz_mst_ntn,1)
        Analiz_layout1.addWidget(save_mst_btn,1)
        save_mst_btn.clicked.connect(self.save_file_csv)
        self.analiz_mst_ntn.clicked.connect(self.show_windows_analyze)
        self.load_mst_btn.clicked.connect(self.load_data)
        layout = QGridLayout()
        layout.addWidget(A_B, 0,0,1,8)
        layout.addWidget(self.label_a_Cap,1,1,1,3)
        layout.addWidget(self.label_b_Tan,1,5,1,3)
        layout.addWidget(label_a,2,0)
        layout.addWidget(self.MST_Cap,2,1,1,3)
        layout.addWidget(self.MST_Tan,2,5,1,3)
        layout.addWidget(self.label_PSU,3,0,1,8)
        #layout.addWidget(self.lineEdit_b1,3,1,1,3)        
        #layout.addWidget(self.lineEdit_b2,3,5,1,3)  

     
        self.bottomRightGroupBox.setLayout(layout)


    def printComboBox1(self):
        print("First ComboBox selected: " + self.comboBox1.currentText())

    def printComboBox2(self):
        print("Second ComboBox selected: " + self.comboBox2.currentText())
    def time_selected(self):
        if self.comboBox_selected_time.currentText() == "None" :
            self.time_end = 99999
        if self.comboBox_selected_time.currentText() == "1000sec":
            self.time_end = 1000
        if self.comboBox_selected_time.currentText() == "1200sec":
            self.time_end = 1200
        if self.comboBox_selected_time.currentText() == "1500sec":
            self.time_end = 1500
        if self.comboBox_selected_time.currentText() == "1800sec":
            self.time_end = 1800

        self.progressBar.setRange(0,self.time_end)
        print("show end time : " + str(self.time_end))
    def InitialState(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, self.time_end)
        self.progressBar.setValue(0)

    
    def bt_start_stop(self):
        
        if self.timer.isActive() :
            self.timer.stop()
            self.timer.timeout.disconnect(self.advanceProgressBar)
            self.st_start_stopButton.setText("START")
            self.st_start_stopButton.setStyleSheet("background-color: green; color: white")
                       
        else:
            self.counter = 0
            self.open = 0
            self.sum_time = 0
            self.show_time = 0
            while os.path.exists(self.file_path):
                self.counter += 1
                self.file_path = f"/home/mst/mst_app/data/output{self.counter}.csv"

            self.progressBar.setValue(0)
            self.st_start_stopButton.setText("STOP")
            self.st_start_stopButton.setStyleSheet("background-color: red")
            self.timer.start(self.hz_value)
            self.timer.timeout.connect(self.advanceProgressBar)

        if self.timer_readSerial.isActive() :
            self.timer_readSerial.stop()
            self.timer_readSerial.timeout.disconnect(self.read_serial)
        else : 
            self.timer_readSerial.start(self.hz_value)
            self.timer_readSerial.timeout.connect(self.read_serial)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        
        self.sum_time = self.interval_time  + self.sum_time
        self.show_time = self.sum_time 
        self.measure_time.setText(str(self.show_time))
        self.progressBar.setValue(int(self.show_time))
        
        self.data = self.s.read_meter()
        self.show_meter(self.data)
        with open(self.file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not self.open:
                writer.writerow(['NO', 'MValue', 'SValue'])
                self.open = 1
            writer.writerow([self.show_time, "{}".format(self.data[0]),"{}".format(self.data[1])])
        try:
            with open(self.file_path, 'r') as file:
                data_string = file.read()
                data = pd.read_csv(self.file_path) if self.file_path.endswith('.csv') else pd.read_csv(self.file_path, delimiter='\t')
                self.textEdit.setPlainText(data_string)
                cursor = self.textEdit.textCursor()
                cursor.movePosition(cursor.End)
                self.textEdit.setTextCursor(cursor)
                self.textEdit.ensureCursorVisible()
                self.plot_data(data)
        except Exception as e:
                print("Error:", e)


        if int(self.show_time) >= self.time_end :
            self.bt_start_stop()
            print(f"CSV file '{self.file_path}' generated successfully!")

  
    def RCL_radiobox_selected(self):
        pass
    def Para2_radiobox_selected(self):
        pass 
    def FEQ_combo_selected(self):
        pass
    def Sampling_selected(self):
        sampling_sl = self.sampling_select.currentIndex()
        print(sampling_sl)
        if sampling_sl == 0 : 
            self.hz_value = 1000
            self.interval_time = 1
        if sampling_sl == 1 :
            self.hz_value = 2000
            self.interval_time = 2
        if sampling_sl == 2 :
            self.hz_value = 500
            self.interval_time = 0.5
        self.timer.start(self.hz_value)
        self.timer_readSerial.start(self.hz_value)
        pass

    def set_data(self):    
        self.str1 = self.comboBox1.currentText()
        self.str2 = self.comboBox2.currentText()
        self.str3 = self.comboBox3.currentText()
        self.s.set_meter(self.str1)
        self.s.set_meter(self.str2)
        self.s.set_meter(self.str3)
        if self.str1 ==  "C" :
            self.str1_1 = "F"
            self.label_a_Cap.setText("Capacitive")
        if self.str1 ==  "L" :
            self.str1_1 = "H"
            self.label_a_Cap.setText("Inductive")
        if self.str1 ==  "R" :
            self.str1_1 = "\u03A9"
            self.label_a_Cap.setText("Resistive")

        if self.str2 ==  "D" : 
            self.str2_1 = ""
            self.label_b_Tan.setText("tan \u03F4")
        if self.str2 ==  "Q" :
            self.str2_1 = ""
            self.label_b_Tan.setText("Q")
        if self.str2 ==  "\u03F4" :
            self.str2_1 = "Rad"
            self.label_b_Tan.setText("Rad")
        if self.str2 ==  "ESR" :
            self.str2_1 = "\u03A9"
            self.label_b_Tan.setText("ESR")
        pass

    def plot_data(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(data.iloc[:, 0], data.iloc[:, 1],'-r')  # Plot 2nd column
        ax2 = ax.twinx()
        ax2.plot(data.iloc[:, 0], data.iloc[:, 2],'-b')  # Plot 3rd column
        ax2.set_ylabel('tan \u03F4', color='b')
        ax.set_title('Data Plot', fontsize=5)
        ax.set_xlabel('time(0.5sec)', fontsize=5)
        ax.set_ylabel('Capacitance',color='r')
        #ax.legend()
        self.canvas.draw()
        self.picture_path = f"/home/mst/mst_app/data/output{self.counter}.jpg"
        self.canvas.figure.savefig(f"{self.picture_path}", format='jpg')
        

        pass
    def load_data(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Data Files (*.csv *.txt)")
        file_dialog.setViewMode(QFileDialog.Detail)
        self.file_path, _ = file_dialog.getOpenFileName(self, "Open Data File", "", "Data Files (*.csv *.txt)")
        if self.file_path:
            try:
                with open(self.file_path, 'r') as file:
                    data_string = file.read()
                data = pd.read_csv(self.file_path) if self.file_path.endswith('.csv') else pd.read_csv(self.file_path, delimiter='\t')
                self.textEdit.setPlainText(data_string)
                print(type(data))
                self.plot_data(data)
            except Exception as e:
                print("Error:", e)

        pass


    def read_serial(self):
        self.show_meter(self.s.read_meter()) # แก้ไขก่อน ส่งงาน   ##############################
            
        pass
    def show_meter(self, data):
        self.measure_1.setText(self.str1 +':'+"{}".format(data[0])+self.str1_1)
        self.measure_2.setText(self.str2 +':'+"{}".format(data[1])+self.str2_1)
        self.measure_Feq.setText('FREQ : '+ self.str3)
        self.measure_time.setText('Time: '+ "{:.1f}".format(self.show_time)+'s')
        self.measure_process.setText('Proc:'+"{:.1f}".format(self.show_time/self.time_end*100.0)+'%')
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        self.topLeftGroupBox.setTitle("กราฟแสดงค่าการวัด   วันเวลา"+ str(current_time))
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    def show_windows_analyze(self):
        self.window_analyze = Analyze_mst(self,file_path_csv=self.file_path)
        self.window_analyze.show()

        pass

    def showParameterValue(self, a1,b1,a2,b2):
        self.MST_Cap.setValue(int((a1+b1)/2))
        self.MST_Tan.setValue(int((a2+b2)/2))
        pass

    def show_graph_in_main_window(self, a, b):
        print(a)
        print(b)
        pass


    def save_file_csv(self):
        usb_drives = []
        media_dir = "/media/mst"
        current_datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        # Initial file name with date and time
        default_file_name = f"/data_{current_datetime}.csv"
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
                str_path = f"data_{current_datetime}.csv"
            
            
        file_path, _ = QFileDialog.getSaveFileName(self,"save Data",str_path, "CSV Files (*.csv)")
        

        if file_path:
            # Write data to the CSV file
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    Text = self.textEdit.toPlainText()
                    lines = Text.strip().split('\n')
                    data_text = [line.split(',') for line in lines]
                    writer.writerows(data_text)
                QMessageBox.information(self, 'Success', 'Data saved to CSV file.')
                QFileDialog.setDirectory(self, self.file_path)
            except Exception as e:
                pass
                #QMessageBox.critical(self, 'Error', f'Failed to save data: {str(e)}')
        pass

if __name__ == '__main__':
    

    #app = QApplication(sys.argv)
    application = QCoreApplication.instance()
    if application is None :
        application = QApplication([])
        application.setStyleSheet(

        '''
            #Show{
                font-size : 15px;
            }
            #RED{
                color :red;
            }
            #Digital_meter{
                font-size : 20px;
                font-family: Courier;  
                font-weight: bold;
                background-color: black;
                color: yellow;
                border: 2px solid yellow;
                border-radius: 10px;
            }
            #Digital_meter2{
                font-size : 15px;
                font-family: Courier;  
                font-weight: bold;
                background-color: black;
                color: yellow;
                border: 2px solid yellow;
                border-radius: 10px;
            }
        '''
    )    
    gallery = WidgetGallery()
    gallery.show()
    application.exec()
    #app.exec()

