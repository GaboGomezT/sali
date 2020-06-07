import pandas as pd
import json
import math
import datetime
import matplotlib.pyplot as plt
from os import listdir
from collections import Counter
from nltk.corpus import stopwords
from nltk import download
download('stopwords')
dir_chats = "whatsapp chats/"
chats = listdir(dir_chats)

def parse_chat(chat_path):
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

chat_dfs = []
for conversation in chats:
    sender_name = conversation[21:]
    conv = parse_chat(dir_chats + conversation)
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

# Palabras más usadas por Pyme
spanish_stopwords = stopwords.words('spanish')
words = " ".join(pyme_messages["content"]).split()
filtered_words = [word for word in words if word not in spanish_stopwords]
pyme_top_20_palabras = list(Counter(filtered_words).most_common(20))

# Palabras más usadas por Clientes
spanish_stopwords = stopwords.words('spanish')
words = " ".join(client_messages["content"]).split()
filtered_words = [word for word in words if word not in spanish_stopwords]
clientes_top_20_palabras = list(Counter(filtered_words).most_common(20))

