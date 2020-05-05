import logging
import json
import math
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
from datetime import datetime, timedelta
from AccessInitiator import AccessInitiator
from DataRetriever import DataRetriever
from TradeManager import TradeManager

logging.basicConfig(level=logging.DEBUG)

class ORBStrategy:
    def __init__(self, symboltxt, symbolcode):
        self.symboltxt = symboltxt
        self.symbolcode = symbolcode
        self.OpeningHigh = 0.0
        self.OpeningLow = 0.0
        self.CurrentOpen = 0.0
        self.CurrentHigh = 0.0
        self.CurrentLow = 0.0
        self.CurrentClose = 0.0
        self.breakevenpercent = 0.0
        self.stoplosspercent = 0.0

        f = open("ORB.json", "r"); jsonconfig = f.read(); f.close()
        brokerconfig = json.loads(jsonconfig)
        self.breakevenpercent = brokerconfig['stoploss percent']
        self.stoplosspercent = brokerconfig['breakeven percent']
        self.quantity = brokerconfig['quantity']
        self.breakevenpercent = float(self.breakevenpercent)
        self.stoplosspercent = float(self.stoplosspercent)
        self.quantity = int(self.quantity)

    def setOHOL(self, ai):
        dr = DataRetriever(self.symbolcode)
        dr.setFromDateTime(datetime.now().date(), 9, 15, 0)
        dr.setToDateTime(datetime.now().date(), 9, 29, 58)
        dr.setTimeframe("15minute")
        responsedata = dr.getHistoricalData(ai)
        print("responseData :", responsedata)
        self.OpeningHigh = responsedata['data']['candles'][0][2]
        self.OpeningLow = responsedata['data']['candles'][0][3]
        print("Opening Candle High :", self.OpeningHigh, "Opening Candle Low :", self.OpeningLow)

    def runstrategy(self, ai):
        print("runstrategy called....")
        #calculate to time
        thour = datetime.now().hour; tminute = datetime.now().minute - 1; tseconds = 59
        if tminute == -1:
            tminute = 59; thour = thour - 1

        #calculate from time
        fhour = datetime.now().hour; fminute = datetime.now().minute - 15; fseconds = 0
        if fminute == -15:
            fminute = 45; fhour = fhour - 1

        dr = DataRetriever(self.symbolcode)
        dr.setFromDateTime(datetime.now().date(), fhour, fminute, fseconds)
        dr.setToDateTime(datetime.now().date(),thour,tminute,tseconds)
        dr.setTimeframe("15minute")
        responsedata = dr.getHistoricalData(ai)

        self.CurrentOpen = responsedata['data']['candles'][0][1]
        self.CurrentHigh = responsedata['data']['candles'][0][2]
        self.CurrentLow = responsedata['data']['candles'][0][3]
        self.CurrentClose = responsedata['data']['candles'][0][4]

        if (self.CurrentClose > self.OpeningHigh) and (self.CurrentOpen < self.OpeningHigh):
            print("Bingo!, We are in Opening Range Upside Breakout, take long trade!")

            tm = TradeManager(self.symboltxt,self.symbolcode)

            # ai, exchange, ordertype, transaction, product, variety, price, SL, TSL, Target, TSLOrder
            breakevenpoints = math.floor(self.CurrentClose*(self.breakevenpercent/100))
            stoplosspoints = math.floor(self.CurrentClose*(self.stoplosspercent/100))

            tm.placeorder(ai, exchange=ai.conn.EXCHANGE_NFO, ordertype=ai.conn.ORDER_TYPE_MARKET,
                          transaction=ai.conn.TRANSACTION_TYPE_BUY, product=ai.conn.PRODUCT_MIS,
                          variety=ai.conn.VARIETY_REGULAR, quantity=self.quantity, price=math.floor(self.CurrentClose), SL=stoplosspoints, TSL=25,
                            Target=125, breakevenpoints=breakevenpoints, manageTSL=False)

        if (self.CurrentClose < self.OpeningLow) and (self.CurrentOpen > self.OpeningLow):
            print("Bingo!, We are in Opening Range Downside Breakout, take short trade!")

            tm = TradeManager(self.symboltxt,self.symbolcode)

            # ai, exchange, ordertype, transaction, product, variety, price, SL, TSL, Target, TSLOrder
            breakevenpoints = math.ceil(self.CurrentClose * (self.breakevenpercent / 100))
            stoplosspoints = math.ceil(self.CurrentClose * (self.stoplosspercent / 100))

            tm.placeorder(ai, exchange=ai.conn.EXCHANGE_NFO, ordertype=ai.conn.ORDER_TYPE_MARKET,
                          transaction=ai.conn.TRANSACTION_TYPE_SELL, product=ai.conn.PRODUCT_MIS,
                          variety=ai.conn.VARIETY_REGULAR, quantity=self.quantity, price=self.CurrentClose, SL=stoplosspoints, TSL=25,
                          Target=125, breakevenpoints=breakevenpoints, manageTSL=False)

