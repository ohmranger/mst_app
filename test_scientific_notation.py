import sys
import random
import matplotlib
matplotlib.use('Agg')  # Specify the backend explicitly
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class TimeSeriesPlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Time Series Plot")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QPushButton("Generate Plot", self)
        self.button.clicked.connect(self.generate_plot)
        self.layout.addWidget(self.button)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.stats_label = QLabel()
        self.layout.addWidget(self.stats_label)

    def generate_plot(self):
        # Generate random time series data
        num_points = 50
        time_series_data = [random.randint(0, 100) for _ in range(num_points)]

        # Calculate statistics
        sorted_data = sorted(time_series_data, reverse=True)
        max1 = sorted_data[0]
        max2 = sorted_data[1]
        max3 = sorted_data[2]

        # Display statistics
        stats_text = f"Max1: {max1}\nMax2: {max2}\nMax3: {max3}"
        self.stats_label.setText(stats_text)

        # Clear previous plot
        self.figure.clear()

        # Plot the time series data
        ax = self.figure.add_subplot(111)
        ax.plot(range(num_points), time_series_data)
        ax.set_title("Time Series Plot")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")

        # Annotate max1, max2, and max3 with their values and positions
        max_positions = []
        max_values = []
        for i, value in enumerate(time_series_data):
            if value == max1 or value == max2 or value == max3:
                max_positions.append(i)
                max_values.append(value)
                ax.annotate(f"{value}\n({i+1})", xy=(i, value), xytext=(-10, 10), textcoords='offset points', ha='center')
                ax.axvline(x=i, ymin=0, ymax=value/100, color='gray', linestyle='--')
                ax.axhline(y=value, xmin=0, xmax=i/num_points, color='gray', linestyle='--')

        # Draw circles around max1, max2, and max3
        ax.scatter(max_positions, max_values, color='red', s=100, zorder=5)

        # Draw the plot
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeSeriesPlot()
    window.show()
    sys.exit(app.exec_())
