
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

import MySQLdb
import sshtunnel

import pandas as pd
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0


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
                write_df = market.completed_asin[(market.completed_asin.Sales_Info != -898989)  & (market.completed_asin.Sales_Info.notnull()) & (market.completed_asin.Sales_Info != -575757)]
                
                for i in write_df.values:
                    try:
                        asin = i[0]
                        sale_info = i[1]
                        #error_code = market.completed_asin.loc[i, "Error_Code"]

                        query_update = (f"""UPDATE remote_completed{market.target} SET Sales_Info={sale_info} WHERE Asin='{asin}'""")
                        cursor.execute(query_update)

                        connection.commit()
                        print(f'asin : {asin} satış : {sale_info}  -->  güncelledim')

                    except Exception as e:
                        
                        print(f'writer hatası: {e}')
            else:
                print('pazar için yazılacak veri yok')
                    

        cursor.close()
        connection.close()

        print('yazmayı bitirdim')




def control(where, By_option, path):    
    #global stop
    #stop = False
    temp_input = None
    start = time.time()
    while True:
        if (time.time() - start) >= 10:
            #stop = True
            break 
        try : 
            if By_option==By.TAG_NAME:
                temp_input = where.find_elements(By_option,path)
            else :
                temp_input = where.find_element(By_option,path)
            break
        except Exception as e:
            continue
    return temp_input






ca = MarketDB('ca')
jp = MarketDB('ja')
au = MarketDB('au')
fr = MarketDB('fr')
de = MarketDB('de')
uk = MarketDB('uk')

chop = webdriver.ChromeOptions()
chop.add_extension('njmehopjdpcckochcggncklnlmikcbnb.crx')
driver = webdriver.Chrome(options = chop)
#driver.start_client()
driver.get("https://www.amazon.com/dp/B0000AQOD3?th=1")
    
time.sleep(15)

markets = [ca,jp,au,fr,de,uk] #bütün pazarları ekle
#markets = []

market_links_dict = dict(
        ca = 'https://www.amazon.ca/dp/',
        ja = 'https://www.amazon.co.jp/dp/',
        au = 'https://www.amazon.com.au/dp/',
        de = 'https://www.amazon.de/dp/',
        fr = 'https://www.amazon.fr/dp/',
        uk = 'https://www.amazon.co.uk/dp/'
    )

#paysametaydin@gmail.com

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
                query = (f"SELECT Asin,Sales_Info,Drop_Count,Profit_Percentage,SalesRank from remote_completed{market.target} WHERE Sales_Info IS NULL OR Sales_Info = -575757")
                cursor.execute(query)
                temp_df = pd.read_sql(query,connection)
                if len(temp_df) > 0:
                    if market.target == "au":
                        temp_df_with_drops = temp_df.drop_duplicates()
                    else:
                        temp_df_with_drops = temp_df.drop_duplicates().query('Drop_Count > 0 or SalesRank < 50000') #and Drop_Count != -575757').query('Drop_Count > 0')
                    market.completed_asin = temp_df_with_drops.drop_duplicates().query('Profit_Percentage >= 0.2')
                    print(f'target : {market.target} ---  asin sayısı : {len(market.completed_asin)}')
                else:
                    print('db boş')

            cursor.close()
            connection.close()



        total_asin_for_helium = 0
        
#0 363 158 0 0 59

        for market in markets:
            total_asin_for_helium += len(market.completed_asin)

        print(f'total_asin_for_helium : {total_asin_for_helium}')
        total_asin_for_helium_count = 0

        for market in markets:
            
            asin_ratio = (len(market.completed_asin) / total_asin_for_helium) if not total_asin_for_helium == 0 else 0
            if len(market.completed_asin) > 0:
                asins = market.completed_asin.tail(int(asin_ratio * 100))['Asin']

                t = len(asins)
                print(f'taranacak asin sayısı {t}')

                print(f'target : {market.target}')


                if len(asins) >= 1 :
                    for asin in asins:
            
                        driver.get(market_links_dict[market.target]+asin)
                        sale_data_path = '//*[@id="h10-style-container"]/div[2]/div/div/div/div/div/div/div[2]'
                        sale_data = control(driver,By_option=By.XPATH,path=sale_data_path)  
                        try : 
                            hel_info = int(sale_data.text.replace('.','').strip())
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Sales_Info'] = hel_info
                            total_asin_for_helium_count += len(market.completed_asin)
                            print(sale_data.text)

                        except AttributeError as a:
                            print('-898989')
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Sales_Info'] = -898989
                        except ValueError as v:
                            print('0')
                            market.completed_asin.loc[market.completed_asin.eval("Asin == @asin"),'Sales_Info'] = 0
                            total_asin_for_helium_count += len(market.completed_asin)
                else:
                    print('ratio yetersiz')
            else:
                print('üzerinde çalışcak veri yok')


        
        if total_asin_for_helium_count > 0:        
            for market in markets:
                print(market.completed_asin)
                print('***')
                print('***')
                print('***')

        completed_writer_thread()
        time.sleep(10)
    except Exception as e:
        print('Helium controller hata')
        print(e)


