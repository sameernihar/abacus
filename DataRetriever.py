import logging
import requests
from AccessInitiator import AccessInitiator
from kiteconnect import KiteConnect
logging.basicConfig(level=logging.DEBUG)


class DataRetriever:
    def __init__(self, symbolcode):
        self.from_date = ""
        self.from_time = ""
        self.from_hour = ""
        self.from_minute = ""
        self.from_second = ""
        self.to_date = ""
        self.to_time = ""
        self.to_hour = ""
        self.to_minute = ""
        self.to_second = ""
        self.symbolcode = symbolcode
        self.timeframe = ""

    def setFromDateTime(self, date, hour, minute, second):
        self.from_date = date
        self.from_hour = hour
        self.from_minute = minute
        self.from_second = second
        self.from_time = "+" + str("{0:02}".format(self.from_hour)) + ":" + str(
            "{0:02}".format(self.from_minute)) + ":" + str("{0:02}".format(self.from_second))
        print("self.from_time :", self.from_time)

    def setToDateTime(self, date, hour, minute, second):
        self.to_date = date
        self.to_hour = hour
        self.to_minute = minute
        self.to_second = second
        self.to_time = "+" + str("{0:02}".format(self.to_hour)) + ":" + str(
            "{0:02}".format(self.to_minute)) + ":" + str("{0:02}".format(self.to_second))
        print("self.to_time :", self.to_time)

    def setTimeframe(self, timeframe):
        print("Timeframe :", timeframe)
        self.timeframe = str(timeframe)
        print(" Self Timeframe :", self.timeframe)

    def getHistoricalData(self, ai):
        #url = "https://api.kite.trade/instruments/historical/" + symbol + "/15minute?from=2020-03-24+09:15:00&to=2020-03-24+09:29:59"
        #dateStr = str(highlowTime.year) + "-" + str("{0:02}".format(highlowTime.month)) + "-" + str(
        #"{0:02}".format(highlowTime.day))
        url = ai.dataurl + self.symbolcode + "/{timeframe1}?from=".format(timeframe1=self.timeframe) + str(self.from_date) + self.from_time + "&to=" + str(self.to_date) + self.to_time
        # ai.printallbrokervalues()
        headers = {"X-Kite-Version": "3", "Authorization": "token " + str(ai.apikey) + ":" + str(ai.accesstoken)}
        print("url:", url)
        print("headers:", headers)
        response = requests.get(url=url, headers=headers)
        print("response.status_code", response.status_code)
        print("response.raw response", response.raw)
        resdata = response.json()
        print(resdata)
        return resdata

