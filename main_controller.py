
#sonsuz loop içinde

    #veri tabanlarını kontrol et
        #veri varsa
            # keepa ? uncompleted ?  asin_fetch ?
            # güncel verileri efektif bir şekilde parçala ve sıraya koy
            # Tek seferde çekilecek asin sayısına göre yapılacak toplam asinin pazarlar bazında ağırlıklı ortalaması df.tail kullan
        #veri yoksa
            #eski verileri kontrol et ve güncellemeleri yap

    #sıralanan verileri bloklara ayır

    #parçalara ayırılan verilerin kar oranlarını hesapla

    #kar oranları hesaplanan verileri sisteme yaz

    #uygun gördüğün oranda bekle

from MarketDB import MarketDB
from MyMarketPlace import MyMarketPlace
from main_worker import work
from keepaWorker import keepa_work
import datetime
import threading

import MySQLdb
import sshtunnel

import pandas as pd
import time


sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0






def keepa_worker_thread(slice_of_df_keepa,target,curr_rate,shipping_cost):
    keepa_work(slice_of_df_keepa,target,curr_rate,shipping_cost)


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
            
            for i in range(len(market.completed_asin)):
                try:
                    market.completed_asin = market.completed_asin.fillna(-575757)

                    asin = market.completed_asin.loc[i, "Asin"]
                    temp_title = str(market.completed_asin.loc[i, "Title"])
                    title = temp_title.replace('"','')
                    title = title.replace('\\','')
                    salesrank = int(market.completed_asin.loc[i, "SalesRank"])
                    drop_count = market.completed_asin.loc[i, "Drop_Count"] 
                    buy_price = market.completed_asin.loc[i, "Buy_Price"]
                    sale_price = market.completed_asin.loc[i, "Sale_Price"]
                    ratio = market.completed_asin.loc[i, "Ratio"]
                    cost = market.completed_asin.loc[i, "Cost"]
                    profit = market.completed_asin.loc[i, "Profit"]
                    profit_percentage = market.completed_asin.loc[i, "Profit_Percentage"]
                    date = str(datetime.datetime.now().date())
                    fba_seller_count = market.completed_asin.loc[i, "Fba_Seller_Count"]
                    is_buybox_fba = market.completed_asin.loc[i, "Is_Buybox_Fba"] if market.completed_asin.loc[i, "Is_Buybox_Fba"] != -575757 else False
                    amazon_current = market.completed_asin.loc[i, "Amazon_Current"]
                    error_code = market.completed_asin.loc[i, "Error_Code"]
                    lbs = market.completed_asin.loc[i, "Lbs"]
                    

                    query_update = (f"""UPDATE remote_completed{market.target} SET SalesRank={salesrank},Drop_Count={drop_count},Buy_Price={buy_price},Sale_Price={sale_price},Ratio={ratio},Cost={cost},Profit={profit},Profit_Percentage={profit_percentage},Date='{date}',Fba_Seller_Count={fba_seller_count},Is_Buybox_Fba={is_buybox_fba},Amazon_Current={amazon_current},Error_Code = {error_code}, Weight={lbs} WHERE Asin='{asin}'""")
                    cursor.execute(query_update)
                    
                    try:
                        query_update = (f"""UPDATE remote_completed{market.target} SET Title="{title}" WHERE Asin='{asin}'""")
                        cursor.execute(query_update)
                    except:
                        print(f'title : {title}')
                        print('title allaha emanet')    

                    query_delete = (f"DELETE FROM remote_notcompleted{market.target} WHERE Asin = '{asin}'")
                    cursor.execute(query_delete)

                    connection.commit()

                except Exception as e:
                    print(f'writer hatası: {e}')
                    

        cursor.close()
        connection.close()

        print('yazmayı bitirdim')


# check curr_rates

control_rate = True

while control_rate:
    control_rate = False

    ca = MarketDB('ca')
    jp = MarketDB('ja')
    au = MarketDB('au')
    fr = MarketDB('fr')
    de = MarketDB('de')
    uk = MarketDB('uk')

    #jp = MarketDB('ja')
    markets = [ca,jp,au,fr,de,uk] #bütün pazarları ekle
    #markets = [jp] #bütün pazarları ekle
    for market in markets:
        print(f'curr_rate : {market.my_market_place.curr_rate}')
        if market.my_market_place.curr_rate == 0:
            print('kurda sorun var')
            control_rate = True


us_market = MyMarketPlace('us')


a = time.time()

