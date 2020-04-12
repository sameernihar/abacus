import logging
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
logging.basicConfig(level=logging.DEBUG)
print("Get Access Token")
api_key = 'xyipj2fx4akxggck'
api_secret = 'ehzimap1bmhdbmrg2jbysn6jddxmmfr4'
conn=KiteConnect(api_key=api_key)

request_token="CizWCsegq3i7cqhlhR2yAR5OriYGN8TT"
data=conn.generate_session(request_token,api_secret='ehzimap1bmhdbmrg2jbysn6jddxmmfr4')
print(data["access_token"])

