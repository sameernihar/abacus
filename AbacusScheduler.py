# Python Program to calculate the square root
# Note: change this value for a different result
import schedule
import time
import logging
from AccessInitiator import AccessInitiator
from ORBStrategy import ORBStrategy
from datetime import datetime, timedelta
from datetime import datetime, timedelta
logging.basicConfig(level=logging.ERROR)

ai = AccessInitiator()
orbs = ORBStrategy("BANKNIFTY20APRFUT","14350850")
jobid = ""

def start_ORB(ai, orbs):
    print("Called start ORB strategy", datetime.now())
    global jobid
    jobid = schedule.every(15).minutes.do(orbs.runstrategy, ai=ai)
    ai.refresh_conn()
    orbs.setOHOL(ai)

def start_trading(ai):
    print("Called start starttrading ", datetime.now())
    ai.getaccesstoken()
    ai.printallbrokervalues()

def stop_ORB():
    print("Called start ORB strategy", datetime.now())
    global jobid
    schedule.cancel_job(jobid)


# Task scheduling
schedule.every().day.at("09:00").do(start_trading, ai=ai)
schedule.every().day.at("09:30").do(start_ORB, ai=ai, orbs=orbs)
schedule.every().day.at("15:05").do(stop_ORB)

while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)

