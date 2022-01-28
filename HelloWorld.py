from kiteconnect import KiteConnect,KiteTicker
import pandas as pd
import numpy as np
import datetime as dt
import xlwings as xw
from multiprocessing.dummy import Pool as ThreadPool
import json
import time
from datetime import date
import mibian

#import greek library here

class OptionsDataRetriever:
    def __init__(self):
        self.BankNiftyPEInstruments = ""
        self.BankNiftyCEInstruments = ""
        self.BankNiftySpotPrice = ""
        self.BankNiftyATMPrice = ""
        self.CE_Option_Chain = ""
        self.PE_Option_Chain = ""
        self.Lotsize = 0
        self.Expiry = ""
        self.kconn = ""
        self.interestrates = 4.0
        
    def initiateOptionsData(self, conn):
        self.kconn = conn
        instrument_df = pd.DataFrame(self.kconn.instruments(exchange='NFO'))        
        print("Length of file", len(instrument_df.index))
        temp_df1 = instrument_df[(instrument_df['segment']=='NFO-OPT') & (instrument_df['name']=='BANKNIFTY')].copy()
        temp_df2 = temp_df1.sort_values(by=['expiry'], ascending=True)
        print("Length of filtered file",len(temp_df2.index))
        self.Expiry = temp_df2['expiry'].iloc[0]
        temp_df3 = temp_df2[temp_df2['expiry'] == self.Expiry]
        print("Length of temp_df3", len(temp_df3.index))
        self.BankNiftyCEInstruments = temp_df3[temp_df3['instrument_type'] == 'CE'].sort_values(by=['strike'], ascending=True)     
        self.BankNiftyPEInstruments = temp_df3[temp_df3['instrument_type'] == 'PE'].sort_values(by=['strike'], ascending=True)
        self.BankNiftyCEInstruments.reset_index(drop=True, inplace=True)
        self.BankNiftyPEInstruments.reset_index(drop=True, inplace=True)
        print("Length of BankNiftyCEInstruments", len(self.BankNiftyCEInstruments.index))
        print("Length of BankNiftyPEInstruments", len(self.BankNiftyPEInstruments.index))
               

    def getOpionsChainCE(self,**kwargs):
        Strike = int(0)
        Length = int(0)
        
        for key, value in kwargs.items():
            print ("%s == %s" %(key, value))
            if(key == "Strike"):
                Strike = int(value)
            elif(key == "Length"):
                Length = int(value)
            else:
                Strike = 0
                Length = 0
        
        if Strike == 0:
           Strike = self.BankNiftyATMPrice
           
        if Length == 0:
           Length = 10        
        
        
        print("Strike :", Strike)
        print("self.BankNiftyATMPrice :", self.BankNiftyATMPrice)
        print("type Strike :", type(Strike))
        print("type str(self.BankNiftyATMPrice) :", type(self.BankNiftyATMPrice))        
        #print("Length :", kwargs["Length"])
        
        self.getBankNiftySpot()    
        self.getBankNiftyATM()
        
      
        idx = self.BankNiftyCEInstruments[self.BankNiftyCEInstruments['strike'] == Strike].index
        x = idx.item()

        print("x :", x)
        CE_Chain_DF = self.BankNiftyCEInstruments[(x-Length):(x+Length)].copy()
        CE_Instrument_list = CE_Chain_DF['tradingsymbol'].tolist()

        for i in range(len(CE_Instrument_list)):
            CE_Instrument_list[i] = "NFO:"+ CE_Instrument_list[i]   

        CEPrices = self.kconn.ltp(CE_Instrument_list)
        print(CEPrices)
        
        CE_Chain_DF['IV'] = np.nan
        CE_Chain_DF['Delta'] = np.nan
        
        for ind in CE_Chain_DF.index :
            CE_Chain_DF["last_price"][ind] = CEPrices["NFO:"+CE_Chain_DF["tradingsymbol"][ind]]["last_price"]
            voltyC = mibian.BS([self.BankNiftySpotPrice,CE_Chain_DF["strike"][ind],self.interestrates,(self.Expiry - date.today()).days],callPrice=CE_Chain_DF["last_price"][ind])
            newVoltyC = float("{:.2f}".format(voltyC.impliedVolatility))
            CE_Chain_DF["IV"][ind] = newVoltyC
            c = mibian.BS([self.BankNiftySpotPrice,CE_Chain_DF["strike"][ind],self.interestrates,(self.Expiry - date.today()).days],volatility=newVoltyC)
            CE_Chain_DF["Delta"][ind] = c.callDelta
            
        return CE_Chain_DF     
    
    
    

    def getOpionsChainPE(self,**kwargs):
        Strike = int(0)
        Length = int(0)
        
        for key, value in kwargs.items():
            print ("%s == %s" %(key, value))
            if(key == "Strike"):
                Strike = int(value)
            elif(key == "Length"):
                Length = int(value)
            else:
                Strike = 0
                Length = 0
        
        if Strike == 0:
           Strike = self.BankNiftyATMPrice
           
        if Length == 0:
           Length = 10   
             
        self.getBankNiftySpot()    
        self.getBankNiftyATM()
        
        idx = self.BankNiftyPEInstruments[self.BankNiftyPEInstruments['strike'] == Strike].index
        x = idx.item()
        PE_Chain_DF = self.BankNiftyPEInstruments[(x-Length):(x+Length)].copy()
        PE_Instrument_list = PE_Chain_DF['tradingsymbol'].tolist()

        for i in range(len(PE_Instrument_list)):
            PE_Instrument_list[i] = "NFO:"+ PE_Instrument_list[i]   

        PEPrices = self.kconn.ltp(PE_Instrument_list)
        print(PEPrices)
        
        PE_Chain_DF['IV'] = np.nan
        PE_Chain_DF['Delta'] = np.nan
        
        for ind in PE_Chain_DF.index :
            PE_Chain_DF["last_price"][ind] = PEPrices["NFO:"+ PE_Chain_DF["tradingsymbol"][ind]]["last_price"]
            voltyP = mibian.BS([self.BankNiftySpotPrice,PE_Chain_DF["strike"][ind],self.interestrates,(self.Expiry - date.today()).days],putPrice=PE_Chain_DF["last_price"][ind])
            newVoltyP = float("{:.2f}".format(voltyP.impliedVolatility))
            PE_Chain_DF["IV"][ind] = newVoltyP
            p = mibian.BS([self.BankNiftySpotPrice,PE_Chain_DF["strike"][ind],self.interestrates,(self.Expiry - date.today()).days],volatility=newVoltyP)
            PE_Chain_DF["Delta"][ind] = p.putDelta            

        return PE_Chain_DF
    
    
    def getBankNiftySpot(self):
        CurPrice = self.kconn.ltp('NSE:NIFTY BANK')
        print(CurPrice["NSE:NIFTY BANK"]["last_price"])
        self.BankNiftySpotPrice = (CurPrice["NSE:NIFTY BANK"]["last_price"])
        return self.BankNiftySpotPrice

    def getBankNiftyATM(self):
        CurPrice = self.kconn.ltp('NSE:NIFTY BANK')
        self.BankNiftySpotPrice = (CurPrice["NSE:NIFTY BANK"]["last_price"])
        self.BankNiftyATMPrice = round(self.BankNiftySpotPrice/100)*100
        print("Rounded BankNifty ATM Price",self.BankNiftyATMPrice)        
        return self.BankNiftyATMPrice     

