#! /usr/bin/python
# Copyright (C) 2011 Michael Zuser mikezuser@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import dbus
import time
import os

# Disable camera-ui
os.system("/usr/sbin/dsmetool -k /usr/bin/camera-ui")

# Some functional programming
# Haskell style type-signatures 

# Cons Lists
class __nil__: 
    def __init__(self): 
        pass
    def __str__(self):
        return "Nil"

class __cons__: 
    def __init__(self, x, xs):
        self.head = x
        self.tail = xs
    def __str__(self):
        return "Cons " + str (self.head) + " (" + str (self.tail) + ")"

# Nil :: [a]
Nil = __nil__()
# Cons :: a -> [a] -> [a]
Cons = lambda x: lambda xs: __cons__(x, xs)

# Some basic functions

# pure :: a -> [a]
pure = lambda x: Cons (x) (Nil)

# foldr :: (b -> a -> a) -> a -> [b] -> a
foldr = lambda f: lambda z: lambda xs: \
    z if xs == Nil else f (xs.head) (foldr (f) (z) (xs.tail))

# comp :: (b -> c) -> (a -> b) -> a -> c
comp = lambda f: lambda g: lambda x: f (g (x))

# map :: (a -> b) -> [a] -> [b]
map = lambda f: foldr (comp (Cons) (f)) (Nil)

# append :: [a] -> [a] -> [a]
append = lambda xs: lambda ys: foldr (Cons) (ys) (xs)

# sum :: (Num a) => [a] -> a
sum = foldr (lambda x: lambda y: x+y) (0)

# fst :: (a, b) -> a
fst = lambda (x,y): x
# snd :: (a, b) -> b
snd = lambda (x,y): y

# lookup :: (Eq a) => a -> [(a, b)] -> b
# NOTE: horrible death if key is not in list
lookup = lambda key: lambda ps: \
    snd (ps.head) if fst (ps.head) == key else lookup (key) (ps.tail)

# mapM_ :: (a -> IO b) -> [a] -> IO ()
def mapM_(f):
    def mapM_f(xs):
        if xs != Nil:
            f (xs.head)
            mapM_f (xs.tail)
    return mapM_f

# convert a python list into a cons list
cl = lambda arr: (Nil) if (len (arr) == 0) else (Cons (arr[0]) (cl (arr[1:])))

################################################################
# Buzz Time

# type MS = Int
# type Freq = InRange 0 255
# type Vibe = [(MS, Freq)]

# vibe_len :: MS
vibe_len = 250

# low_freq :: Freq
low_freq = 96
# high_freq :: Freq
high_freq = 255

# null_vibe :: Vibe
null_vibe = pure ((vibe_len, 0))
# zero_vibe :: Vibe
zero_vibe = pure ((vibe_len * 3 / 2, low_freq))
# one_vibe :: Vibe
one_vibe = pure ((vibe_len, high_freq))
# two_vibe :: Vibe
two_vibe = cl (
    [ (2 * vibe_len / 5, high_freq)
    , (1 * vibe_len / 5, 0)
    , (2 * vibe_len / 5, high_freq)
    ])

# bin_case :: [(Int, Vibe)]
bin_case = cl(
    [ (0, zero_vibe)
    , (1, one_vibe)
    ])
# tern_case :: [(Int, Vibe)]
tern_case = Cons ((2, two_vibe)) (bin_case)

# gen_vibes :: Int -> Int -> [Vibe]
gen_vibes = lambda modulus: lambda val: cl(
    [ lookup (val / (modulus /  2) % 2) (bin_case)
    , lookup (val / (modulus /  6) % 3) (tern_case)
    , lookup (val / (modulus / 12) % 2) (bin_case)
    ])

# vibes :: Int -> Int -> [Vibe]
vibes = lambda hours: lambda minutes: \
    (append
        (gen_vibes (12) (hours))
        (Cons (null_vibe) (gen_vibes (60) (minutes)))
    )

# main :: IO ()
def main():
    hours = int (time.strftime ("%H"))
    minutes = int (time.strftime ("%M"))
    proxy = dbus.SystemBus().get_object ('com.nokia.mce', '/com/nokia/mce/request')
    iface = dbus.Interface (proxy, dbus_interface='com.nokia.mce.request')
    def doVibe(f):
        iface.req_start_manual_vibration (snd (f), fst (f))
        time.sleep (float (fst (f)) / 1000)
    def doVibeList(fs):
        total = sum (map (fst) (fs))
        mapM_ (doVibe) (fs)
        time.sleep (float (total) / 2000)
    mapM_ (doVibeList) (vibes (hours) (minutes))

main()

# Reenable camera-ui
os.system("/usr/sbin/dsmetool -t /usr/bin/camera-ui")

