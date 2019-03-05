from threading import Thread
import datetime
import speedtest
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
import time
import sqlite3
import re


def database():
    print("Connecting to Database")
    conn = sqlite3.connect("speedloggerdb.db")
    c = conn.cursor()

    # Create table
    #c.execute('''CREATE TABLE results
    #             (date text, time text, download float, upload float, ping float, bytes_received float, bytes_sent float, picture text)''')

    # commit the changes
    conn.commit()
    conn.close()


def speedlogger():
    while 1:
        now = str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute)  # Format 00:00
        print("Current Time: ", str(now))
        if re.match("^([01]?[0-9]|2[0-3]):[^1-9][^1-9]$", now):  # Matches only full hours
            print("Current Time: ", str(now))
            servers = []
            print("Running speedtest")
            s = speedtest.Speedtest()
            s.get_servers(servers)
            s.get_best_server()
            s.download()
            s.upload(pre_allocate=False)
            print("Download: " + str(s.results.download))
            print("Upload: " + str(s.results.upload))
            print("Ping: " + str(s.results.ping))
            print("Link: " + str(s.results.share()))
            print("Timestamp: " + str(s.results.timestamp))
            print("Bytes received: " + str(s.results.bytes_received))
            print("Bytes sent: " + str(s.results.bytes_sent))

            # Downloading the speedtest result as .png to display it in ui
            urllib.request.urlretrieve(s.results.share(), str("speedtestresult.png"))
            time.sleep(60)  # To make sure it doesnt run twice in an hour


if __name__ == '__main__':
    speedThread = Thread(target=speedlogger, args=()).start()
    database()
