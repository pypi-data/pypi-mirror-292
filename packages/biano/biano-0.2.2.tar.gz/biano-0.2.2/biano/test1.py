#coding=utf-8

from matplotlib import pyplot as plt

import numpy as np
import math
from buildz import pyz
pyz.add(__file__)
from biano import sound1 as sound
# mn,mx=None,None
# for i in range(0, 100):
#     y = sound.f(sound.fn(i), i)
#     if mn is None:
#         mn = min(y)
#     else:
#         mn = min(min(y), mn)
#     if mx is None:
#         mx = max(y)
#     else:
#         mx = max(max(y), mx)
#     print(max(y), min(y))

# pass
# print(mx, mn)
# exit()
i = 39
y = sound.f(sound.fn(i), i)
#y=y[:len(y)>>1]
x = np.array(list(range(0, len(y))),dtype=np.float32)
x = x*(1/sound.fps)#/len(x))
print(max(y), min(y))
plt.plot(x,y)
plt.show()