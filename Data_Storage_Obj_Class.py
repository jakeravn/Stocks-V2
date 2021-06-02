#This class has a series of functions for storing data by ticker symbol 
import os
class stock():
    #param: self -this stock object
    #param: ticker -str for 
    def __init__(self, ticker):
        folder="stock_data"
        filename=ticker+'.csv'
        path=os.path.join(folder,filename)
