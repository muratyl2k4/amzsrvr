import datetime
import pandas as pd
import numpy as np
import time

import MySQLdb
import sshtunnel


"""
sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

markets = ['ca','au','de','fr','uk','ja']


with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username='jaylee54', ssh_password='',
                remote_bind_address=('jaylee54.mysql.pythonanywhere-services.com', 3306)
            ) as tunnel:
                connection = MySQLdb.connect(
                    user='jaylee54',
                    password='muratyl1A',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    database='',
                )
                cursor = connection.cursor()

                for market in markets:
                    query = (f"SELECT * from remote_completed{market}")
                    cursor.execute(query)
                    resultPD = pd.read_sql(query,connection)
                    res = resultPD.drop_duplicates(subset='Asin', keep="last")
                    print(f'market : {market} normal uzunluk : {len(resultPD)}  duplicate çıkınca {len(res)}')
                    res.to_excel(f'databaseBackup/completed{market}.xlsx')
                cursor.close()
                connection.close()



"""




com = pd.read_excel('com123.xlsx')
tar = pd.read_excel('uk123.xlsx')
a = time.time()
res = pd.merge(com,tar,how="left",on='ASIN')
print(time.time()-a)