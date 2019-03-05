import speedtest
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
import time
import sqlite3


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


if __name__ == '__main__':
    database()
    scheduler = BackgroundScheduler()
    scheduler.add_job(speedlogger, 'interval', seconds=60)
    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
