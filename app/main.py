import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QFileDialog, QLabel
from dialog import Ui_MainWindow
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import pandas as pd
import json
import math
import datetime
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        title = "Sali"
        self.setWindowTitle(title)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.openFileDialog)

        self.show()

    def openFileDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home', 'JSON files (*.json)')
        
        if fname[0]:
            f = open(fname[0], 'r')
            
            with f:
                data = f.read()
                self.showGraphic()

    def showGraphic():
        filename = 'WhatsApp Chat with Ben Cliente.txt'
        df = pd.read_csv(filename, header=None, error_bad_lines=False,encoding='utf8')
        df = df.drop(0)
        df.columns = ['Date', 'Chat']
        Message = df['Chat'].str.split('-', n=1, expand=True)
        df['Date'] = df['Date'].str.replace(',', '')
        df['Time'] = Message[0]
        df['content'] = Message[1]
        Message1 = df['content'].str.split(':', n=1, expand=True)
        df['content'] = Message1[1]
        df['sender_name'] = Message1[0]
        df = df.drop(columns=['Chat'])
        df['content'] = df['content'].str.lower()
        df['content'] = df['content'].str.replace('<media omitted>', 'MediaShared')
        df['content'] = df['content'].str.replace('this message was deleted',
                                            'DeletedMsg')
        df.dropna(inplace=True)
        df["date_time"] = pd.to_datetime(df.Date + df.Time) 
        df = df.reindex(columns=['date_time', 'sender_name', 'content'])
        df["delta_mensajes_minutos"] = df.date_time.diff()[:].astype('timedelta64[m]')
        df["delta_mensajes_horas"] = df.date_time.diff()[:].astype('timedelta64[h]')
        df = df.set_index("date_time")

        y = df.sender_name.groupby(df.index.hour).count()

        fig = plt.figure()
        ax = plt.axes()
        plt.title("Frecuencia de mensajes x hora del día")
        plt.xlabel("horas")
        plt.ylabel("cantidad de mensajes")
        ax.plot(y.index, y)

        plt.show()

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())