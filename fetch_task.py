import MySQLdb
import sshtunnel
import pandas as pd
from task_markets import task_markets
sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

market_place_id_to_market = {'A1F83G8C2ARO7P' : 'uk',
                             'A2EUQ1WTGCTBG2' : 'ca',
                             'A39IBJ37TRP1C6' : 'au',
                             'A1VC38T7YXB528' : 'ja',
                             'A1PA6795UKMFR9' : 'de',
                             'A13V1IB3VIYZZH' : 'fr'}

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
            
            query = (f"SELECT * FROM remote_storelink")
            test = pd.read_sql(query,connection)
            cursor.execute(query)
            a = cursor.fetchall()
            
            cursor.close()
            connection.close()

test = pd.DataFrame({
        'id' : [1,2,3],
        'Seller_Id' : ['a','b','c'],
        'MarketPlace_Id' : ['x','y','z'],
        'User_id' : ['k','l','m']})


def fetch_asins(seller_id,market_place_id):
        print
    #return list()


asin_list = ['B00K7KJFL8']
user_id = 1
market_place_id = 'A1F83G8C2ARO7P' #uk



def write_to_db(asin_list,user_id,market_place_id):

    with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='jaylee54', ssh_password='b3k1rs4m3t',
            remote_bind_address=('jaylee54.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            connection = MySQLdb.connect(
                user='jaylee54',
                password='muratyl1A',
                host='127.0.0.1', port=tunnel.local_bind_port,
                database='jaylee54$deneme2',
            )
            cursor = connection.cursor()
    
            
            for asin in asin_list:
                try:
                    query = (f"SELECT * FROM remote_completed{market_place_id_to_market[market_place_id]} WHERE User_id = {user_id} AND Asin = '{asin}' ")
                    cursor.execute(query)
                    query_result = cursor.fetchall()
                    
                    if not query_result: #Completed empty
                        print('completed db de yok')
                        query = (f"SELECT * FROM remote_keepaexcel{market_place_id_to_market[market_place_id]} WHERE Asin = '{asin}' ")
                        cursor.execute(query)
                        query_result = cursor.fetchall()
                        
                        if not query_result: #Keepaexcel empty
                            print('keepa db de yok')
                            query = (f"SELECT * FROM remote_notcompleted{market_place_id_to_market[market_place_id]} WHERE Asin = '{asin}' ")
                            cursor.execute(query)
                            query_result = cursor.fetchall()
                            
                            if not query_result:#not completed is empty
                                print('notcompleted db de yok')
                                query = (f"INSERT INTO remote_notcompleted{market_place_id_to_market[market_place_id]} (Asin) VALUES ('{asin}')")
                                cursor.execute(query)
                                connection.commit()
                                query = (f"INSERT INTO remote_completed{market_place_id_to_market[market_place_id]} (Asin,User_id) VALUES ('{asin}','{user_id}')")
                                cursor.execute(query)
                                connection.commit()
                            else:#notcompleted is not empty
                                print('notcompleted db de var')
                                query = (f"INSERT INTO remote_completed{market_place_id_to_market[market_place_id]} (Asin,User_id) VALUES ('{asin}','{user_id}')")
                                cursor.execute(query)
                                connection.commit()
                        else:#Keepa excel is not empty
                            print('keepa db de var')
                            query = (f"SELECT Asin,Title,SalesRank,Is_Buybox_Fba,Fba_Seller_Count,Amazon_Current FROM remote_completed{market_place_id_to_market[market_place_id]} WHERE Asin = '{asin}' ")
                            cursor.execute(query)
                            query_result = cursor.fetchall()
                            temp = query_result[0]
                            query = (f"INSERT INTO remote_completed{market_place_id_to_market[market_place_id]} (Asin,Title,SalesRank,Is_Buybox_Fba,Fba_Seller_Count,Amazon_Current,User_id) VALUES ('{temp[0]}','{temp[1]}',{temp[2]},{temp[3]},{temp[4]},{temp[5]},{user_id})")
                            cursor.execute(query)
                            connection.commit()
                    else:#Completed is not empty
                        print ('completed db de var')
                except Exception as e:
                    print('yazma işlemi hatalı')






            query = (f"SELECT * FROM remote_storelink")

            cursor.close()
            connection.close()




for i in test.values:
    seller_id = i[1]
    market_place_id = i[2]
    user_id = i[3]
    asin_list = fetch_asins(seller_id,market_place_id)
    write_to_db(asin_list,user_id,market_place_id)


