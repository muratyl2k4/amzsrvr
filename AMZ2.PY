
from datetime import datetime, timedelta
from sp_api.base import Marketplaces
from sp_api.api import Orders , Catalog , ProductFees, Products
from sp_api.util import throttle_retry, load_all_pages


from sp_api.base import Marketplaces
from sp_api.api import Orders

import pandas as pd
import time


credentials = dict(
    #refresh token avrupa 
    #refresh_token='Atzr|IwEBIK7NadGedrSYQke-26CRJ3J8UBe3-gaRrYIj5S3B-AjVVU8oHwWpBUyZGl6hji3UMSFdjbvlNjgzThMs4lZ2AulznA-VqElJlwnoyUc9TtSqedUQJmylBiEN5k9Hvu2a7jR42d1J_OAgIO4g4y9Jg7fdOHTUShTm3JWCXGovzRPlEJqGSw9yaVMXn3Zuj7N8j1E7msu4OttnrIFdi_h13tmwgv6V58pNrWpgCvM7fcEB11JEiGx1sYqMEvH8RKYT6ERw3PiRNHyLMT3zfMwx-jJG0ZhnSw95EYQb2wX20qbyjiw97FbO58JRmV2Tgrui3Kf1yFptVix2B7XpsZURvGQp',
    
    #refresh token us
    #refresh_token='Atzr|IwEBIFGdMvwLAop6jzvqI2LzNj5z-2Xrp5UvaXe8O_DdM85RcIE8o2D3MEeAk6QFeK7vVKC56R9n0QDtiGEpBeeXJav6z92q09aYY0WfU46TUN3xfVuCeZnYGlW3L2KCSI9O7ff0ePKYpSV_HNwTSPSBYh7UTJkHFGGSzVptngBndMLolq_bqIfZcxM_EXMQIpztpOlANscWjWRtg4JXuSXg-TkDKuTAmYlRYWcpOaydoO_xfu2fobWv72DumFvQPMOeoMN0520gZeksr1anEkz_SbEzlgUE0HE1xPT7-EPG0kPmwbWojcK1d8QTcZlMwEYw_1F1XQIfysZaRcxhE3hxWVZe',
    
    #refresh token jp
    refresh_token='',
    
    
    lwa_app_id='',
    lwa_client_secret='',
    aws_access_key='',
    aws_secret_key='',
    role_arn='',
)


"""
#order_client = Orders(credentials=credentials, marketplace=Marketplaces.UK)

data_start = pd.read_excel('VERI_BASLANGIC.xlsx')



asins = data_start.query("KAR.isnull() | KAR==-100000")['ASIN']
print('Kontrol edilecek asin sayısı : ' + str(asins.count()))
i=0
for asin in asins:
    try :
        sale_price = float(data_start.query('ASIN == @asin')['SATIS_FIYATI'].values[0])
        buy_price_usd = float(data_start.query('ASIN == @asin')['ALIS_FIYATI'].values[0])
        

        temp_cost = round((buy_price_usd + 2.5) * 0.93232897,2)
        vat_cost = sale_price/6

        productResponse = ProductFees(credentials=credentials, marketplace=Marketplaces.FR).get_product_fees_estimate_for_asin(asin,sale_price,currency='EUR',  is_fba=True,)

        totalFee = productResponse.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']

        temp_profit = sale_price - vat_cost - (totalFee + 0.99) - temp_cost

        i=i+1
        print(i)
        print(temp_profit)

        time.sleep(1.2)
    except Exception as e:
        print(e)
        temp_profit = -10000
        time.sleep(1.2)

    temp_profit_percentage = temp_profit / temp_cost

    data_start.loc[data_start.eval("ASIN == @asin"),'MALIYET'] = temp_cost
    data_start.loc[data_start.eval("ASIN == @asin"),'KAR'] = temp_profit
    data_start.loc[data_start.eval("ASIN == @asin"),'KAR_YUZDE'] = temp_profit_percentage
    
    


data_start.to_excel('Son.xlsx')



"""


#sex =ProductFees(credentials=credentials, marketplace=Marketplaces.FR).get_product_fees_estimate_for_asin("B0BSVF524B",20.9,currency='EUR',  is_fba=True,)
#print(sex)
"""
aFee = sex.payload['FeesEstimateResult']['FeesEstimate']['FeeDetailList'][0]['FeeAmount']['Amount']
ffCost = sex.payload['FeesEstimateResult']['FeesEstimate']['FeeDetailList'][3]['FeeAmount']['Amount']

totalFee = sex.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']


cost = 5

profit = 20.9 - (20.9 / 6.0) - (totalFee*1.2 + 1.0) - cost

print(profit)
"""
"""
sex = ProductFees(credentials=credentials, marketplace=Marketplaces.CA).get_product_fees_estimate(
    [
                    dict(id_type='ASIN', id_value='B07FZ7TSKV',price=241, is_fba =True, currency='CAD'),
                    dict(id_type='ASIN', id_value='B09NK5P28F',price=64.9, is_fba=True, currency='CAD'),
                ]
)
print(sex)
"""
"""
a = ['B09NK5P28F', 'B07FZ7TSKV','B09NK5P28F', 'B07FZ7TSKV','B09NK5P28F', 'B07FZ7TSKV','B09NK5P28F', 'B07FZ7TSKV','B09NK5P28F', 'B07FZ7TSKV']


for asin in a:
    
    print("------------------------------")
"""



data_start = pd.read_excel('JP SELLER ID.xlsx')


print(data_start['ASIN'])
sellerIDs = []


#asinResponse = Products(credentials=credentials, marketplace=Marketplaces.FR).get_item_offers('B09NZD9S1M',item_condition='New')
#print(asinResponse.payload)


for asin in data_start['ASIN']:

    #offers = []
    try :
        print(asin)
        time.sleep(1.2)
        asinResponse = Products(credentials=credentials, marketplace=Marketplaces.JP).get_item_offers(asin,item_condition='New')
        
        asinOffers = asinResponse.payload['Offers']

        #print("başlangıc")
        #print(offers)

        for offer in asinOffers:
            o = offer['SellerId']
            link = 'https://keepa.com/#!seller/5-'+o
            sellerIDs.append(link)
            print(offer['SellerId'])
            #offers = offer['SellerId']+ ',' + offers
        #print("son")
        #print(offers)
        #sellerIDs.append(offers)

        
    except Exception as e:
        print(e)
        time.sleep(1.2)


df = pd.DataFrame(sellerIDs)
df = df.drop_duplicates()

print(sellerIDs)
print(df)
df.to_excel('Seller IDs.xlsx')






