#coding=utf-8

import sys
from buildz import pyz
import numpy as np
import threading as th
import time
sys.path.append(r"D:\downloads\codes\python\pydub-0.25.1")
pyz.add(__file__)

from pydub import AudioSegment
audio_file=r"D:\rootz\data\music\稻香guita.mp3"
audio = AudioSegment.from_file(audio_file)
x = audio.get_array_of_samples()
nx = np.array(x)

from biano import sound
fps = len(nx)/audio.duration_seconds
import threading as th
fps = int(fps)
nbyte = 2
def write(dt):
    lk = th.Lock()
    #s.write(dt.tobytes())
    #return
    n=100
    sz = len(nx)//n
    for i in range(n):
        with lk:
            dt = nx[i*sz:i*sz+sz]
            dt = dt*0.1
            dt=dt*1.0
            dt = dt.astype(sound.ndtype)
            s.write(nx[i*sz:i*sz+sz].tobytes())
            print(i*sz, i*sz+sz)
    #s.write(nx)

pass
s = sound.p.open(format=sound.p.get_format_from_width(nbyte), channels=1, rate=fps, output=True)
t = th.Thread(target=write, args = (nx,),daemon=True)
t.start()
#s.write(nx)
try:
    while t.is_alive():
        time.sleep(1.0)
finally:
    sound.close(s)

pass
