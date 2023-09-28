from datetime import datetime, timedelta
from sp_api.base import Marketplaces
from sp_api.api import Orders , Catalog , ProductFees, Products
from sp_api.util import throttle_retry, load_all_pages
from sp_api.base import Marketplaces
from sp_api.base.exceptions import SellingApiException



import pandas as pd
import time

import threading



exception_codes = {
    'PackageDimensions' : -8888,
    'Low_Ratio'    : -777777,
    'Unauthorized' : -666666,
    'InvalidInput' : -555555,
    'feesEstimate' : -444444,
    'BuyboxPrices' : -333333,
    'LowestPrices' : -222222,
    'noCredential' : -111111
}

amazon_Market_place_Ids = ['A3DWYIK6Y9EEQB',
    'AN1VRQENFRJN5',
    'ANEGB3WVEVKZB',
    'A3JWKAKR8XB7XF  ',
    'A1X6FK5RDHNB96']
"""
amazon_Market_place_Ids = {
    'ca' : 'A3DWYIK6Y9EEQB',
    'ja' : 'AN1VRQENFRJN5',
    'au' : 'ANEGB3WVEVKZB',
    'de' : 'A3JWKAKR8XB7XF  ',
    'fr' : 'A1X6FK5RDHNB96'
    #'uk' : 'A3DWYIK6Y9EEQB',
}
"""

