import datetime
import pandas as pd
import numpy as np
import time

import MySQLdb
import sshtunnel

sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

def get_Com(target):
    
    target = target.replace(-21, np.NaN)

    target.rename(columns = {'Asin':'ASIN'}, inplace = True)
    target.rename(columns = {'New, 3rd Party FBM: Current':'Buy_Price_FBM'}, inplace = True)
    target.rename(columns = {'New, 3rd Party FBA: Current':'Buy_Price_FBA'}, inplace = True)
    target.rename(columns = {'New: Current':'Buy_Price_NC'}, inplace = True)
    target.rename(columns = {'Buy Box: Current':'Buy_Price_BB'}, inplace = True)

    concat_list = []
    
    target_FBM_FBA_Null = target[(target.Buy_Price_FBM.isnull()) & (target.Buy_Price_FBA.isnull())][['ASIN','Buy_Price_BB','Buy_Price_NC']]

    #target bb null New Curr fiyatı eklenecek
    target_BB_Null = target_FBM_FBA_Null[(target_FBM_FBA_Null.Buy_Price_BB.isnull())][['ASIN','Buy_Price_NC']]
    target_BB_Null.rename(columns = {'Buy_Price_NC':'BUY_PRICE'}, inplace = True)
    concat_list.append(target_BB_Null)

    #target bb not null BB fiyatı eklenecek
    target_BB_Not_Null = target_FBM_FBA_Null[(target_FBM_FBA_Null.Buy_Price_BB.notnull())][['ASIN','Buy_Price_BB']]
    target_BB_Not_Null.rename(columns = {'Buy_Price_BB':'BUY_PRICE'}, inplace = True)
    concat_list.append(target_BB_Not_Null)

    target_FBM_FBA_Not_Null = target[(target.Buy_Price_FBM.notnull()) | (target.Buy_Price_FBA.notnull())][['ASIN','Buy_Price_BB','Buy_Price_NC','Buy_Price_FBM','Buy_Price_FBA']]
    minvalue_series_FBM_FBA_Not_Null = target_FBM_FBA_Not_Null[['Buy_Price_BB','Buy_Price_FBM','Buy_Price_FBA']].min(axis = 1)

    #eklenecek min bb, fba, fbm
    target_BB_FBA_FBM_min = pd.DataFrame({'ASIN' : target_FBM_FBA_Not_Null['ASIN'],
                                        'BUY_PRICE' : minvalue_series_FBM_FBA_Not_Null}
    )

    concat_list.append(target_BB_FBA_FBM_min)
    asin_salePrice_df = pd.concat(concat_list)
    res = pd.merge(asin_salePrice_df,target,how='inner',on=["ASIN" , 'ASIN'])[['Title','ASIN','BUY_PRICE']]

    return res

def get_Target(target):
    
    target = target.replace(-21, np.NaN)


    target.rename(columns = {'Asin':'ASIN'}, inplace = True)
    target.rename(columns = {'Sales Rank: Current':'SalesRank'}, inplace = True)
    target.rename(columns = {'Sales Rank: Drops last 30 days':'Drop_Count'}, inplace = True)

    target.rename(columns = {'New, 3rd Party FBM: Current':'Sale_Price_FBM'}, inplace = True)
    target.rename(columns = {'New, 3rd Party FBA: Current':'Sale_Price_FBA'}, inplace = True)
    target.rename(columns = {'New: Current':'Sale_Price_NC'}, inplace = True)
    target.rename(columns = {'Buy Box: Current':'Sale_Price_BB'}, inplace = True)
    target.rename(columns = {'Referral Fee %':'Referral_Fee_Percentage'}, inplace = True)
    target.rename(columns = {'FBA Fees:':'Pick_and_Pack_Fee'}, inplace = True)

    concat_list = []

    target_FBM_FBA_Null = target[(target.Sale_Price_FBM.isnull()) & (target.Sale_Price_FBA.isnull())][['ASIN','Sale_Price_BB','Sale_Price_NC']]

    #target bb null New Curr fiyatı eklenecek
    target_BB_Null = target_FBM_FBA_Null[(target_FBM_FBA_Null.Sale_Price_BB.isnull())][['ASIN','Sale_Price_NC']]
    target_BB_Null.rename(columns = {'Sale_Price_NC':'SALE_PRICE'}, inplace = True)
    concat_list.append(target_BB_Null)

    #target bb not null BB fiyatı eklenecek
    target_BB_Not_Null = target_FBM_FBA_Null[(target_FBM_FBA_Null.Sale_Price_BB.notnull())][['ASIN','Sale_Price_BB']]
    target_BB_Not_Null.rename(columns = {'Sale_Price_BB':'SALE_PRICE'}, inplace = True)
    concat_list.append(target_BB_Not_Null)

    target_FBM_FBA_Not_Null = target[(target.Sale_Price_FBM.notnull()) | (target.Sale_Price_FBA.notnull())][['ASIN','Sale_Price_BB','Sale_Price_NC','Sale_Price_FBM','Sale_Price_FBA']]
    minvalue_series_FBM_FBA_Not_Null = target_FBM_FBA_Not_Null[['Sale_Price_BB','Sale_Price_FBM','Sale_Price_FBA']].min(axis = 1)

    #eklenecek min bb, fba, fbm
    target_BB_FBA_FBM_min = pd.DataFrame({'ASIN' : target_FBM_FBA_Not_Null['ASIN'],
                                        'SALE_PRICE' : minvalue_series_FBM_FBA_Not_Null}
    )

    concat_list.append(target_BB_FBA_FBM_min)
    asin_salePrice_df = pd.concat(concat_list)
    res = pd.merge(asin_salePrice_df,target,how='inner',on=["ASIN" , 'ASIN'])[['ASIN','SalesRank','Drop_Count','SALE_PRICE','Referral_Fee_Percentage','Pick_and_Pack_Fee']]

    return res

