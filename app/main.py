import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QFileDialog, QLabel
from dialog import Ui_MainWindow
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from os import listdir
from collections import Counter
# from nltk.corpus import stopwords
# from nltk import download
# download('stopwords')

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
        #fname = QFileDialog.getOpenFileName(self, 'Open file', '/home', 'Text files (*.txt)')
        dirname = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        print(dirname)
        if dirname:            
            self.showAnalitics(dirname+'/')
            #self.showGraphic(fname[0])

    def showGraphic(self, fname):
        filename = fname
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

    def parse_chat(self,chat_path):
        filename = chat_path
        df = pd.read_csv(filename, header=None, error_bad_lines=False,
                        encoding='utf8')
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
        return df

    def showAnalitics(self, dir_chats):
        chats = listdir(dir_chats)

        chat_dfs = []
        for conversation in chats:
            sender_name = conversation[21:]
            conv = self.parse_chat(dir_chats + conversation)
            chat_dfs.append(conv)

        all_chats = pd.concat(chat_dfs)
        name_filter = all_chats["sender_name"].str.strip()!='A n e m o n e'
        client_messages = all_chats[name_filter]

        y = client_messages.sender_name.groupby(client_messages.index.hour).count()

        # Horarios con más chats
        horarios = y.sort_values(ascending=False)[:3].index
        mensaje_horarios = f"Sus horarios en donde recibe más mensajes son a las {horarios[0]}hrs, las {horarios[1]}hrs y las {horarios[2]}hrs."

        # ¿Quienes son los clientes más activos?
        client_most_messages = client_messages.groupby(client_messages.sender_name).count().sort_values("content", ascending=False)[:3].index
        most_active_client_message = f"Sus top tres clientes más activos son 1.{client_most_messages[0]}, 2.{client_most_messages[1]}, y 3.{client_most_messages[2]}"

        # ¿Cuál es el tiempo promedio que tardamos en responder?
        pyme_filter = all_chats["sender_name"].str.strip()=='A n e m o n e'
        pyme_messages = all_chats[pyme_filter]
        mean_response = pyme_messages.delta_mensajes_minutos.mean()
        mensaje_respuesta_promedio = f"Usted se tarda en promedio {int(mean_response)} minutos en responder a sus clientes."

        # Tiempo promedio de respuesta de clientes
        mean_client_response = client_messages.delta_mensajes_horas.mean()
        mensaje_respuesta_promedio_cliente = f"Sus clientes se tardan en promedio {int(mean_client_response)} horas en responderle."

        # # Palabras más usadas por Pyme
        # spanish_stopwords = stopwords.words('spanish')
        # words = " ".join(pyme_messages["content"]).split()
        # filtered_words = [word for word in words if word not in spanish_stopwords]
        # pyme_top_20_palabras = list(Counter(filtered_words).most_common(20))

        # # Palabras más usadas por Clientes
        # spanish_stopwords = stopwords.words('spanish')
        # words = " ".join(client_messages["content"]).split()
        # filtered_words = [word for word in words if word not in spanish_stopwords]
        # clientes_top_20_palabras = list(Counter(filtered_words).most_common(20))

        self.ui.lblInfo1.setText("Horarios con más chats")
        self.ui.lbl1.setText(mensaje_horarios)
        self.ui.lblInfo2.setText("¿Quienes son los clientes más activos?")
        self.ui.lbl2.setText(most_active_client_message)
        self.ui.lblInfo3.setText("¿Cuál es el tiempo promedio que tardamos en responder?")
        self.ui.lbl3.setText(mensaje_respuesta_promedio)
        self.ui.lblInfo4.setText("Tiempo promedio de respuesta de clientes")
        self.ui.lbl4.setText(mensaje_respuesta_promedio_cliente)
        # self.ui.lbl5.setText(pyme_top_20_palabras)
        # self.ui.lbl6.setText(clientes_top_20_palabras)

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())