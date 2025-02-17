import hashlib
import random
from spacesaving import SpaceSaving

def md5_32bit(s):
    md5_digest = hashlib.md5(s).digest()  # 16-byte (128-bit) digest
    return int.from_bytes(md5_digest[:4], byteorder='little') & 0xffffffff

class ssummary:
    """
    Python translation of the C++ ssummary class, using hashlib.md5
    see https://github.com/papergitkeeper/heavy-keeper-project/blob/master/ssummary.h
    """
    def __init__(self, K, N=1000, M=1000, LEN2=1000):
        # maximum flow
        # M is maximum size of stream-summary
        self.K = K
        self.N = N
        self.M = M
        self.LEN2 = LEN2

        self.sum  = [0] * (self.M + 10)
        self.last = [0] * (self.M + 10)
        self.Next = [0] * (self.M + 10)
        self.ID   = [0] * (self.M + 10)

        self.strs = ["" for _ in range(self.M + 10)]

        self.Next2 = [0] * (self.M + 10)
        self.head2 = [0] * (self.LEN2 + 10)

        self.head = [0] * (self.N + 10)
        self.Left = [0] * (self.N + 10)
        self.Right= [0] * (self.N + 10)

        self.tot = 0
        for i in range(1, M+2):
            self.ID[i]=i
        self.num = self.M+2
        self.Right[0] = N
        self.Left[N]=0

    def space(self):
        return self.M*6 + self.N*3 + self.LEN2

    def location(self, ST):
        data = ST.encode('utf-8')
        return md5_32bit(data) % self.LEN2
    
    def getid(self):
        n = self.num
        self.num -= 1
        i = self.ID[n]
        self.last[i] = 0
        self.Next[i] = 0
        self.sum[i] = 0
        self.Next2[i] = 0
        return i;

    def add2(self, x, y):
        """
        C++:
            Next2[y] = head2[x];
            head2[x] = y;
        """
        self.Next2[y] = self.head2[x]
        self.head2[x] = y

    def find(self, s):
        """
        C++:
            for(int i = head2[location(s)]; i; i = Next2[i])
                if(str[i] == s) return i;
            return 0;
        """
        loc = self.location(s)
        i = self.head2[loc]
        while i != 0:
            if self.strs[i] == s:
                return i
            i = self.Next2[i]
        return 0

    def linkhead(self, i, j):
        """
        C++:
            Left[i] = j;
            Right[i] = Right[j];
            Right[j] = i;
            Left[Right[i]] = i;
        """
        self.Left[i] = j
        self.Right[i] = self.Right[j]
        self.Right[j] = i
        self.Left[self.Right[i]] = i

    def cuthead(self, i):
        """
        C++:
            int t1 = Left[i], t2 = Right[i];
            Right[t1] = t2;
            Left[t2] = t1;
        """
        t1 = self.Left[i]
        t2 = self.Right[i]
        self.Right[t1] = t2
        self.Left[t2] = t1

    def getmin(self):
        if self.tot < self.K:
            return 0
        if self.Right[0] == self.N:
            return 1
        return self.Right[0]

    def link(self, i, ww):
        self.tot += 1
        s = self.sum[i]
        flag = (self.head[s] == 0)

        self.Next[i] = self.head[s]
        if self.Next[i] != 0:
            self.last[self.Next[i]] = i
        self.last[i] = 0
        self.head[s] = i

        if flag:
            j = s - 1
            while j > 0 and j > s - 10:
                if self.head[j] != 0:
                    self.linkhead(s, j)
                    return
                j -= 1
            self.linkhead(s, ww)

    def cut(self, i):
        self.tot -= 1
        s = self.sum[i]
        if self.head[s] == i:
            self.head[s] = self.Next[i]
        if self.head[s] == 0:
            self.cuthead(s)
        t1 = self.last[i]
        t2 = self.Next[i]
        if t1 != 0:
            self.Next[t1] = t2
        if t2 != 0:
            self.last[t2] = t1

    def recycling(self, i):
        w = self.location(self.strs[i])
        if self.head2[w] == i:
            self.head2[w] = self.Next2[i]
        else:
            j = self.head2[w]
            while j != 0:
                if self.Next2[j] == i:
                    self.Next2[j] = self.Next2[i]
                    break
                j = self.Next2[j]

        self.num += 1
        if self.num < len(self.ID):
            self.ID[self.num] = i   

