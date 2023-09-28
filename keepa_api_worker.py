
import keepa

from MarketDB import MarketDB

import MySQLdb
import sshtunnel

import pandas as pd
import time
import datetime

sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0



accesskey = '' 
api = keepa.Keepa(accesskey)


def completed_writer_thread():
    print('yazmaya başladım')
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
            
            if len(market.completed_asin) >= 1:
                write_df = market.completed_asin[(market.completed_asin.Drop_Count >= -10)]
                
                for i in write_df.values:
                    try:
                        asin = i[0]
                        drop_count = i[1]
                        variation_count = i[2]
                        print(f'var count : {variation_count}')#BURADA KALDIM DENENECEK
                        #error_code = market.completed_asin.loc[i, "Error_Code"]

                        query_update = (f"""UPDATE remote_completed{market.target} SET Drop_Count={drop_count} WHERE Asin='{asin}'""")
                        cursor.execute(query_update)

                        connection.commit()
                        print(f'asin : {asin} satış : {drop_count}  -->  güncelledim')

                    except Exception as e:
                        
                        print(f'writer hatası: {e}')
            else:
                print('pazar için yazılacak veri yok')
                    

        cursor.close()
        connection.close()

        print('yazmayı bitirdim')



ca = MarketDB('ca')
jp = MarketDB('ja')

fr = MarketDB('fr')
de = MarketDB('de')
uk = MarketDB('uk')

markets = [ca,jp,fr,de,uk] #bütün pazarları ekle



while True:
    try:
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
                print(f'*********** {market.target}')
                query = (f"SELECT Asin,Drop_Count,Variation_Asins,Profit_Percentage from remote_completed{market.target} WHERE Drop_Count <=-19 OR Drop_Count IS NULL")
                cursor.execute(query)
                temp_df = pd.read_sql(query,connection)
                if len(temp_df) > 0:
                    market.completed_asin = temp_df.drop_duplicates().query('Profit_Percentage > 0')
                    print(f'target : {market.target} ---  asin sayısı : {len(market.completed_asin)}')
                    
                else:
                    print('db boş')

            cursor.close()
            connection.close()

       

        total_asin_for_keepa_api = 0
        
        for market in markets:
            total_asin_for_keepa_api += len(market.completed_asin)

        print(f'total_asin_for_keepa_api : {total_asin_for_keepa_api}')
        total_asin_made = 0

        for market in markets:
            
            asin_ratio = (len(market.completed_asin) / total_asin_for_keepa_api) if not total_asin_for_keepa_api == 0 else 0
            if len(market.completed_asin) > 0:
                asins = market.completed_asin.tail(int(asin_ratio * 100))['Asin']

                t = len(asins)
                print(f'target : {market.target} taranacak asin sayısı {t}')

                if len(asins) >= 1 :
                    for asin in asins:
            
                        #products = api.query(asin,domain=str(market.target).upper(),stats=90,progress_bar=False) # returns list of product data
                        products = api.query('B0787P86ZZ',domain=ca.target.upper(),stats=90,progress_bar=False) # returns list of product data
                        variations = products[0]['variationCSV']
                        result_varr = str(variations).split(',')

                        print()
                        try : 
                            #print(products[0]['stats_parsed'])
                            drop_count = products[0]['stats_parsed']['salesRankDrops30']
                            
                            #print(drop_count)
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Drop_Count'] = drop_count
                            total_asin_made += 1
                            print(f'asin : {asin} drop_count : {drop_count}')

                            var_count = len(result_varr)
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Variation_Asins '] = var_count

                        except AttributeError as a:
                            print('-898989')
                            print(a)
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Drop_Count'] = -898989
                        except ValueError as v:
                            print('0')
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Drop_Count'] = 0
                            total_asin_made += 1
                        except KeyError as k:
                            print('0')
                            print(k)
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Drop_Count'] = 0
                            
                else:
                    print('ratio yetersiz')
            else:
                print('üzerinde çalışcak veri yok')

        print('total yapılan asin ',total_asin_made)
        
        if total_asin_made > 0:        
            for market in markets:
                print(market.completed_asin)
                print('***')
                print('***')
                print('***')

        completed_writer_thread()
        time.sleep(100)
    except Exception as e:
        print('Keepa Api controller hata')
        print(e)




