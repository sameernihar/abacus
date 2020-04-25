import logging
import math
import schedule
from datetime import datetime, timedelta
from AccessInitiator import AccessInitiator
from kiteconnect import KiteConnect
from DataRetriever import DataRetriever
logging.basicConfig(level=logging.DEBUG)


class TradeManager:
    def __init__(self, symboltext,symbolcode):
        self.symboltext = symboltext
        self.timeframe = ""
        self.exchange = ""
        self.ordertype = ""
        self.transaction = ""
        self.product = ""
        self.variety = ""
        self.entryprice = 0.0
        self.SL = 0.0
        self.TSL = ""
        self.target = ""
        self.manageTSL = False
        self.quantity = ""
        self.CurrentOpen = ""
        self.CurrentHigh = ""
        self.CurrentLow = ""
        self.CurrentClose = ""
        self.breakevenpoints = 0.0
        self.managetrade_jobid = ""
        self.dr = DataRetriever(symbolcode)

    # ai, exchange, ordertype, transaction, product, variety, price, SL, TSL, Target, TSLOrder
    def placeorder(self, ai, exchange, ordertype, transaction, product, variety, quantity, price, SL, TSL, Target, breakevenpoints, manageTSL):
        self.exchange = exchange
        self.ordertype = ordertype
        self.transaction = transaction
        self.product = product
        self.variety = variety
        self.entryprice = price
        self.quantity = quantity
        self.SL = SL
        self.TSL = TSL
        self.target = Target
        self.manageTSL = manageTSL
        self.breakevenpoints = breakevenpoints

        order_long = ai.conn.place_order(tradingsymbol=self.symboltext, quantity=self.quantity, exchange=self.exchange,
                                         order_type=self.ordertype, transaction_type=self.transaction,
                                         product=self.product, variety=self.variety, price=self.entryprice,
                                         stoploss=self.SL, trailing_stoploss=self.TSL, squareoff=self.target)
        print(order_long)
        self.managetrade_jobid = schedule.every(1).minutes.do(self.managetrade, ai=ai)


    def managetrade(self, ai):

        if datetime.now().hour == 15 and datetime.now().minute == 15:
            schedule.cancel_job(self.managetrade_jobid)

        #calculate to time
        thour = datetime.now().hour; tminute = datetime.now().minute - 1; tseconds = 59
        if tminute == -1:
            tminute = 59; thour = thour - 1

        #calculate from time
        fhour = datetime.now().hour; fminute = datetime.now().minute - 1; fseconds = 0
        if fminute == -1:
            fminute = 59; fhour = fhour - 1

        dr.setFromDateTime(datetime.now().date(), fhour, fminute, fseconds)
        dr.setToDateTime(datetime.now().date(),thour,tminute,tseconds)
        dr.setTimeframe("1minute")

        responseData = dr.getHistoricalData(ai)

        self.CurrentOpen = responseData['data']['candles'][0][1]
        self.CurrentHigh = responseData['data']['candles'][0][2]
        self.CurrentLow = responseData['data']['candles'][0][3]
        self.CurrentClose = responseData['data']['candles'][0][4]

        if ((self.CurrentClose  - self.entryprice) >= self.breakevenpoints) and (self.transaction == ai.conn.TRANSACTION_TYPE_BUY) :
            self.SL = math.ceil(self.entryprice)

        if ((self.entryprice - self.CurrentClose) >= self.breakevenpoints) and (self.transaction == ai.conn.TRANSACTION_TYPE_SELL) :
            self.SL = math.floor(self.entryprice)

        if (self.transaction == ai.conn.TRANSACTION_TYPE_BUY) and (self.CurrentClose <= self.SL):
            order_long = ai.conn.place_order(tradingsymbol=self.symboltext, quantity=self.quantity,
                                             exchange=self.exchange,
                                             order_type=self.ordertype, transaction_type=ai.conn.TRANSACTION_TYPE_SELL,
                                             product=self.product, variety=self.variety, price=self.SL)
            schedule.cancel_job(self.managetrade_jobid)


        if (self.transaction == ai.conn.TRANSACTION_TYPE_SELL) and (self.CurrentClose >= self.SL):
            order_long = ai.conn.place_order(tradingsymbol=self.symboltext, quantity=self.quantity,
                                             exchange=self.exchange, order_type=self.ordertype,
                                             transaction_type=ai.conn.TRANSACTION_TYPE_BUY, product=self.product,
                                             variety=self.variety, price=self.SL)
            schedule.cancel_job(self.managetrade_jobid)

