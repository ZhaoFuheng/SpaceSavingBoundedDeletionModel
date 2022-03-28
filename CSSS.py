import numpy as np
import math
from Crypto.Util import number
import random
import statistics
import hashlib



class CSSS_CountSketch():
    def __init__(self, d, t):
        # Original count sketch t = O(1/epsilon) and d = O(log(1/delta)) 
        # Think delta as U^{-c} d = O(logU)
        # d represent number of rows and t represent number of columns
        
        self.total_input = 0
        self.columns = math.ceil(t)
        
        self.rows =math.ceil(d)
        self.prime = number.getPrime(32)
        
        self.table_positive = np.zeros( (self.rows, self.columns) )
        self.table_negative = np.zeros( (self.rows, self.columns) )
        
        # Generate 4-wise independent hash functions
        self.a = []
        self.b = []
        self.c = []
        self.d = []
        for i in range(d):
            aj, bj = np.random.randint(self.prime - 1, size=2) #randomly select one number from 0 to self.prime -1
            cj, dj = np.random.randint(self.prime - 1, size=2)
            assert aj != bj and cj!=dj
            self.a.append(aj+1)
            self.b.append(bj+1)
            self.c.append(cj+1)
            self.d.append(dj+1)
    # Rountine A is only called from CSSS Sketch
    def routine_a(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.table_positive[i][j] = np.random.binomial(self.table_positive[i][j], 1/2)
                self.table_negative[i][j] = np.random.binomial(self.table_negative[i][j], 1/2)

    def add(self, item, weight):
        self.update(item, weight)
        
    def update(self, x, weight=1):
        item = None
        try:
            item = int(x)
        except:
            item = int( hashlib.md5(str(hash(x.encode('utf-8'))).encode('utf-8')).hexdigest(), 16)

        self.total_input += weight

        for j in range(self.rows):
            hj = ( (self.a[j] * item + self.b[j]) % self.prime) % self.columns
            gj = 2 * (( (self.c[j] * item + self.d[j]) % self.prime) % 2) - 1
            updated_weight = weight * gj
            if updated_weight > 0:
                self.table_positive[j][hj] += updated_weight
            else:
                #updated_weight<0
                self.table_negative[j][hj] += abs(updated_weight)

    def query(self, x):
        item = None
        try:
            item = int(x)
        except:
            item = int( hashlib.md5(str(hash(x.encode('utf-8'))).encode('utf-8')).hexdigest(), 16)
        ans = []
        for j in range(self.rows):
            hj = int( ( (self.a[j] * item + self.b[j]) % self.prime) % self.columns )
            gj = 2 * (( (self.c[j] * item + self.d[j]) % self.prime) % 2) - 1
            assert( gj == -1 or gj == 1)
            ans.append ( gj * (self.table_positive[j][hj] - self.table_negative[j][hj] ))

        return statistics.median(ans)

    def inputsize(self):
        return self.total_input

    def countertable(self):
        return self.table


class CSSS_sketch():
    def __init__(self, epsilon=0.01, universe=2**16, k=100, alpha=2):
        assert k>=1
        assert 0<epsilon<1
        self.alpha = alpha
        self.epsilon = epsilon
        self.universe = universe
        
        self.T = math.ceil(4/(epsilon**2) + math.log2(universe))
        self.S = math.ceil( alpha*alpha/(epsilon*epsilon) * self.T*self.T* math.log2(universe) )
        self.d = math.ceil(math.log2(universe))
        self.multiple = math.ceil(math.log(self.S)) # Used to perform binomial sampling
        
        self.k = math.ceil(k) * 6
        self.count_sketch = CSSS_CountSketch( self.d, self.k) # d x 6k 
        self.r = 1
        self.p = 0
        self.time = 0 #time <= |m|
        self.samples = 0
        self.total_input = 0

    def expo_of_two(self, x):
        return (x and (not(x & (x - 1))) )

    def update(self, item, weight=1):
        self.time += 1
        self.total_input += 1
        
        factor = (self.time -1) /self.multiple
        if (self.time -1)%self.multiple == 0 and factor >= 1 and self.expo_of_two(int(factor)) :
            self.count_sketch.routine_a()
            self.p+=1
        rand = random.random()
        if rand < 2**(-1*self.p):
            #sampled
            self.samples += 1
            self.count_sketch.update(item, weight)
    def query(self, item):
        ans = self.count_sketch.query(item)
        return ans* (2**(self.p))
    def space(self):
        return math.floor( self.d*self.k*math.log2(self.alpha* math.log2(self.universe) / self.epsilon) )
