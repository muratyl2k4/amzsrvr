



class task_markets():

    
    def __init__(self,target):
        self.target = target
        self.__asins = []


    @property
    def asins(self):
        return self.__asins
    
    
    @asins.setter
    def asins(self, value):
        self.__asins = value