#coding=utf-8

import pyaudio
import numpy as np
import math
from . import cache
fps = 4096*10*8
p = pyaudio.PyAudio()
nbyte = 2
ndtype = np.int16
nmax = (1<<(nbyte<<3))-1

nrange = nmax/2
nrange = (nmax+1)/2
def fn(n):
    """
        乐谱音符转频率
        C1: n=4 fn(4)=32.703
        C1#: n=5
        D1: n=6
    """
    return 27.5*(2**(1/12))**(n-1)

pass

def f1(rate, n, sec = 1.0, msound = 1.0):
    """
    rate: 频率
    n: 乐谱音符（1234567）
    sec: 声波发音时间，单位秒
    msound: 全局音量大小
    """
    global fps #每秒取样数
    size = int(fps * sec)
    prev = 0#int(size*0.02)
    data = np.zeros(prev+size+int(size*0.7), dtype = np.float32)
    # 频率越高，声音越小
    #sound = 1-(mid-n)*(mid-n)/(120*120)
    sound = (100-n)**2/100**2
    #if n > mid:
    #    sound = -sound
    offset = random.random()*math.pi
    for i in range(len(data)):
        s0 = i/fps
        w1 = (s0**0.25)
        w2 = math.exp(-1*(s0**2)/(10*(0.2**2)))
        y = w1*math.sin(offset+2*math.pi*s0*rate)*w2
        #y = math.exp(-1/(2*0.2*0.2)*s0*s0)
        #y=math.exp(-1*(s0**2)/(11*(0.2**2)))
        #y=w1*w2
        y*=(400/rate)**0.5
        y*=0.5
        #y*=nrange
        y*=msound
        data[prev+i] = y
    return data#rst

pass
mid = 50
import random
def f2(rate, n, sec = 1.0, msound = 1.0, index=0):
    """
    rate: 频率
    n: 乐谱音符（1234567）
    sec: 声波发音时间，单位秒
    msound: 全局音量大小
    """
    global fps #每秒取样数
    size = int(fps * sec)
    prev = 0#int(size*0.02)
    data = np.zeros(prev+size+int(size*0.5), dtype = np.float32)
    # 频率越高，声音越小
    #sound = 1-(mid-n)*(mid-n)/(120*120)
    sound = (100-n)**2/100**2
    #if n > mid:
    #    sound = -sound
    offset = index*math.pi*0.03*random.random()*0
    #print(size)
    for i in range(size):
        #s0 = rate*i
        #y = (s0**0.25)*math.sin(2*math.pi*s0/fps)*math.exp(-1/(2*0.2*0.2)*s0*s0)
        x0 = i*2*math.pi*rate/fps
        #x0 += (random.random()-0.5)*0.1
        #sound = math.cos(abs(mid-n)/50*math.pi*0.5)
        y = math.sin(x0+offset)*(0.1*sound+sound*0.9)
        #y *=(1+(random.random()-0.5)*0.1)
        # 音量从1到0
        r = (size-i)/size
        y *= r*msound
        #y *= math.cos(i*math.pi/size)*0.5+0.5
        #y *= nrange
        y = max(-nrange+1,min(nrange-1, y))
        data[prev+i] = y
    return data#rst

pass
f=f2
import random
class CacheFc:
    def __init__(self,n=10):
        #self.cache = {}
        self.index=0
        self.n = n
        self.caches = []
        for i in range(n):
            self.caches.append({})
    def __call__(self, rate, n):
        i = self.index
        self.index=(self.index+1)%self.n
        cache = self.caches[0]
        if rate not in cache:
            cache[rate] = f(rate, n, 1.0)
        return cache[rate]

pass
def create():
    return p.open(format=p.get_format_from_width(nbyte), channels=1, rate=fps, output=True)

pass

def close(stream):
    stream.stop_stream()
    stream.close()

pass
import threading


class Sound:
    def __init__(self):
        self.fc = CacheFc()
        self.zero = create()
        #print(fps)
        self.stream = cache.Stream(self.zero.write, nrange,100, int(fps*0.05), ndtype, left=1)
        self.stream.start()
        # self.frees = [create() for i in range(20)]
        # self.zero = create() #一直播放着空旋律，避免噪音
        # self.index = 0
        # self.lock = threading.Lock()
        # self.running = True
        # th = threading.Thread(target = self.run_zero)
        # th.setDaemon(True)
        # th.start()
    def play(self, n):
        if not self.stream.running:
            return
        rate = fn(n)
        data = self.fc(rate, n)
        self.stream.add(data)
    def close(self):
        import time
        self.stream.stop()
        time.sleep(1.0)
        close(self.zero)

pass
sd = Sound()
def release():
    p.terminate()

pass
