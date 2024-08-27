#coding=utf-8

import pynput
from pynput.keyboard import Listener, Key
from biano import sound1 as sound


ctls = list("1234567890")
c2base = {}
c2i = {}
for c in ctls[:len(ctls)>>1]:
    c2base[c] = 0
    c2i[c] = int(c)-1

pass

for c in ctls[len(ctls)>>1:]:
    c2base[c] = 1
    c2i[c] = int(c)-6
    if c2i[c] <0:
        c2i[c] = 4

pass

lefts = "qwertasdfzxc"
rights = "yuiophjklnm,"
nlefts = {k:i for k,i in zip(lefts, range(len(lefts)))}
nrights = {k:i for k,i in zip(rights, range(len(rights)))}
maps = {}
k2base = {}
for k in nlefts:
    maps[k] = nlefts[k]
    k2base[k] = 0
for k in nrights:
    maps[k] = nrights[k]
    k2base[k] = 1

pass
bases = [40,40]
moves = [0,0]
mvs = "-="
pressed = set()
pressed = set()
c='3'
bases[c2base[c]] = c2i[c]*len(lefts)+16
c='9'
bases[c2base[c]] = c2i[c]*len(lefts)+16
def press(key):
    global moves
    if hasattr(key, "char"):
        c = key.char
        if c in maps:
            if c in pressed:
                return
            vc = maps[c] + bases[k2base[c]]+moves[k2base[c]]
            if vc <= 0:
                return
            if vc >= 89:
                return
            sound.sd.play(vc)
            #print(vc)
            pressed.add(c)
            #print(vc)
        elif c in mvs:
            if c == "-":
                moves = [0,0]
            else:
                moves = [-24, 24]
        elif c in ctls:
            bases[c2base[c]] = c2i[c]*len(lefts)+16
        # elif c in maps:
        #     if c in pressed:
        #         return
        #     vc = maps[c] + bases[k2base[c]]+moves[k2base[c]]
        #     if vc <= 0:
        #         return
        #     if vc >= 89:
        #         return
        #     pressed.add(c)
        #     #print(vc)
        #     sound.sd.play(vc)
    global lst
    if key == Key.esc:
        lst.stop()
        sound.sd.close()
        sound.release()

pass

def release(key):
    if hasattr(key, "char"):
        c = key.char
        if c not in maps:
            return
        if c in pressed:
            pressed.remove(c)

pass
lst = None
def run():
    global lst
    print("按键: 左手: qwertasdfzxc 右手: yuiophjklnm,")
    print("修改音调: 左手按键: 1,2,3,4,5 右手按键: 6,7,8,9,0")
    print("修改模式: 按-或=")
    print("按esc退出")
    print("press to sound: left: qwertasdfzxc right: yuiophjklnm,")
    print("change tone: left: press 1,2,3,4,5 right: press 6,7,8,9,0")
    print("change mode: press - or =")
    print("press esc to exit")
    with Listener(on_press=press, on_release=release) as lst:
        lst.join()

pass
if __name__=="__main__":
    run()

pass
"""
python keys.py
"""