from collections import defaultdict
class SpaceSaving():
    def __init__(self, k=100):
        self.k = k
        self.size = 0
        self.weight_heap = [] # Min heap
        self.item_to_indices = defaultdict(int)
        self.total_items = 0
    
    def parent(self, i):
        return (i-1)//2
    def left(self, i): 
        return 2*i + 1
    def right(self, i):
        return 2*i + 2
    def isFull(self):
        return self.size == self.k
    def isEmpty(self):
        return self.size==0
    
    def swap(self, tuple_x, tuple_y):
        x, insert_x, delete_x = tuple_x
        y, insert_y, delete_y = tuple_y

        assert self.weight_heap[self.item_to_indices[x]][0] == x, 'bug'
        assert self.weight_heap[self.item_to_indices[y]][0] == y, 'bug'

        x_weight_index = self.item_to_indices[x]
        y_weight_index = self.item_to_indices[y]

        self.weight_heap[x_weight_index] = tuple_y
        self.weight_heap[y_weight_index] = tuple_x
        self.item_to_indices[x] = y_weight_index
        self.item_to_indices[y] = x_weight_index
        
        assert self.weight_heap[self.item_to_indices[x]][0] == x, 'bug'
        assert self.weight_heap[self.item_to_indices[y]][0] == y, 'bug'
            
    
    def insertUnmonitored(self, item, val):
        assert val > 0 

        arr = self.weight_heap
        self.item_to_indices[item] = len(arr)
        
        assert(len(arr) < self.k)

        arr.append([item, val, 0]) # item, insert count, delete count

        index = len(arr) - 1
        while index!=0 and arr[self.parent(index)][1] > arr[index][1]:
            self.swap(arr[self.parent(index)], arr[index])
            index = self.parent(index)
            
    def updateMonitored(self, item, delta_val):
        assert item in self.item_to_indices
        assert delta_val in {1, -1}

        index = 0
        arr = self.weight_heap
        index = self.item_to_indices[item]

        assert self.weight_heap[index][0] == item
        
        prev_val = arr[index][1]
        if delta_val == 1: 
            arr[index][1] += 1
        else:
            arr[index][2] += 1

        new_val = arr[index][1]
        
        if new_val <= prev_val:
            return
            # push up
            # while index!=0 and arr[self.parent(index)][1] > arr[index][1]:
            #     self.swap(arr[self.parent(index)], arr[index])
            #     index = self.parent(index)
        else:
            # push down
            while self.left(index) < self.size:
                smallest_child_index = self.left(index)
                if self.right(index) < self.size and arr[self.right(index)][1] < arr[smallest_child_index][1]:
                    smallest_child_index = self.right(index)
                if arr[index][1] > arr[smallest_child_index][1]:
                    self.swap(arr[index], arr[smallest_child_index])
                    index = smallest_child_index
                else:
                    return
        
        
        
    def update(self, x, val):
        self.total_items += val
        if x in self.item_to_indices:
            weight_index = self.item_to_indices[x]
            self.updateMonitored(x, val)
        else:
            if self.size < self.k:
                assert(val > 0)
                self.size += 1
                self.insertUnmonitored(x, val)
            else:
                if val > 0:
                    # replace min
                    min_item, min_weight, _ = self.weight_heap[0]
                    assert self.item_to_indices[min_item] == 0
                    
                    self.updateMonitored(min_item, val)

                    weight_index = self.item_to_indices[min_item]
                    assert self.weight_heap[weight_index][0] == min_item
                    
                    self.weight_heap[weight_index][0] = x
                    self.weight_heap[weight_index][2] = 0 # reset delete count
                    del self.item_to_indices[min_item]
                    self.item_to_indices[x] = weight_index
                        
                    
              
    def query(self, x):
        """
        Return an estimation of the amount of times `x` has ocurred.
        """
        if x in self.item_to_indices:
            index = self.item_to_indices[x]
            return self.weight_heap[index][1] - self.weight_heap[index][2]
        return 0

    def __getitem__(self, x):
        """
        A convenience method to call `query`.
        """
        return self.query(x)
    
    def space(self):
        return self.k
    
    def output(self):
        print("weight_heap: ", self.weight_heap)
        print("map: ", self.item_to_indices)