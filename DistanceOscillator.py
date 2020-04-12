import logging
import requests
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
print("Opening Range Breakout Code for BANKNIFTY")
symbol = "14350850"
symboltxt = "BANKNIFTY20APRFUT"
api_key = 'xyipj2fx4akxggck'
api_secret = 'ehzimap1bmhdbmrg2jbysn6jddxmmfr4'
conn = KiteConnect(api_key=api_key)
accToken = 'i2E2K37aqYaBuWBNcC9uDT23Pbq14hYr'
conn.set_access_token(accToken)
high = 0
low = 0
kiteTicker = KiteTicker('xyipj2fx4akxggck', accToken)

def on_ticks(ws, ticks):

    now = datetime.now()
    triggerTime = datetime.now()
    triggerTime = triggerTime.replace(hour=9, minute=39, second=59)
    if now > triggerTime:
        if (now.minute == 59 or now.minute == 14 or now.minute == 29 or now.minute == 44) and (now.second == 55):
            print("inside time condition: time now: ", now, now.hour, now.minute, now.second)
            lastPrice = ticks[0]['last_price']
            logging.debug(int(lastPrice))
            # Get historical data
            lCSTime = datetime.now() - timedelta(days=1)
            lCETime = datetime.now() - timedelta(seconds=1)
            fromStr = str(lCSTime.year) + "-" + str("{0:02}".format(lCSTime.month)) + "-" + str(
                "{0:02}".format(lCSTime.day))
            toStr = str(lCETime.year) + "-" + str("{0:02}".format(lCETime.month)) + "-" + str(
                "{0:02}".format(lCETime.day)) + "+" + str("{0:02}".format(lCETime.hour)) + ":" + str(
                "{0:02}".format(lCETime.minute)) + ":" + str("{0:02}".format(lCETime.second))
            newurl = "https://api.kite.trade/instruments/historical/" + symbol + "/15minute?from=" + fromStr + "+09:15:00&to=" + toStr + ""
            print(newurl)
            print("Header:", headers)
            response = requests.get(url=url, headers=headers)
            resdata = response.json()
            newJson = resdata['data']['candles']
            df = pd.DataFrame(newJson)
            highDf = df[2]
            lowDf = df[3]
            count = 20
            hSer = pd.Series()
            lSer = pd.Series()
            print(df)
            for i in df.index:
                if i < 20:
                    maxNum = max(highDf[0:i + 1])
                    minNum = min(lowDf[0:i + 1])
                    hSer._set_value(i, maxNum)
                    lSer._set_value(i, minNum)
                elif i >= 20:
                    maxNum = max(highDf[i - 19:i + 1])
                    minNum = min(lowDf[i - 19:i + 1])
                    hSer._set_value(i, maxNum)
                    lSer._set_value(i, minNum)

            df['highest'] = hSer
            df['lowest'] = lSer
            print(df)
            df['src'] = (df['highest'] + df['lowest']) / 2
            df['sum'] = (df[4] - df['src']) / df[4] * 100
            df['ema50'] = pd.Series.ewm(df['sum'], span=50).mean()
            df['ema12'] = pd.Series.ewm(df['ema50'], span=12).mean()
            prevFast = df['ema12'][-1]
            prevSlow = df['ema50'][-1]
            nowFast = df['ema12'][-2]
            nowSlow = df['ema50'][-2]
            print("Previous Candle FastSlow: ", prevFast, prevSlow)
            print("Current Candle FastSlow: ", nowFast, nowSlow)
            if (nowFast > nowSlow ) and (prevFast < prevSlow):
                print("Long Breakout")

            elif (nowFast < nowSlow ) and (prevFast > prevSlow):
                print("Short Breakout")
            else:
                print("No Breakout")


def on_connect(ws, response):
    # Callback on successful connect.
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
