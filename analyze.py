import pandas as pd
import json
import math
import datetime
import matplotlib.pyplot as plt

filename = 'WhatsApp Chat with Ben Cliente.txt'
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

y = df.sender_name.groupby(df.index.hour).count()

fig = plt.figure()
ax = plt.axes()
plt.title("Frecuencia de mensajes x hora del día")
plt.xlabel("horas")
plt.ylabel("cantidad de mensajes")
ax.plot(y.index, y)



df["is_q"] = df.apply(lambda x: True if ("?" in x["content"] or "¿" in x["content"]) else False, axis=1)
questions = df[df.is_q==True]
questions = questions[questions["sender_name"].str.strip()!='Gabo']

# Las preguntas del cliente las puedes encontrar en : questions.content.values