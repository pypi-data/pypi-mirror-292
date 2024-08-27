#coding=utf-8
import pyaudio
import numpy as np
import math
from buildz.tools import *
import threading as th
import time
class Stream(Base):
    def run(self):
        self.running = True
        self.loop()
    def start(self):
        t = th.Thread(target=self.run,daemon=True)
        t.start()
        self.t = t
    def stop(self):
        self.running=False
    def init(self, output, nrange ,num, size, ndtype, left=1, r_new = 1.0, r_old = 0.7):
        self.r_new = r_new
        self.ndtype = ndtype
        self.r_old = r_old
        self.win = size
        self.range = nrange
        self.num = num
        self.left = left
        self.size = size
        self.total = size*num
        self.data = np.zeros(size*num, dtype = np.float32)
        self.out_data = None
        self.lock = th.Lock()
        self.running = False
        self.output = output
        self.offset = 0
        self.lock_offset = -1
    def loop(self):
        while self.running:
            while self.running:
                with self.lock:
                    if self.offset==self.lock_offset:
                        time.sleep(0.001)
                        continue
                    dt = self.data[self.offset*self.size:self.offset*self.size+self.size]
                    tmp=(dt*self.range).astype(self.ndtype)
                    dt[:]=0
                    self.offset=(self.offset+1)%self.num
                    break
            self.output(tmp.tobytes())
    def add(self, data):
        with self.lock:
            off = (self.offset+self.left)%self.num
            self.lock_offset = off
        l = data.size
        l1 = min((self.num-off)*self.size, l)
        tmp = self.data[off*self.size:off*self.size+l1]
        data1=data
        if l1!=l:
            data1=data[:l1]
        tmp[:] = np.maximum(np.minimum(1*(tmp*self.r_old+data1*self.r_new),1.0), -1.0)
        #tmp[:] = np.maximum(np.minimum(tmp, 1.0), -1.0)
        if l1!=l:
            left = l-l1
            tmp = self.data[:left]
            data1 = data[l1:]
            tmp[:] = np.maximum(np.minimum(1*(tmp*self.r_old+data1*self.r_new),1.0), -1.0)
            #tmp[:] = np.maximum(np.minimum(tmp, 1.0), -1.0)
        with self.lock:
            self.lock_offset=-1

pass