#

#  maliyet = Cost    kar = Profit   kar_yüzde = Profit_Percentage   satış_sayısı = Sales_Info
def calculate_Final(market_place,data_start,curr_rate,shipping_cost):

    print(f'size = {len(data_start)}')
    veri_baslangıc = data_start
    
    

    #veri_baslangıc = veri_baslangıc.query('ORAN >= 1.8')

    veri_baslangıc.loc[:, "MALIYET"] = (veri_baslangıc['BUY_PRICE'] + shipping_cost + 1) * curr_rate

    veri_baslangıc.loc[:, "ORAN"] = veri_baslangıc['SALE_PRICE'] / veri_baslangıc['MALIYET'] 

    referral_fee = veri_baslangıc['SALE_PRICE'] * veri_baslangıc['Referral_Fee_Percentage']
    referral_fee_with_tax = referral_fee * 1.2

    pick_and_pack_fee_with_tax = veri_baslangıc['Pick_and_Pack_Fee'] * 1.2

    if market_place == 'ca' or market_place == 'ja' or market_place == 'au':
        veri_baslangıc.loc[:,"KAR"] = veri_baslangıc['SALE_PRICE'] - referral_fee - veri_baslangıc['Pick_and_Pack_Fee'] - veri_baslangıc['MALIYET']

    elif market_place == 'fr' or market_place == 'de':
        veri_baslangıc.loc[:,"KAR"] = (veri_baslangıc['SALE_PRICE'] / 6 * 5) - referral_fee_with_tax - pick_and_pack_fee_with_tax - veri_baslangıc['MALIYET']

    elif market_place == 'uk':
        veri_baslangıc.loc[:,"KAR"] = veri_baslangıc['SALE_PRICE'] - referral_fee_with_tax - pick_and_pack_fee_with_tax - veri_baslangıc['MALIYET']

    
    veri_baslangıc.loc[:, "KAR_YUZDE"] = veri_baslangıc['KAR'] / veri_baslangıc['MALIYET']
    veri_baslangıc.loc[:,"SATIS_SAYISI"] = ""
    return veri_baslangıc
    #veri_baslangıc.to_excel('VERI_BASLANGIC.xlsx')


def keepa_work(result_dataFrame,target_market,curr_rate,shipping_cost):

    

    counter = 0
    while True:

        if counter > 5:
            break
        try:
            #res dolumu boşmu kontrol et
            res = result_dataFrame.replace(-10000,np.nan)
            
            com = res[['Title','Asin','Buy_Price_FBA', 'Buy_Price_BB', 'Buy_Price_FBM',	'Buy_Price_NC']]
            target = res[['Asin','SalesRank','Drop_Count','Sale_Price_NC', 'Sale_Price_BB',	'Sale_Price_FBM', 'Sale_Price_FBA', 'Referral_Fee_Percentage', 'Pick_and_Pack_Fee']]

            data_start = pd.merge(get_Com(com),get_Target(target),how='inner',on=["ASIN" , 'ASIN'])

            final_dataFrame = calculate_Final(target_market,data_start,curr_rate,shipping_cost)


            print('keepa worker : basladım')
                
            a = time.time()
            
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
                
                
                
                for i in range(len(final_dataFrame)):
                    print(i)
                    asin = final_dataFrame.loc[i, "ASIN"]

                    buy_price = final_dataFrame.loc[i, "BUY_PRICE"]
                    sale_price = final_dataFrame.loc[i, "SALE_PRICE"]
                    ratio = final_dataFrame.loc[i, "ORAN"]
                    cost = final_dataFrame.loc[i, "MALIYET"]
                    profit = final_dataFrame.loc[i, "KAR"]
                    profit_percentage = final_dataFrame.loc[i, "KAR_YUZDE"]
                    drop_count = final_dataFrame.loc[i, "Drop_Count"]
                    date = datetime.datetime.now().date()
                    
                    if True :

                        query_update = (f"""UPDATE remote_completed{target_market} SET 
                                
                                Buy_Price = '{buy_price}', 
                                Sale_Price = '{sale_price}',
                                Ratio = '{ratio}',
                                Cost = '{cost}',
                                Profit = '{profit}',
                                Profit_Percentage = '{profit_percentage}',
                                Drop_Count = '{drop_count}',
                                Date = '{date}' WHERE Asin = '{asin}'""")
                        cursor.execute(query_update)
                        

                        query_delete = (f"DELETE FROM remote_keepaexcel{target_market} WHERE Asin = '{asin}'")
                        cursor.execute(query_delete)

                    
                connection.commit()    
                cursor.close()
                connection.close()
                """
                sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
                t_date = datetime.datetime.now()

                final_log = sw_log.append(pd.Series([t_date, 'Sorunsuz Çalıştım', f'yapılan asin sayısı : {len(final_dataFrame)}'],index=['DATE','LOG','DETAIL']), ignore_index=True)

                final_log.to_excel('SW_LOG.xlsx')
                """
                counter = 15
        except Exception as e:
            """
            sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
            t_date = datetime.datetime.now()

            final_log = sw_log.append(pd.Series([t_date, 'KeepaWorker Hata', f'{e}'],index=['DATE','LOG','DETAIL']), ignore_index=True)

            final_log.to_excel('SW_LOG.xlsx')
            """
            print(f'keepa worker hata     : {e}')

    print(f'counter : {counter}')
    print(f'keepa süre : {time.time() - a}')