def get_Buy_Price(asin,credentials):
    try:
        #Alış Fiyatı
        comResponse = Products(credentials=credentials, marketplace=Marketplaces.US).get_item_offers(asin,item_condition='New')
        
        lowestBuyPrice = comResponse.payload['Summary']['LowestPrices'][0].get('LandedPrice')['Amount']   # Kontolü yapılacak

        for lowestPrices in comResponse.payload['Summary']['LowestPrices']:
            if lowestPrices.get('condition') == 'new':
                temp_low_price = lowestPrices.get('LandedPrice')['Amount']
                if temp_low_price < lowestBuyPrice:
                    lowestBuyPrice = temp_low_price
    
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Buy_Price'] = lowestBuyPrice

        
        catalogResponse = Catalog(credentials=credentials, marketplace=Marketplaces.US).get_item(asin)
        
        try:
            pack_dims = catalogResponse.payload['AttributeSets'][0]['PackageDimensions']
            lbs_cubic = pack_dims['Height']['value'] * pack_dims['Length']['value'] * pack_dims['Width']['value'] / 135
            #lbs_cubic_fedex = pack_dims['Height']['value'] * pack_dims['Length']['value'] * pack_dims['Width']['value'] / 139
            lbs_weight = pack_dims['Weight']['value']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Lbs'] = max(lbs_weight,lbs_cubic)
        except:
            None
        
        try:
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Title'] = catalogResponse.payload['AttributeSets'][0]['Title']
        except:
            None   
        try:
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'SalesRank'] = catalogResponse.payload['SalesRankings'][0]['Rank']
        except:
            None

    except IndexError as ind:
        #print(ind)
        """
        sw_log = pd.read_excel('SW_LOG.xlsx')[['DATE','LOG','DETAIL']]
        t_date = datetime.now()
        final_log = sw_log.append(pd.Series([t_date, 'GetBuyPrice Hata', f'asin : {asin} with error {ind}'],index=['DATE','LOG','DETAIL']), ignore_index=True)
        final_log.to_excel('SW_LOG.xlsx')
        """
    except KeyError as k:
        #print(k)
        code_res = -100000
    
        if  k.args[0] == 'BuyboxPrices':
            code_res = exception_codes['BuyboxPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif  k.args[0] == 'LowestPrices':
            code_res = exception_codes['LowestPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Buy_Price'] = code_res
        

    except SellingApiException as e:
        #print(e)
        code_res = -100000

        if e.args[0][0]['code'] == 'Unauthorized':
            code_res = exception_codes['Unauthorized']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif e.args[0][0]['code'] == 'InvalidInput':
            code_res = exception_codes['InvalidInput']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == "'BuyBoxPrices'":
            code_res = exception_codes['BuyboxPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == "'LowestPrices'":
            code_res = exception_codes['LowestPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == 'can only concatenate str (not "NoneType") to str':
            code_res = exception_codes['noCredential']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        

        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Buy_Price'] = code_res
        

def get_Sell_Price(asin,credentials,target_marketPlace):
    try:
        
        

        #Satış Fiyatı
        targetResponse = Products(credentials=credentials, marketplace=target_marketPlace).get_item_offers(asin,item_condition='New')
        lowestSellPrice = targetResponse.payload['Summary']['LowestPrices'][0].get('LandedPrice')['Amount']

        for lowestPrices in targetResponse.payload['Summary']['LowestPrices']:
            if lowestPrices.get('condition') == 'new':
                temp_low_price = lowestPrices.get('LandedPrice')['Amount']
                if temp_low_price < lowestSellPrice:
                    lowestSellPrice = temp_low_price

        
        
        try:
            buyboxSellPrice = targetResponse.payload['Summary']['BuyBoxPrices'][0].get('LandedPrice')['Amount']
        except:
            print('')
        
        
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Amazon_Current'] = 0
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Is_Buybox_Fba'] = False
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Fba_Seller_Count'] = '0'

        
        for offer in targetResponse.payload['Offers']:
            if (offer['SellerId'] in amazon_Market_place_Ids):
                main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Amazon_Current'] = offer['ListingPrice']['Amount']
            if offer['IsBuyBoxWinner'] and offer['IsFulfilledByAmazon']:
                main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Is_Buybox_Fba'] = True
        
        for sumOffer in targetResponse.payload['Summary']['NumberOfOffers']:
            if sumOffer['fulfillmentChannel'] == 'Amazon':
                main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Fba_Seller_Count'] = sumOffer['OfferCount']
        

        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Sale_Price'] = lowestSellPrice

    except KeyError as k:

        code_res = -100000
    
        if  k.args[0] == 'BuyboxPrices':
            code_res = exception_codes['BuyboxPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif  k.args[0] == 'LowestPrices':
            code_res = exception_codes['LowestPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Sale_Price'] = code_res
        


    except SellingApiException as e:

        code_res = -100000

        
        if e.args[0][0]['code'] == 'Unauthorized':
            code_res = exception_codes['Unauthorized']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif e.args[0][0]['code'] == 'InvalidInput':
            code_res = exception_codes['InvalidInput']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == "'BuyBoxPrices'":
            code_res = exception_codes['BuyboxPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == "'LowestPrices'":
            code_res = exception_codes['LowestPrices']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == 'can only concatenate str (not "NoneType") to str':
            code_res = exception_codes['noCredential']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True


        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Sale_Price'] = code_res
        
        

def calculate(asin, credentials, target_marketPlace, lowestBuyPrice, lowestSellPrice, shipping_cost, temp_curr, curr_type,minRatio):
    try :
        cost = round((lowestBuyPrice + shipping_cost + 1) * temp_curr,2)
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Cost'] = cost
        asinRatio = lowestSellPrice / cost
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Ratio'] = asinRatio
        if asinRatio >= minRatio:
            vat_cost = 0
            fee_mult = 1
            if target_marketPlace == Marketplaces.DE or target_marketPlace == Marketplaces.FR:
                vat_cost = lowestSellPrice/6

            if target_marketPlace == Marketplaces.DE or target_marketPlace == Marketplaces.FR or target_marketPlace == Marketplaces.UK:
                fee_mult = 1.2

            productResponse = ProductFees(credentials=credentials, marketplace=target_marketPlace).get_product_fees_estimate_for_asin(asin,lowestSellPrice,currency=curr_type,is_fba=True)
            totalFee = productResponse.payload['FeesEstimateResult']['FeesEstimate']['TotalFeesEstimate']['Amount']
            profit = lowestSellPrice - vat_cost - (totalFee * fee_mult) - cost
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Profit'] = profit
        else:
            profit = -777777
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Profit'] = profit
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True

    except KeyError as k:

        code_res = -100000
    
        if  k.args[0] == 'FeesEstimate':
            code_res = exception_codes['feesEstimate']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Profit'] = code_res
        profit = code_res

    except SellingApiException as e:

        code_res = -100000

        
        if e.args[0][0]['code'] == 'Unauthorized':
            code_res = exception_codes['Unauthorized']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif e.args[0][0]['code'] == 'InvalidInput':
            code_res = exception_codes['InvalidInput']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == "'FeesEstimate'":
            code_res = exception_codes['feesEstimate']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        elif str(e) == 'can only concatenate str (not "NoneType") to str':
            code_res = exception_codes['noCredential']
            main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Error_Code'] = True
        
        main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Profit'] = code_res
        profit = code_res

    profit_percentage = profit / cost
    main_dataframe.loc[main_dataframe.eval("Asin == @asin"),'Profit_Percentage'] = profit_percentage
    



# DB : Title -*- Asin -*- SalesRank -*- Drop_Count -*- Buy_Price -*- Sale_Price -*- Ratio -*- Cost -*- Profit -*- Profit_Percentage -*- Sales_Info -*- Date
#       Fba_Seller_Count -*-  Is_Buybox_Fba  -*- Is_Amazon_Selling

data = { 
    'Title' : [],
    'Asin' : [],
    'SalesRank' : [],
    'Drop_Count' : [],
    'Buy_Price' : [],
    'Sale_Price' : [],
    'Ratio' : [],
    'Cost' : [],
    'Profit' : [],
    'Profit_Percentage' : [],
    'Sales_Info' : [],
    'Date' : [],
    'Fba_Seller_Count' : [],
    'Is_Buybox_Fba' : [],
    'Amazon_Current' : [],
    'Lbs' : [],
    'Error_Code' : []
}

main_dataframe = pd.DataFrame(data)

minimumRatio = 1.5

# hata kodlarına göre boşa aramasını engelle

def work(slice_of_df, us_market, target_market):

    global main_dataframe
    main_dataframe = pd.DataFrame(data)
    main_dataframe = pd.merge(main_dataframe,slice_of_df['Asin'],how='outer',on=["Asin" , 'Asin'])
    print(main_dataframe.columns)
    print(main_dataframe)
    main_dataframe['Error_Code'] = False

    n = 9   # blok sayısı
    k = 0
    b = time.time()
    while True:
        k = k + 1
        print(k)

        threads = list()

        if k % 10 == 0:
            time.sleep(5)

        buy_price_df = main_dataframe[(main_dataframe.Error_Code == False) & ((main_dataframe.Buy_Price.isnull()) | (main_dataframe.Buy_Price == -100000))]['Asin']#.tail(n)
        sale_price_df = main_dataframe[(main_dataframe.Error_Code == False) & ((main_dataframe.Buy_Price.notnull()) & (main_dataframe.Buy_Price != -100000) & ((main_dataframe.Sale_Price.isnull()) | (main_dataframe.Sale_Price == -100000)))]['Asin']#.tail(n)
        profit_df = main_dataframe[(main_dataframe.Error_Code == False) & (((main_dataframe.Buy_Price.notnull()) & (main_dataframe.Buy_Price != -100000) & (main_dataframe.Sale_Price.notnull()) & (main_dataframe.Sale_Price != -100000)) & ((main_dataframe.Profit.isnull()) | (main_dataframe.Profit == -100000)))]['Asin']#.tail(n)
        


        if (buy_price_df.count() + sale_price_df.count() + profit_df.count()) <= 0:
            break

        z = 0

        for asin in buy_price_df:
            z = z + 1
            #print(asin)
            t1 = threading.Thread(target=get_Buy_Price, args=([asin,us_market.credentials]))
            threads.append(t1)
            t1.start()
        print(z)
        zz = 0
        for asin in sale_price_df:
            zz = zz+1
            
            t2 = threading.Thread(target=get_Sell_Price, args=([asin,target_market.credentials,target_market.api_market_place]))
            threads.append(t2)
            t2.start()
        print(zz)
        zzz = 0
        #calculate(asin, credentials, target_marketPlace, lowestBuyPrice, lowestSellPrice, shipping_cost, temp_curr, curr_type)
        for asin in profit_df:
            zzz = zzz+1
            
            lowestBuyPrice = main_dataframe[main_dataframe.Asin == asin].iloc[0]['Buy_Price']
            lowestSellPrice = main_dataframe[main_dataframe.Asin == asin].iloc[0]['Sale_Price']
          
            t3 = threading.Thread(target=calculate, args=([asin,target_market.credentials,target_market.api_market_place,lowestBuyPrice,lowestSellPrice,target_market.shipping_cost,target_market.curr_rate,target_market.curr_type,minimumRatio]))
            threads.append(t3)
            t3.start()
            
        print(zzz)
        print('**********')
        
        for index,thread in enumerate(threads):
            thread.join()

    print('Son süre  : ' + str(time.time()-b))
    return main_dataframe



######  kendine özel bir thread sınıfı yazıp her asin için görevlendirilmiş işçiye göre çağıracak düzen kurulacak

