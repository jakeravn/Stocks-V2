#This class has a series of functions for storing data by ticker symbol 
import os
class stock():
    #class contructor: makes a new stock obj to hold relevant data
    #param: self -this stock object
    #param: ticker -str for 
    def __init__(self, ticker):
        folder="stock_data"
        if not os.path.exists(folder):
            os.mkdir(folder)
        filename=ticker+'.csv'
        path=os.path.join(folder,filename)
        f=open(path,'w',encoding='utf-8')
        csv_head=[['Date','Frequency','Sentiment Ratio','Volume','Price','Change Today']]
        f.write(str(csv_head))
        f.close()
    #Gets the .csv file where this data is sto
    def get_filename(self):

    #param: self -this stock object
    #param: data- LS format [Date, Freq, Sent, Volume, Price, Change]
    def add_data(self, data):

    
print("Run")
ticker='SPY'
stock1=stock(ticker)
print("ran")