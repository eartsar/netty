from telnetlib import Telnet
import sys
from threading import *


class ReaderThread(Thread):

    __slots__ = ("telnet", "callback", "acc", "uid")

    def __init__(self, telnet, callback=None, uid=None):
        self.uid = uid
        self.telnet = telnet
        self.acc = ""
        Thread.__init__(self)
        self.callback = callback

    def run(self):
        done = False
        while not done:
            try:
                s = self.telnet.read_until("\n")
                s = s.strip()
                if s == '':
                    continue
                self.callback(s, self.uid)
            except:
                done = True


class Client():

    __slots__ = ("reader", "telnet", "uid")

    def __init__(self, callback=None, uid=None):
        self.uid = uid
        host = 'localhost'
        port = 8080
        self.telnet = Telnet()
        self.telnet.open(host, port)
        self.reader = ReaderThread(self.telnet, callback, uid)
        self.reader.start()

    def send_input(self, line):
        self.telnet.write(line+'\n')