def main():
    print("Hello Option Chain!")
    api_key = open('api_key.txt','r').read()
    api_secret = open('api_secret.txt','r').read()
    api_access_token = open("api_access_token.txt",'r').read()
    print("api_key : ",api_key)
    print("api_secret : ",api_secret)
    print("api_access_token : ",api_access_token)

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(api_access_token)

    odr = OptionsDataRetriever()
    
    odr.initiateOptionsData(kite)
    
    print("BNF Spot",odr.getBankNiftySpot())
    
    print("BNF ATM",odr.getBankNiftyATM())
    
    CE_Chain = odr.getOpionsChainCE()
    print(CE_Chain[['strike','expiry','IV','Delta']])
    
    PE_Chain = odr.getOpionsChainPE(Strike="37900", Length="6")
    print(PE_Chain[['strike','expiry','IV','Delta']])    


if __name__ == "__main__":
    main()

#idx = temp_df5[temp_df5['strike'] == rounded_BNF_Price].index

#y = idx.item()

#print(y)
#print(type(y))

#print(temp_df5[(y-10):(y+10)])

#PE_Chain_DF = temp_df5[(y-10):(y+10)].copy()

#PE_Instrument_list = PE_Chain_DF['tradingsymbol'].tolist()

#print(PE_Instrument_list)
#print(type(PE_Instrument_list))

#for i in range(len(PE_Instrument_list)):
#    PE_Instrument_list[i] = "NFO:"+ PE_Instrument_list[i]   

#print(PE_Instrument_list)


#PEPrices = kite.ltp(PE_Instrument_list)

#print(PEPrices)
#print(type(PEPrices))

#expiryDate = PE_Chain_DF['expiry'].iloc[0]

#print(expiryDate)
#print(type(expiryDate))

#print("Days to expiry",(expiryDate - date.today()).days)

#print(type(expiryDate - date.today()).days)


