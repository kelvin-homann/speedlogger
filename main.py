from threading import Thread
import datetime
import speedtest
import urllib.request
import time
import sqlite3
import re
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError


# backing up the database to dropbox
def backup():
    localfile = './speedloggerdb.db'
    destination = '/speedloggerdb.db'
    token = 'YOUR TOKEN'  # Add your personal Dropbox Access Token as String
    dbx = dropbox.Dropbox(token)  # Connecting to dropbox folder
    with open('./speedloggerdb.db', 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + localfile + " to Dropbox")
        try:
            dbx.files_upload(f.read(), destination, mode=WriteMode('overwrite'))
        except ApiError as err:
            pass


# fetches the result number of the last entry and adds 1
def getnewrnr(cursor):
    cursor.execute("SELECT rnr FROM results ORDER BY rnr DESC LIMIT 1")
    return cursor.fetchone()[0] + 1


# corrects the time format return from datetime for regex
def correctdate(hours, minutes):
    if minutes <= 9:
        return str(hours) + ":0" + str(minutes)
    else:
        return str(hours) + ":" + str(minutes)


# fixes the datetime format to a readable format
def get_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%y')


def speedlogger():
    print("started speedlogger")
    conn = sqlite3.connect("speedloggerdb.db")  # establishing database connection
    c = conn.cursor()
    while 1:  # infite loop checks the current time
        currenttime = correctdate(datetime.datetime.now().hour, datetime.datetime.now().minute)  # Format 00:00
        currentday = get_date(str(datetime.datetime.now().date()))
        if re.match("^([01]?[0-9]|2[0-3]):[^1-5][^1-9]$", currenttime):  # matches only full hours
            try:
                print("Running speedtest")
                servers = []
                speedlog = speedtest.Speedtest()
                speedlog.get_servers(servers)
                speedlog.get_best_server()
                speedlog.download()
                speedlog.upload(pre_allocate=False)

                print("Current Date: %s %s", str(currentday), str(currenttime))
                print("Download: " + str(round(speedlog.results.download / (1000*1000), 2)) + " Mbit/s")  # fixed byte to megabyte output
                print("Upload: " + str(round(speedlog.results.upload / (1000*1000), 2)) + " Mbit/s")  # fixed byte to megabyte output
                print("Ping: " + str(speedlog.results.ping))
                print("Timestamp: " + str(speedlog.results.timestamp))
                print("Bytes received: " + str(speedlog.results.bytes_received))
                print("Bytes sent: " + str(speedlog.results.bytes_sent))
                print("Link: " + str(speedlog.results.share()))

                download = float(round(speedlog.results.download / (1000*1000), 2))  # fixed byte to megabyte output
                upload = float(round(speedlog.results.upload / (1000*1000), 2))  # fixed byte to megabyte output
                ping = float(round(speedlog.results.ping))
                bytes_received = float(speedlog.results.bytes_received)
                bytes_sent = float(speedlog.results.bytes_sent)
                result_pic = str(speedlog.results.share())

                params = (getnewrnr(c), currentday, currenttime, download, upload, ping, bytes_received, bytes_sent, result_pic)
                c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", params)

                print("Finished speedtest and wrote into the database")

                # saving the changes
                conn.commit()
                # downloading the speedtest result as .png to display it in ui later on
                # urllib.request.urlretrieve(speedlog.results.share(), str("speedtestresult.png"))

                # backup of the database
                backup()

                time.sleep(60)  # To make sure it doesnt run twice in an hour

            except speedtest.SpeedtestException:
                print("speedtest failed")
                # adding empty entrys incase the internet doesnt work
                params = (getnewrnr(c), currentday, currenttime, 0, 0, 0, 0, 0, "")
                c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                print("Finished speedtest and wrote into the database")

                # saving the changes
                conn.commit()
                time.sleep(60)  # to make sure it doesnt run twice in an hour


if __name__ == '__main__':
    speedThread = Thread(target=speedlogger, args=()).start()  # speedtestthread

