import logging
import requests

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
print("Opening Range Breakout Code for BANKNIFTY")
symbol = "14350850"
symboltxt = "BANKNIFTY20APRFUT"
#sameer key
#api_key = '7s6e8cjvyjw4bgvo'
#api_secret = 'b8yem58dwlgih4s1u2ryd7ynkj39hxck'
api_key = 'xyipj2fx4akxggck'
api_secret = 'ehzimap1bmhdbmrg2jbysn6jddxmmfr4'
conn = KiteConnect(api_key=api_key)
accToken = 'i2E2K37aqYaBuWBNcC9uDT23Pbq14hYr'
conn.set_access_token(accToken)
high = 0
low = 0
highlowTime = datetime.now()
highlowTime1 = highlowTime.replace(hour=9, minute=29, second=56)
highlowTime2 = highlowTime.replace(hour=9, minute=29,second=59)

print("Get Opening Range High Low")
#url = "https://api.kite.trade/instruments/historical/" + symbol + "/15minute?from=2020-03-24+09:15:00&to=2020-03-24+09:29:59"
dateStr = str(highlowTime.year) + "-" + str("{0:02}".format(highlowTime.month)) + "-" + str(
    "{0:02}".format(highlowTime.day))
url = "https://api.kite.trade/instruments/historical/" + symbol + "/15minute?from=" + dateStr + "+09:15:00&to=" + dateStr + "+09:29:58"
headers = {"X-Kite-Version": "3", "Authorization": "token " + api_key + ":" + accToken + ""}
print("url:", url)
response = requests.get(url=url, headers=headers)
resdata = response.json()
print(resdata)
high = resdata['data']['candles'][0][2]
low = resdata['data']['candles'][0][3]
#high = 18350
#low = 18000
print("Opening Candle HighLow: ", high, low)

kiteTicker = KiteTicker('xyipj2fx4akxggck', accToken)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    #logging.debug("Ticks: {}".format(ticks))
    #lastPrice = ticks[0]['last_price']
    #logging.debug(int(lastPrice))
    now = datetime.now()

    #if (now > highlowTime1) and (now < highlowTime2) :
    #    response = requests.get(url=url, headers=headers)
    #    resdata = response.json()
    #    print(resdata)
    #    high = resdata['data']['candles'][0][2]
    #    low = resdata['data']['candles'][0][3]
    #    print("HighLow: ", high, low)

    triggerTime = datetime.now()
    triggerTime = triggerTime.replace(hour=9, minute=39, second=59)
    if now > triggerTime:
        if (now.minute == 59 or now.minute == 14 or now.minute == 29 or now.minute == 44) and (now.second == 55):
            print("inside time condition: time now: ", now, now.hour, now.minute, now.second)
            logging.debug("Ticks: {}".format(ticks))
            lastPrice = ticks[0]['last_price']
            logging.debug(int(lastPrice))
            # Get last candle
            lCSTime = datetime.now() - timedelta(minutes=15) + timedelta(seconds=6)
            lCETime = datetime.now() - timedelta(seconds=1)
            toStr = str(lCETime.year) + "-" + str("{0:02}".format(lCETime.month)) + "-" + str(
                "{0:02}".format(lCETime.day)) + "+" + str("{0:02}".format(lCETime.hour)) + ":" + str(
                "{0:02}".format(lCETime.minute)) + ":" + str("{0:02}".format(lCETime.second))
            fromStr = str(lCSTime.year) + "-" + str("{0:02}".format(lCSTime.month)) + "-" + str(
                "{0:02}".format(lCSTime.day)) + "+" + str("{0:02}".format(lCSTime.hour)) + ":" + str(
                "{0:02}".format(lCSTime.minute)) + ":" + str("{0:02}".format(lCSTime.second))
            newurl = "https://api.kite.trade/instruments/historical/" + symbol + "/15minute?from=" + fromStr + "&to=" + toStr + ""
            print(newurl)
            print("Header:", headers)
            #url = "https://api.kite.trade/instruments/historical/" + symbol + "/10minute?from=2020-03-20+09:15:00&to=2020-03-20+09:29:59"
            prevResp = requests.get(url=newurl, headers=headers)
            preResdata = prevResp.json()
            print(preResdata)
            prevOpen = preResdata['data']['candles'][0][1]
            prevHigh = preResdata['data']['candles'][0][2]
            prevLow = preResdata['data']['candles'][0][3]
            prevClose = preResdata['data']['candles'][0][4]
            print("Previous Candle HighLow: ", prevHigh, prevLow)
            if (prevOpen < high ) and (lastPrice > high):
                print("Long Breakout")
                #order_long = conn.place_order(tradingsymbol=symbol, quantity=1, exchange=conn.EXCHANGE_NFO,
                #   order_type=conn.ORDER_TYPE_MARKET,
                #   TRANSACTION_TYPE=CONN.TRANSACTION_TYPE_BUY, product=conn.PRODUCT_MIS,
                #   variety=conn.VARIETY_REGULAR)
                order_long = conn.place_order(tradingsymbol=symboltxt, quantity=20, exchange=conn.EXCHANGE_NFO,
                                              order_type=conn.ORDER_TYPE_LIMIT,
                                              transaction_type=conn.TRANSACTION_TYPE_BUY, product=conn.PRODUCT_MIS,
                                              variety=conn.VARIETY_REGULAR, price=lastPrice - 5, stoploss=75,
                                              trailing_stoploss=25, squareoff=125)
                print(order_long)
            elif (prevOpen > low ) and (lastPrice < low):
                print("Short Breakout")
                #order_short = conn.place_order(tradingsymbol=symbol, quantity=1, exchange=conn.EXCHANGE_NFO,
                #   order_type=conn.ORDER_TYPE_MARKET,
                #   transaction_type=conn.TRANSACTION_TYPE_SELL, product=conn.PRODUCT_MIS,
                #   variety=conn.VARIETY_REGULAR)
                order_short = conn.place_order(tradingsymbol=symboltxt, quantity=20, exchange=conn.EXCHANGE_NFO,
                                              order_type=conn.ORDER_TYPE_LIMIT,
                                              transaction_type=conn.TRANSACTION_TYPE_SELL, product=conn.PRODUCT_MIS,
                                              variety=conn.VARIETY_REGULAR, price=lastPrice + 5, stoploss=75,
                                              trailing_stoploss=25, squareoff=125)
                print(order_short)
            else:
                print("No Breakout")
            #print(conn.orders())
            #print(conn.holdings())
            print(conn.positions())

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE & ACC here).
    # ws.subscribe([738561, 5633])
    # Subscribe to a list of instrument_tokens (BANKNIFTY20MARFUT here).
    ws.subscribe([14350850])
    ws.set_mode(ws.MODE_FULL, [14350850])

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

print("Run loop")
kiteTicker.on_ticks = on_ticks
kiteTicker.on_connect = on_connect
kiteTicker.on_close = on_close
kiteTicker.connect()