class heavykeeper_minheap:
    def __init__(self, k):
        self.k = k
        self.heap = []      # List to hold [item, weight] pairs.
        self.pos = {}       # Dictionary to map item -> index in heap.

    def isFull(self):
        return self.k == len(self.heap)
    
    def query(self, item):
        if item in self.pos:
            idx = self.pos[item]
            return self.heap[idx][1]
        else:
            return 0


    def update(self, item, weight):
        if item in self.pos:
            idx = self.pos[item]
            self.heap[idx][1] += weight
            self._heapify(idx)
        else:
            if len(self.heap) < self.k:
                self.heap.append([item, weight])
                self.pos[item] = len(self.heap) - 1
                self._bubble_up(len(self.heap) - 1)
            else:
                assert False

    def getmin(self):
        if not self.heap:
            return 0
        return self.heap[0][1]
    
    def find(self, x):
        return x in self.pos

    def replace_min(self, item, weight):
        old_item = self.heap[0][0]
        del self.pos[old_item]
        self.heap[0] = [item, weight]
        self.pos[item] = 0
        self._bubble_down(0)

    # --- Internal helper methods for maintaining the heap ---

    def _bubble_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx][1] < self.heap[parent][1]:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _bubble_down(self, idx):
        n = len(self.heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2

            if left < n and self.heap[left][1] < self.heap[smallest][1]:
                smallest = left
            if right < n and self.heap[right][1] < self.heap[smallest][1]:
                smallest = right

            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def _heapify(self, idx):
        self._bubble_up(idx)
        self._bubble_down(idx)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos[self.heap[i][0]] = i
        self.pos[self.heap[j][0]] = j


class HeavyKeeper:
    """
    Python implementation of the HeavyKeeper algorithm,
    check https://github.com/papergitkeeper/heavy-keeper-project/blob/master/heavykeeper.h
    and https://github.com/migotom/heavykeeper/blob/master/bin/topk-hk/main.go
    """

    def __init__(self, M2, k):
        random.seed(0)

        self.HK_b = 1.08
        self.K = k
        self.M2 = M2
        self.depth = 5
        self.width = int(M2//self.depth)

        self.buckets = [
            [{"key": None, "count": 0} for _ in range(self.width)]
            for _ in range(self.depth)
        ]
        # self.min_heap = ssummary(self.K, self.K, self.K, self.K)
        self.min_heap = heavykeeper_minheap(self.K)

    def space(self):
        # 16 bits fp + counter for each bucket
        # ssumary uses 10 list of K counters
        return self.width*self.depth*1.5 + self.K

    def _hash(self, x):
        initial_data = str(hash(x)).encode('utf-8')
        for i in range(self.depth):
            md5_obj = hashlib.md5(initial_data)
            md5_obj.update(str(i).encode('utf-8'))
            full_digest = md5_obj.digest()
            bucket_idx = int(md5_obj.hexdigest(), 16) % self.width
            fp_16 = int.from_bytes(full_digest[-2:], byteorder='little')
            yield (bucket_idx, fp_16)

    def update(self, item, increment=1):
        item = str(item)
        in_min_heap = self.min_heap.find(item)
        maxv = 0

        for row_idx, (bucket_idx, fingerprint) in enumerate(self._hash(item)):
            # print(item, bucket_idx, fingerprint)
            bucket = self.buckets[row_idx][bucket_idx]

            if bucket["key"] == fingerprint:
                if in_min_heap or (bucket["count"]<=self.min_heap.getmin() and increment > 0) or (bucket["count"] > 0 and increment < 0):
                    bucket["count"] += increment
                maxv = max(maxv, bucket["count"])
            else:
                # decay
                if increment > 0:
                    decay_prob = self.HK_b ** (-1*bucket["count"])
                    if random.random() < decay_prob:
                        bucket["count"] -= increment
                        if bucket["count"] < 0:
                            bucket["key"] = fingerprint
                            bucket["count"] = 0
                        maxv = max(maxv, bucket["count"])
        if not in_min_heap:
            if self.min_heap.isFull() == False:
                if maxv > 0:
                    self.min_heap.update(item, maxv)
            elif maxv - self.min_heap.getmin() == 1 and increment > 0:
                self.min_heap.replace_min(item, maxv)
        else:
            self.min_heap.update(item, increment)


    def query(self, item):
        item = str(item)

        in_min_heap =self.min_heap.find(item)
        est_count = 0
        if in_min_heap:
            est_count = self.min_heap.query(item)
        else:
            for row_idx, (bucket_idx, fingerprint) in enumerate(self._hash(item)):
                bucket = self.buckets[row_idx][bucket_idx]
                if bucket["key"] == fingerprint:
                    est_count = max(bucket["count"], est_count)
        return est_count


if __name__ == "__main__":
    # Example usage
    hk = HeavyKeeper(2,2)
    print(hk.space())

    data_stream = [
        "apple", "banana", "cherry", "apple", "banana",
        "apple", "apple", "durian", "banana", "banana",
        "cherry", "apple", "cherry", "eggplant", "banana"
    ]

    for item in data_stream:
        hk.update(item)

    print("Estimated count for 'apple':   ", hk.query("apple"), data_stream.count("apple"))
    print("Estimated count for 'banana':  ", hk.query("banana"), data_stream.count("banana"))
    print("Estimated count for 'cherry':  ", hk.query("cherry"), data_stream.count("cherry"))
    print("Estimated count for 'durian':  ", hk.query("durian"), data_stream.count("durian"))
    print("Estimated count for 'eggplant':", hk.query("eggplant"), data_stream.count("eggplant"))
    print('-------')

    for item in data_stream:
        hk.update(item, -1)

    print("Estimated count for 'apple':   ", hk.query("apple"))
    print("Estimated count for 'banana':  ", hk.query("banana"))
    print("Estimated count for 'cherry':  ", hk.query("cherry"))
    print("Estimated count for 'durian':  ", hk.query("durian"))
    print("Estimated count for 'eggplant':", hk.query("eggplant"))
