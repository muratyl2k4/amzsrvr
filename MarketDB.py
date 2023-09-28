import pandas as pd
from MyMarketPlace import MyMarketPlace

class MarketDB():

    

    def __init__(self,target):
        self.target = target
        self.__notcompleted = pd.DataFrame()
        self.__keepaexcel = pd.DataFrame()
        self.__completed_asin = pd.DataFrame()
        self.__completed_keepa = pd.DataFrame()
        self.my_market_place = MyMarketPlace(target)
    

    @property
    def notcompleted(self):
        return self.__notcompleted
    
    
    @notcompleted.setter
    def notcompleted(self, value):
        self.__notcompleted = value
    
    
    @property
    def keepaexcel(self):
        return self.__keepaexcel
    
    @keepaexcel.setter
    def keepaexcel(self, value):
        self.__keepaexcel = value



    @property
    def completed_asin(self):
        return self.__completed_asin
    
    
    @completed_asin.setter
    def completed_asin(self, value):
        self.__completed_asin = value


    @property
    def completed_keepa(self):
        return self.__completed_keepa
    
    
    @completed_keepa.setter
    def completed_keepa(self, value):
        self.__completed_keepa = value