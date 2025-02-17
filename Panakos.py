from spacesaving import SpaceSaving
from githubCountMin import CountMinSketch
import math
import collections
from collections import defaultdict
import hashlib
import copy
from statistics import mean
import numpy as np



class Panakos():
    def __init__(self, memory_budget, T = 16):
        bitVectorLength = int(memory_budget * 0.35 * 32 / 2)
        self.bitmapLen = int(bitVectorLength)
        self.bitmap = np.zeros(self.bitmapLen, dtype=bool)
        self.bitmap_morethanonce = np.zeros(self.bitmapLen, dtype=bool)

        self.countMinColumns =  int(memory_budget * 0.15 * 32 / 4)
        self.countMinRows = 2
        self.CountMin = CountMinSketch(self.countMinColumns, self.countMinRows)
        self.T = T
        self.SpaceSaving = SpaceSaving(int(memory_budget * 0.5 / 3)) # spacesaving uses 3 counters (item, insert count, delete count)
    
    def _hash(self, x):
        md5 = hashlib.md5(str(hash(x)).encode('utf-8'))
        return int(md5.hexdigest(), 16) % self.bitmapLen

    def update(self, x, weight=1):
        if weight > 0:
            bit_position = self._hash(x)
            if self.bitmap[bit_position] == False:
                self.bitmap[bit_position] = True
                self.bitmap_morethanonce[bit_position] = False
                return
            if self.CountMin.query(x) < self.T-1: # 4 bit so 0 - 15
                self.bitmap_morethanonce[bit_position] = True
                self.CountMin.add(x, weight)
                return
            self.SpaceSaving.update(x, weight)
        else:
            if self.SpaceSaving.find(x): # monitored
                self.SpaceSaving.update(x, weight)
                return
            bit_position = self._hash(x)
            if self.bitmap[bit_position] == True and self.bitmap_morethanonce[bit_position] == False:
                self.bitmap[bit_position] = False
                return
            if self.bitmap_morethanonce[bit_position] == True and self.CountMin.query(x) > 0:
                self.CountMin.add(x, weight)
                return
            if self.CountMin.query(x) == 0:
                self.bitmap_morethanonce[bit_position] = False
            self.bitmap[bit_position] = False
        return
    def query(self, x):
        """
        Return an estimation of the amount of times `x` has ocurred.
        """
        if self.SpaceSaving.find(x):
            return self.SpaceSaving.query(x) + self.T
        bit_position = self._hash(x)
        if self.bitmap[bit_position] == False and self.bitmap_morethanonce[bit_position] == False:
            return 0
        if self.bitmap[bit_position] == True and self.bitmap_morethanonce[bit_position] == False:
            return 1
        return self.CountMin.query(x) + int(self.bitmap[bit_position])
    