"""

res = work(pd.DataFrame({'Asin' : ['B01LYHE49W']}),us_market,ca.my_market_place)


print(res)
print(time.time() - a)
"""

genel_toplam = 0

while True:
    
    try:
        b = time.time()
        a = time.time()
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
                    
                query = (f"SELECT * from remote_notcompleted{market.target}")
                cursor.execute(query)
                market.notcompleted = pd.read_sql(query,connection)

                query = (f"SELECT * from remote_keepaexcel{market.target}")
                cursor.execute(query)
                market.keepaexcel = pd.read_sql(query,connection)

            cursor.close()
            connection.close()



        total_notcompleted_asin_count = 0
        total_keepaexcel_asin_count = 0
        


        for market in markets:
            total_notcompleted_asin_count += len(market.notcompleted)
            total_keepaexcel_asin_count += len(market.keepaexcel)

        print(f'total_notcompleted_asin_count : {total_notcompleted_asin_count}')
        print(f'total_keepaexcel_asin_count : {total_keepaexcel_asin_count}')


        total_completed_asin_count = 0

        print(f'kayıp süre : {time.time() - b}')

        for market in markets:
            
            notcompleted_ratio = (len(market.notcompleted) / total_notcompleted_asin_count) if not total_notcompleted_asin_count == 0 else 0
            keepa_ratio = (len(market.keepaexcel) / total_keepaexcel_asin_count) if not total_keepaexcel_asin_count == 0 else 0

            slice_of_df_notcompleted = market.notcompleted.tail(int(notcompleted_ratio * 100))
            slice_of_df_keepa = market.keepaexcel.tail(int(keepa_ratio * 200))  

            tt = len(slice_of_df_notcompleted)
            print(f'notcompleted taranacak asin sayısı {tt}')

            t = len(slice_of_df_keepa)
            print(f'keepa taranacak asin sayısı {t}')
            
            
            genel_toplam = genel_toplam + tt + t
            
            if len(slice_of_df_keepa) >= 1:
                if True:
                    t1 = threading.Thread(target=keepa_worker_thread, args=([slice_of_df_keepa,market.target,market.my_market_place.curr_rate,market.my_market_place.shipping_cost]))
                    t1.start()
                else:
                    print('keepa worker çalışıyor')#BURAYI YOLUNA KOY

            print(f'target : {market.target}')
            
            t_date = datetime.datetime.now()
            if len(slice_of_df_notcompleted) >= 1 :
                if market.target != 'uk':
                    market.completed_asin = work(slice_of_df_notcompleted,us_market,market.my_market_place)
                    total_completed_asin_count += len(market.completed_asin)
                    print(f'hatalı asin sayısı : {market.completed_asin[(market.completed_asin.Error_Code == True)]}  total asin sayısı : {len(market.completed_asin)}')
                    
                    #sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
                    #t_date = datetime.datetime.now()
                    #final_log = sw_log.append(pd.Series([t_date, 'Sorunsuz Çalıştım', f'yapılan asin sayısı : {tt}'],index=['DATE','LOG','DETAIL']), ignore_index=True)
                    #final_log.to_excel('SW_LOG.xlsx')
                    
                    
                else:
                    
                    #sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
                    #t_date = datetime.datetime.now()
                    #final_log = sw_log.append(pd.Series([t_date, 'Main controller', f'Uk de asin var ancak yapmıyorum'],index=['DATE','LOG','DETAIL']), ignore_index=True)
                    #print(final_log)
                    #final_log.to_excel('SW_LOG.xlsx')
                    
                    print('uk yi yapmıyorum')
            else:
                print('üzerinde çalışcak veri yok')

            
            #print(int(notcompleted_ratio * 1000)) # profit calc
            #print(int(keepa_ratio * 1000))        # profit calc
            
            

            #print('3 sn soluklanıyorum')
            #time.sleep(3)
        
        

        #print('total completed asin ' + str(total_completed_asin_count))
        
        if total_completed_asin_count > 0:        
            for market in markets:
                print(market.completed_asin)
                print('***')
                print('***')
                print('***')

            print(f'time = {time.time() - a}')
            
            completed_writer_thread()

        print('bekliyorum')
        
        print(t_date)
        print('genel , toplam : ' , genel_toplam)
        time.sleep(200)
    except Exception as e:
        
        #sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
        #t_date = datetime.datetime.now()
        #final_log = sw_log.append(pd.Series([t_date, 'Main Worker Hata', f'{e}'],index=['DATE','LOG','DETAIL']), ignore_index=True)
        #final_log.to_excel('SW_LOG.xlsx')
        
        print('main controller hata')
