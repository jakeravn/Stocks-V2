# For data manipulation
from os import set_inheritable
import pandas as pd

# To extract fundamental data
from bs4 import BeautifulSoup as bs
from pandas.core.tools import numeric
import requests
import yfinance as yf
import os
import datetime
import requests
import csv
from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import schedule
import time

### Data Collection

def fundamental_metric(soup, metric):

    return soup.find(text = metric).find_next(class_='snapshot-td2').text

def get_fundamental_data(df):
    for symbol in df.index:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
            r=requests.get(url,headers=headers)
            r.raise_for_status()
            try:
                soup = bs(r.content,'html.parser') 
            except:
                print('fail at parse')
            for m in df.columns:               
                df.loc[symbol,m] = fundamental_metric(soup,m)
        except:
            print(symbol, ' not found')             
    return df

def pull_wsb_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        url='https://stocks.comment.ai/trending.html'
        r=requests.get(url,headers=headers)
        r.raise_for_status()
        doc=bs(r.text,'html.parser')
        trs=doc.find_all('tr')
        tickers=[]
        sentiment=[]
        for tr in trs[1:]:
            tds=tr.find_all('td')
            td_ls=[]
            for td in tds:
                td_ls.append(td.text)
            try:
                sentiment.append(int(td_ls[0]))
            except:
                sentiment.append(None)
            
            try:
                tickers.append(str(td_ls[2]))
            except:
                tickers.append(None)
    except requests.ConnectionError as e:
        print("Unable to reach WSB trending data site",e )
    return tickers, sentiment

def first_pull():
    metric = ['P/B','P/E','Forward P/E','PEG','Debt/Eq','EPS (ttm)','Dividend %','ROE','ROI','EPS Q/Q','Insider Own']
    ret=pull_wsb_data()
    df = pd.DataFrame(index=ret[0],columns=metric)
    df = get_fundamental_data(df)
    df['Sentiment']=ret[1]
    global result
    result=df
    return result

def second_pull(df):
    index=list(df.index)
    per_change_ls=[]
    for ticker in index:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
        r=requests.get(url,headers=headers)
        try:
            r.raise_for_status()
        except:
            print(ticker, 'request failed')
            per_change_ls.append(None)
            continue
        try:
            soup = bs(r.content,'html.parser') 
        except:
            print('fail at parse')
        m="Change"
        per_change_ls.append(str(fundamental_metric(soup,m)))
    df['Percent Change']=per_change_ls
    global result
    result=df
    return result

def get_current_price(ticker_obj):
    todays_data = ticker_obj.history(period='1d')
    return todays_data['Close'][0]

def store_data(df):
    folder='Stocks'
    if not os.path.exists(folder):
        os.mkdir(folder)
    for ticker in list(df.index):
        folder1=os.path.join(folder,ticker)
        if not os.path.exists(folder1):
            os.mkdir(folder1)
        new_data_file=os.path.join(folder1,'new_data.pkl')
        if not os.path.exists(new_data_file):
            f=open(new_data_file,'w')
            f.close()
            data=pd.DataFrame(df.loc[ticker]).T
            data.to_pickle(new_data_file)
        elif os.path.exists(new_data_file):
            data=pd.read_pickle(new_data_file)
            data=pd.concat([data,pd.DataFrame(df.loc[ticker]).T])
            data.to_pickle(new_data_file)

def clean_df(df):
    for ticker in list(df.index):
        try:
            df.loc[ticker,'Percent Change']=float(df.loc[ticker,'Percent Change'].replace('%',''))
        except: 
            continue
    df = df.apply(pd.to_numeric, errors='coerce')
    df=df.replace(np.nan,0)
    global result
    result=df
    return result
    
def store_data_long_term():
    stocks_folder=os.listdir('Stocks')
    for folder in stocks_folder:
        long_data_file=os.path.join('Stocks',folder,'long_data.pkl')
        new_data_file=os.path.join('Stocks',folder,'new_data.pkl')
        data=pd.read_pickle(new_data_file)
        if not os.path.exists(long_data_file):
            f=open(long_data_file,'w')
            f.close()
            data.to_pickle(long_data_file)
            os.remove(new_data_file)
        else:
            long_data=pd.read_pickle(long_data_file)
            for row in list(data.index):
                long_data=pd.concat([long_data, pd.DataFrame(data.loc[row])])
            long_data.to_pickle(long_data_file)
            os.remove(new_data_file)

def load_data(ticker):
    filename=(os.path.join('Stocks',ticker,'new_data.pkl'))
    data=pd.read_pickle(filename)
    return data

def create_prac_data(df):
    for i in range(7):
        store_data(df)

def store_daily_df(df):
    filename=os.join('Stocks','daily.pkl')
    f=open(filename,'w')
    f.close()
    df.to_pickle(filename)

def load_daily_df():
    filename=os.join('Stocks','daily.pkl')
    df=pd.read_pickle(filename)
    os.remove(filename)
    return df

def run_data_first():
    df=first_pull()
    store_daily_df(df)

def run_data_second():
    df=load_daily_df()
    df=second_pull(df)
    df=clean_df(df)
    store_data(df)

### KERAS Modeling

def init_model(): 
    model = Sequential()
    model.add(Dense(12, input_dim=12, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def format_data(ticker):
    data=load_data(ticker)
    target_output_val=pd.DataFrame(data['Percent Change'])
    input_val=data.drop(columns=['Percent Change'])
    return input_val, target_output_val

def run_model(ticker):
    model=init_model()
    input_val, target_output_val=format_data(ticker)
    model.fit(input_val,target_output_val,epochs=150,batch_size=1)
    return model

### Main functions

def main_data_collection():
    schedule.every().day.at('08:00').do(run_data_first)
    schedule.every().day.at('17:00').do(run_data_second)
    while True:
        print('Running Data Collection...')
        schedule.run_pending()
        time.sleep(1)

main_data_collection()

