from collections import defaultdict
class SpaceSaving():
    def __init__(self, k=10, lazy=False, universe = 2**16):
        self.k = k
        self.size = 0
        self.weight_heap = [] # Min heap
        self.error_heap = [] # Max heap
        self.item_to_indices = defaultdict(list)
        self.lazy = lazy
        self.universe = universe
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
    
    def swap(self, isWeight, tuple_x, tuple_y):
        x, x_val = tuple_x
        y, y_val = tuple_y      
        
        x_weight_index, x_error_index = self.item_to_indices[x]
        y_weight_index, y_error_index = self.item_to_indices[y]

        if isWeight:
            self.weight_heap[x_weight_index] = tuple_y
            self.weight_heap[y_weight_index] = tuple_x
            self.item_to_indices[x][0] = y_weight_index
            self.item_to_indices[y][0] = x_weight_index
            
        else:
            self.error_heap[x_error_index] = tuple_y 
            self.error_heap[y_error_index] = tuple_x
            self.item_to_indices[x][1] = y_error_index
            self.item_to_indices[y][1] = x_error_index
        
        x_weight_index, x_error_index = self.item_to_indices[x]
        y_weight_index, y_error_index = self.item_to_indices[y]
        
        if isWeight:
            assert self.weight_heap[x_weight_index][0] == x, 'bug'
            assert self.weight_heap[y_weight_index][0] == y, 'bug'
        else:
            assert self.error_heap[x_error_index][0] == x, 'bug'
            assert self.error_heap[y_error_index][0] == y, 'bug'
            
            
    
    def insertUnmonitored(self, isWeight, item, val):
        arr = []
        if isWeight:
            arr = self.weight_heap
            if item not in self.item_to_indices:
                self.item_to_indices[item] = [len(arr), 0]
            else:
                self.item_to_indices[item][0] = len(arr)
        else:
            arr = self.error_heap
            if item not in self.item_to_indices:
                self.item_to_indices[item] = [0, len(arr)]
            else:
                self.item_to_indices[item][1] = len(arr)
    
        assert(len(arr) < self.k)
        arr.append([item, val])
        index = len(arr) - 1
        
        while index!=0 and arr[self.parent(index)][1] > arr[index][1]:
            self.swap(isWeight, arr[self.parent(index)], arr[index])
            index = self.parent(index)
            
    def updateMonitored(self, isWeight, item, new_val):
        assert item in self.item_to_indices
        index = 0
        arr = []
        if isWeight:
            arr = self.weight_heap
            index = self.item_to_indices[item][0]
        else:
            arr = self.error_heap
            index = self.item_to_indices[item][1]
        
        prev_val = arr[index][1]
        arr[index][1] = new_val
        
        if new_val < prev_val:
            # push up
            while index!=0 and arr[self.parent(index)][1] > arr[index][1]:
                self.swap(isWeight, arr[self.parent(index)], arr[index])
                index = self.parent(index)
        else:
            # push down
            while self.left(index) < self.size:
                smallest_child_index = self.left(index)
                if self.right(index) < self.size and arr[self.right(index)][1] < arr[smallest_child_index][1]:
                    smallest_child_index = self.right(index)
                if arr[index][1] > arr[smallest_child_index][1]:
                    self.swap(isWeight, arr[index], arr[smallest_child_index])
                    index = smallest_child_index
                else:
                    return
        
        
        
    def update(self, x, val):
        self.total_items += val
        if x in self.item_to_indices:
            weight_index, error_index = self.item_to_indices[x]
            self.updateMonitored(True, x, self.weight_heap[weight_index][1]+val)
        else:
            if self.size < self.k:
                assert(val > 0)
                self.size += 1
                self.insertUnmonitored(True, x, val) # for weight
                self.insertUnmonitored(False, x, 0) # for error
            else:
                if val > 0:
                    # replace min
                    min_item, min_weight = self.weight_heap[0]
                    assert self.item_to_indices[min_item][0] == 0
                    
                    self.updateMonitored(True, min_item, min_weight+val)
                    self.updateMonitored(False, min_item, (-1)*min_weight)
                    weight_index, error_index = self.item_to_indices[min_item]
                    
                    assert self.weight_heap[weight_index][0] == min_item
                    assert self.error_heap[error_index][0] == min_item
                    
                    self.weight_heap[weight_index][0] = x
                    self.error_heap[error_index][0] = x
                    
                    del self.item_to_indices[min_item]
                    self.item_to_indices[x] = [weight_index, error_index]
                else:
                    # it is deletion
                    if not self.lazy:
                        max_error_item, max_error = self.error_heap[0]
                        weight_index, error_index = self.item_to_indices[max_error_item]
                        
                        assert error_index == 0
                        assert self.weight_heap[weight_index][0] == max_error_item
                        assert self.error_heap[error_index][0] == max_error_item
                        #val is negative, wieghts are positive, and errors are negative
                        self.updateMonitored(True, max_error_item, self.weight_heap[weight_index][1]+val) 
                        self.updateMonitored(False, max_error_item, self.error_heap[error_index][1]-val)
                        
                    
              
    def query(self, x):
        """
        Return an estimation of the amount of times `x` has ocurred.
        """
        if x in self.item_to_indices:
            return self.weight_heap[self.item_to_indices[x][0]][1]
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
        print("error_heap (-1*error): ", self.error_heap)
        print("map: ", self.item_to_indices)