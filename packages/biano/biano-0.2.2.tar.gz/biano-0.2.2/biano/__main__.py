#coding=utf-8
import sys
from buildz import pyz
pyz.add(__file__)
#sys.path.append(r"D:\root\gits\biano\biano")
from biano import keys
if __name__=="__main__":
    keys.run()

pass