#voltyC = mibian.BS([BNF_Price,38200,4.0,(expiryDate - date.today()).days],callPrice=645)
#newVoltyC = float("{:.2f}".format(voltyC.impliedVolatility))
#c = mibian.BS([38046,38200,4.0,(expiryDate - date.today()).days],volatility=newVoltyC)

#print(c.callDelta)
#print(type(c.callDelta))


#Read the complete file in Excel.
#wb = xw.Book('Option_Chain.xlsx')
#wks = wb.sheets('Sheet1')
#wks.range("A1").value = instrument_df

#temp_df1 = instrument_df[(instrument_df['segment']=='NFO-OPT') & (instrument_df['name']=='BANKNIFTY')].copy()

#Read the option & Banknifty filtered file in Excel.
#wb = xw.Book('Option_Chain_Filtered.xlsx')
#wks = wb.sheets('Sheet1')
#wks.range("A1").value = temp_df1

#temp_df2 = temp_df1.sort_values(by=['expiry'], ascending=True)


#print("Length of filtered file",len(temp_df2.index))
#print(type(temp_df2))
#print(temp_df2)

#expiry = temp_df2['expiry'].iloc[0]

#print(type(expiry))
#print(expiry)

#temp_df3 = temp_df2[temp_df2['expiry'] == expiry]

#print("Length of temp_df3", len(temp_df3.index))
#print(type(temp_df3))

#temp_df4 = temp_df3[temp_df3['instrument_type'] == 'CE'].sort_values(by=['strike'], ascending=True)
#temp_df5 = temp_df3[temp_df3['instrument_type'] == 'PE'].sort_values(by=['strike'], ascending=True)

#print("Length of temp_df4", len(temp_df4.index))
#print(type(temp_df4))

#Read LTP of banknifty from here. Bank nifty spot price read

#idx = temp_df4.index[temp_df4['strike']== '37100']

#start_time = time.time()

#CurPrice = kite.ltp('NSE:NIFTY BANK')

#print(type(CurPrice))
#print(CurPrice["NSE:NIFTY BANK"]["last_price"])
#print(type(CurPrice["NSE:NIFTY BANK"]["last_price"]))

#BNF_Price = (CurPrice["NSE:NIFTY BANK"]["last_price"])
#print("BankNifty Spot Price",BNF_Price)

#rounded_BNF_Price = round(BNF_Price/100)*100


#rint("Rounded BankNifty Spot Price",rounded_BNF_Price)

#temp_df4.reset_index(drop=True, inplace=True)
#temp_df5.reset_index(drop=True, inplace=True)

