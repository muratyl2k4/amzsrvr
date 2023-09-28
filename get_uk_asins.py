
import MySQLdb
import sshtunnel

import pandas as pd
import time
import datetime

sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

temp_date = datetime.datetime.now().date()
asin = 'B09DL4WHQ1'

with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username='jaylee54', ssh_password='',
        remote_bind_address=('jaylee54.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        connection = MySQLdb.connect(
            user='jaylee54',
            password='muratyl1A',
            host='127.0.0.1', port=tunnel.local_bind_port,
            database='jaylee54$deneme2',
        )
        cursor = connection.cursor()

        query = f"SELECT * FROM  remote_notcompleteduk "
        data = pd.read_sql(query,connection)
        print(len(data))
        
        #temp = cursor.fetchall()
        #print(temp)
        cursor.close()
        connection.close()

data.to_excel('uk_asin.xlsx')