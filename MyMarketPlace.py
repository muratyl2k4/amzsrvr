from sp_api.base import Marketplaces

from google_currency import convert
import json


class MyMarketPlace():
    
    #target initiate edilecek olan pazaryeri
    def __init__(self,target):


        credentials = dict(
            lwa_app_id='',
            lwa_client_secret='',
            aws_access_key='',
            aws_secret_key='',
            role_arn=''
        )

        if target == 'us' or target == 'ca':
            credentials['refresh_token'] = ''
        elif target == 'fr' or target == 'de' or target == 'uk':
            credentials['refresh_token'] = ''
        elif target == 'ja' :
            credentials['refresh_token'] = ''
        elif target == 'au' :
            credentials['refresh_token'] = ''
        


        self.credentials = credentials
        
        self.api_market_place = self.marketPlace_dict[target]
        self.curr_type = self.curr_type_dict[target]

        self.curr_type = self.curr_type_dict[target]
        self.curr_rate = self.current_currency()

        self.shipping_cost = 3

    def current_currency(self):
        if self.curr_type != 'usd':
            temp = json.loads(convert('usd',self.curr_type,100000))
            curr_rate = float(temp['amount'])/100000
            
            return curr_rate
        else:
            return 1


    

    
    marketPlace_dict = dict(
        us = Marketplaces.US,
        ca = Marketplaces.CA,
        ja = Marketplaces.JP,
        au = Marketplaces.AU,
        de = Marketplaces.DE,
        fr = Marketplaces.FR,
        uk = Marketplaces.UK
    )

    curr_type_dict = dict(
        us = 'USD',
        ca = 'CAD',
        ja = 'JPY',
        au = 'AUD',
        de = 'EUR',
        fr = 'EUR',
        uk = 'GBP'
    )