"""
idx = temp_df4[temp_df4['strike'] == rounded_BNF_Price].index

print(idx)
print(type(idx))

x = idx.item()

print(x)
print(type(x))

print(temp_df4[(x-10):(x+10)])

CE_Chain_DF = temp_df4[(x-10):(x+10)].copy()

CE_Instrument_list = CE_Chain_DF['tradingsymbol'].tolist()

print(CE_Instrument_list)
print(type(CE_Instrument_list))

for i in range(len(CE_Instrument_list)):
    CE_Instrument_list[i] = "NFO:"+ CE_Instrument_list[i]   

print(CE_Instrument_list)

idx = temp_df5[temp_df5['strike'] == rounded_BNF_Price].index

y = idx.item()

print(y)
print(type(y))

print(temp_df5[(y-10):(y+10)])

PE_Chain_DF = temp_df5[(y-10):(y+10)].copy()

PE_Instrument_list = PE_Chain_DF['tradingsymbol'].tolist()

print(PE_Instrument_list)
print(type(PE_Instrument_list))

for i in range(len(PE_Instrument_list)):
    PE_Instrument_list[i] = "NFO:"+ PE_Instrument_list[i]   

print(PE_Instrument_list)



#bnfInstruments = ["NFO:BANKNIFTY2220338000PE","NFO:BANKNIFTY2220338100PE","NFO:BANKNIFTY2220338300PE"]

CEPrices = kite.ltp(CE_Instrument_list)

print(CEPrices)
print(type(CEPrices))


PEPrices = kite.ltp(PE_Instrument_list)

print(PEPrices)
print(type(PEPrices))

expiryDate = PE_Chain_DF['expiry'].iloc[0]

print(expiryDate)
print(type(expiryDate))

print("Days to expiry",(expiryDate - date.today()).days)

print(type(expiryDate - date.today()).days)


voltyC = mibian.BS([BNF_Price,38200,4.0,(expiryDate - date.today()).days],callPrice=645)
newVoltyC = float("{:.2f}".format(voltyC.impliedVolatility))
c = mibian.BS([38046,38200,4.0,(expiryDate - date.today()).days],volatility=newVoltyC)

print(c.callDelta)
print(type(c.callDelta))

CE_Chain_DF['IV'] = np.nan
CE_Chain_DF['Delta'] = np.nan
PE_Chain_DF['IV'] = np.nan
PE_Chain_DF['Delta'] = np.nan

for ind in CE_Chain_DF.index :
    print(CE_Chain_DF["tradingsymbol"][ind],": ", CE_Chain_DF["last_price"][ind])    
    print(CEPrices["NFO:"+CE_Chain_DF["tradingsymbol"][ind]]["last_price"])
    CE_Chain_DF["last_price"][ind] = CEPrices["NFO:"+CE_Chain_DF["tradingsymbol"][ind]]["last_price"]
    PE_Chain_DF["last_price"][ind] = PEPrices["NFO:"+PE_Chain_DF["tradingsymbol"][ind]]["last_price"]
    voltyC = mibian.BS([BNF_Price,CE_Chain_DF["strike"][ind],4.0,(expiryDate - date.today()).days],callPrice=CE_Chain_DF["last_price"][ind])
    newVoltyC = float("{:.2f}".format(voltyC.impliedVolatility))
    CE_Chain_DF["IV"][ind] = newVoltyC
    c = mibian.BS([BNF_Price,CE_Chain_DF["strike"][ind],4.0,(expiryDate - date.today()).days],volatility=newVoltyC)
    CE_Chain_DF["Delta"][ind] = c.callDelta
    voltyP = mibian.BS([BNF_Price,PE_Chain_DF["strike"][ind],4.0,(expiryDate - date.today()).days],putPrice=PE_Chain_DF["last_price"][ind])
    newVoltyP = float("{:.2f}".format(voltyP.impliedVolatility))
    PE_Chain_DF["IV"][ind] = newVoltyP
    p = mibian.BS([BNF_Price,PE_Chain_DF["strike"][ind],4.0,(expiryDate - date.today()).days],volatility=newVoltyP)
    PE_Chain_DF["Delta"][ind] = p.putDelta
    
    
#CE_Chain_DF.loc[i,"last_price"] = CEPrices["NFO:"+CE_Chain_DF.loc[i,"tradingsymbol"]]["last_price"]



print("--- %s seconds ---" % (time.time() - start_time))



#---------------------------------------------------------------------------



#Read the option & Banknifty filtered file in Excel.
#wb = xw.Book('Option_Chain_Filtered_Sorted.xlsx')
#wks = wb.sheets('Sheet1')
#wks.range("A1").value = temp_df1

#temp_df = temp_df.copy()



final_df = temp_df[temp_df['expiry'] == expiry]

print(type(final_df))

print(len(final_df.index))

underlying_symbols = final_df['name'].to_list() 

print(type(underlying_symbols))

print(len(underlying_symbols))

CE_Tokens = final_df[(final_df['name']=='NIFTY') & (final_df['instrument_type']=='CE')]
CE_Tokens_List = CE_Tokens.instrument_token.to_list()

print(type(CE_Tokens_List))

print(len(CE_Tokens_List))

print(CE_Tokens_List)

PE_Tokens = final_df[(final_df['name']=='NIFTY') & (final_df['instrument_type']=='PE')]
PE_Tokens_List = PE_Tokens.instrument_token.to_list()

print(type(PE_Tokens_List))

print(len(PE_Tokens_List))

print(PE_Tokens_List)


All_Tokens = final_df[(final_df['name']=='NIFTY')].instrument_token.to_list()
All_Strikes = final_df[(final_df['name']=='NIFTY')].strike.to_list()

print(type(All_Strikes))

print(len(All_Strikes))

print(All_Strikes)

lot_size = final_df['lot_size'].to_list()

CE_Token = [int(i) for i in CE_Tokens_List]
PE_Token = [int(i) for i in PE_Tokens_List]
All_Token = [int(i) for i in All_Tokens]


kws = KiteTicker(api_key,api_access_token)

fno_dict = {'CE_OI':[],'CE_IV':[],'CE_VOL':[],'CE_LTP':[],'CE_CHG':[],'STRIKE':[],'PE_CHG':[],'PE_LTP':[],'PE_VOL':[],'PE_IV':[],'PE_OI':[]}

fno_df = pd.DataFrame(fno_dict)

fno_df['CE_IV'] = fno_df['CE_IV'].astype(str)
fno_df['PE_IV'] = fno_df['PE_IV'].astype(str)

wb = xw.Book('Option_Chain.xlsx')
wks = wb.sheets('Sheet1')
#wks.range("A1").value = instrument_df

i = 0

for strike in All_Strikes:
    fno_df.at[i,'STRIKE'] = strike
    i = i+1
    
rows = np.arange(0,len(All_Strikes)+1)

print(type(rows))    

strike_list = dict(zip(All_Token,All_Strikes))

row_list = dict(zip(All_Token,All_Strikes))

"""
    









 
 







