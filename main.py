import speedtest
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
import time


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
    scheduler = BackgroundScheduler()
    scheduler.add_job(speedlogger, 'interval', seconds=60)
    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
