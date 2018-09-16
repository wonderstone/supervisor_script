# -*- coding: utf-8 -*-
# @Time    : 2018/9/15 14:14
# @Author  : wonderstone
# @FileName: std_script.py
# @Software: PyCharm
# @Ref     :



import json, requests, datetime, os, time
import configparser
from urllib import request
from json import load
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import *
import re

def check_ip(ip):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

def send_msg(url, msg, chan='IPaddr'):
    try:
        info = {
            'text': msg,
            'channel': chan,
        }
        headers = {'content-type': 'application/json'}
        req = requests.post(url, data=json.dumps(info), headers=headers)
        print(req)
    except Exception as e:
        print('Send bearychat Msg Error e: ', e)
        return False
    return True


class CheckIP:
    def __init__(self, url, chan, my_last_IP=None):
        self.url = url
        self.chan = chan
        self.my_last_IP = my_last_IP
        self.state = None

    def get_IP(self):
        try:
            my_IP = request.urlopen('http://ip.42.pl/raw').read()
            if check_ip(str(my_IP, encoding='utf-8')):
                pass
            else:
                raise TypeError('NOT IP')
        except:
            try:
                my_IP = load(request.urlopen('http://jsonip.com'))['ip']
                if check_ip(str(my_IP, encoding='utf-8')):
                    pass
                else:
                    raise TypeError('NOT IP')
            except:
                try:
                    my_IP = load(request.urlopen('http://httpbin.org/ip'))['origin']
                    if check_ip(str(my_IP, encoding='utf-8')):
                        pass
                    else:
                        raise TypeError('NOT IP')
                except:
                    try:
                        my_IP = load(request.urlopen('https://api.ipify.org/?format=json'))['ip']
                        if check_ip(str(my_IP, encoding='utf-8')):
                            pass
                        else:
                            raise TypeError('NOT IP')
                    except:
                        my_IP = "Sorry! All sites are down!!"

        if type(my_IP) is bytes:
            self.my_IP = str(my_IP, encoding='utf-8')
        else:
            self.my_IP = my_IP

    def chk_IP_job(self):
        self.get_IP()
        if self.my_last_IP is None:
            self.my_last_IP = self.my_IP
            self.state = send_msg(url=self.url, msg=self.my_IP, chan=self.chan)
        else:
            if self.my_last_IP != self.my_IP:
                self.state = send_msg(url=self.url, msg=self.my_IP, chan=self.chan)
                self.my_last_IP = self.my_IP
            else:
                pass

    def my_listener(self, event):
        if event.exception:
            msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Check IP function Crashed !'
            print(msg)
            print("The state for sending the message is " + str(self.state))
        else:
            msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Job Done !'
            print(msg)
            print("The state for sending the message is " + str(self.state))

    def job_interval(self,minutes =10):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.chk_IP_job, 'interval', minutes=minutes)
        scheduler.add_listener(self.my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(5)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    url = config['BearyChat']['URL']
    chan = config['BearyChat']['CHAN']

    chk_IP = CheckIP(url=url, chan=chan)
    chk_IP.job_interval()
