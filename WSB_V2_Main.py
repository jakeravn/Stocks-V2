import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
import os
import requests
import time
from tabulate import tabulate
import numpy as np

def initialize():
    url='https://stocks.comment.ai/trending.html'
    filename='stocks.html'
    download(filename,url)


def download(filename, url):
    #Developed in Lab-P12
    #downloads a file from a url and caches it locally under filename
    # We do not download again if the file already exists
    if os.path.exists(filename):
        return (str(filename) + " already exists!")
    else: 
        r = requests.get(url)
        r.raise_for_status()
        data = r.text
        f = open(filename, "w", encoding="utf-8")
        f.write(data)
        f.close()
    return (str(filename) + " created!")

def parse_HTML(file):
    f=open(file)
    html=f.read()
    f.close()
    doc=BeautifulSoup(html,'html.parser')
    return doc

def extract_data(doc): 
    tr_data_ls=[]
    table=doc.find_all('tr')
    for tr in table[1:]:
        td_data_ls=[]
        td_data=tr.find_all('td')
        for td in td_data:
            td_data_ls.append(td.get_text())
        sent_num=td_data_ls[1].split(' ') #ls of positve and negative
        clean_td_data_ls=[]
        clean_td_data_ls.append(td_data_ls[2])
        clean_td_data_ls.append(int(td_data_ls[0]))
        clean_td_data_ls.append(round(1000*(int(sent_num[1])-int(sent_num[4]))/int(td_data_ls[0]),2)) #pos:neg ratio
        tr_data_ls.append(clean_td_data_ls)
    
    for line in tr_data_ls:
        ticker=line[0]
        line_data=yf.download(ticker,period='1d', rounding=True,progress=False)
        try:
            volume=int(line_data['Volume'])
        except:
            volume=None
        line.append(volume)
        try:
            close=round(float(line_data['Close']),2)
        except:
            close=None
        line.append(close)
        try: #catch zero division error
            per_change_day=((int(line_data['Close'])/int(line_data['Open']))*100)-100
        except:
            per_change_day=None
        line.append(per_change_day)

    data_df=pd.DataFrame(tr_data_ls)
    data_df.columns=["Ticker","Frequency","Sentiment Ratio","Volume","Price","Change Today"]

    return data_df

class NeuralNetwork():
    
    def __init__(self):
        # seeding for random number generation
        np.random.seed(1)
        
        #converting weights to a 3 by 1 matrix with values from -1 to 1 and mean of 0
        self.synaptic_weights = 2 * np.random.random((3, 1)) - 1

    def sigmoid(self, x):
        #applying the sigmoid function
        return (1 / (1 + np.exp(-x)))

    def sigmoid_derivative(self, x):
        #computing derivative to the Sigmoid function
        return x * (1 - x)

    def train(self, training_inputs, training_outputs, training_iterations):
        
        #training the model to make accurate predictions while adjusting weights continually
        for iteration in range(training_iterations):
            #siphon the training data via  the neuron
            output = self.think(training_inputs)

            #computing error rate for back-propagation
            error = training_outputs - output
            
            #performing weight adjustments
            adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output))

            self.synaptic_weights += adjustments

    def think(self, inputs):
        #passing the inputs via the neuron to get output   
        #converting values to floats
        
        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs, self.synaptic_weights))
        return output

# def intialize_weights():
# def retrieve_weights():
print("Running ++++++")
starttime=time.time()
filename='stocks.html'
df=extract_data(parse_HTML(filename))
print((df))
print(list(df.loc[1,["Ticker","Frequency"]]))
print("Seconds: "+ str(time.time()-starttime))
neural_network=NeuralNetwork()
print(neural_network.synaptic_weights)
input_ls=[]
for idx in range(len(df)):
    input_ls.append(list(df.loc[1,["Frequency","Sentiment Ratio","Volume"]]))
training_inputs=np.array(input_ls)
training_outputs=np.array([list(df["Change Today"])]).T
neural_network.train(training_inputs,training_outputs,100)
print("Final Weights:")
print(neural_network.synaptic_weights)
print("Seconds: "+ str(time.time()-starttime))