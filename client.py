from telnetlib import Telnet
import sys
from threading import *


class ReaderThread(Thread):

    __slots__ = ("telnet", "callback", "acc", "client_ip")

    def __init__(self, telnet, callback=None, client_ip=None):
        self.client_ip = client_ip
        self.telnet = telnet
        self.acc = ""
        Thread.__init__(self)
        self.callback = callback

    def run(self):
        i = 0
        done = False
        while not done:
            try:
                s = self.telnet.read_very_eager()
                if s == '':
                    continue
                self.callback(s, self.client_ip)
            except:
                done = True


class Client():

    __slots__ = ("reader", "telnet", "client_ip")

    def __init__(self, callback=None, client_ip=None):
        self.client_ip = client_ip
        host = 'localhost'
        port = 8888
        self.telnet = Telnet()
        self.telnet.open(host, port)
        self.reader = ReaderThread(self.telnet, callback, client_ip)
        self.reader.start()

    def send_input(self, line):
        self.telnet.write(line+'\n')
