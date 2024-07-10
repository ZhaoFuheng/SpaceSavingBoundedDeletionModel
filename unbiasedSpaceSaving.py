from collections import defaultdict
import random
class SpaceSaving():
    def __init__(self, k=100):
        self.k = k
        self.size = 0
        self.total_items = 0
        self.insert_count_heap = [] # Min heap map to index in self.items
        self.delete_count_heap = [] # Min heap map to index in self.items
        self.items = []

        # map item to [index in insertHeap, index in deleteHeap]
        self.item_to_indices = defaultdict(list) 
        random.seed(1)

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
    
    def swap(self, arr_index_x, arr_index_y, isInsertHeap):
        weight_heap = None
        # if isInsertHeap:
        #     weight_heap = self.insert_count_heap
        # else:
        #     weight_heap = self.delete_count_heap

        x = self.items[arr_index_x][0]
        y = self.items[arr_index_y][0]

        x_insert_heap_index, x_delete_heap_index = self.item_to_indices[x]
        y_insert_heap_index, y_delete_heap_index = self.item_to_indices[y]

        if isInsertHeap:
            self.insert_count_heap[x_insert_heap_index] = arr_index_y
            self.insert_count_heap[y_insert_heap_index] = arr_index_x

            # make sure it points to the correct position in insert heap
            self.item_to_indices[x][0] = y_insert_heap_index
            self.item_to_indices[y][0] = x_insert_heap_index

        else:
            self.delete_count_heap[x_delete_heap_index] = arr_index_y
            self.delete_count_heap[y_delete_heap_index] = arr_index_x

            # make sure it points to the correct position in delete heap
            self.item_to_indices[x][1] = y_delete_heap_index
            self.item_to_indices[y][1] = x_delete_heap_index
            
    
    def insertUnmonitored(self, item, val):
        assert val > 0 

        self.items.append([item, val, 0])
        self.item_to_indices[item] = [len(self.insert_count_heap), len(self.delete_count_heap)]
        
        assert(len(self.items) <= self.k)

        self.insert_count_heap.append(len(self.items)-1)
        self.delete_count_heap.append(len(self.items)-1)

        insert_count_index = len(self.insert_count_heap) - 1
        while insert_count_index!=0 and\
            self.items[self.insert_count_heap[self.parent(insert_count_index)]][1] >\
                self.items[self.insert_count_heap[insert_count_index]][1]:
            self.swap(self.insert_count_heap[self.parent(insert_count_index)], self.insert_count_heap[insert_count_index], True)
            insert_count_index = self.parent(insert_count_index)

        delete_count_index = len(self.delete_count_heap) - 1
        while delete_count_index!=0 and\
            self.items[self.delete_count_heap[self.parent(delete_count_index)]][1] >\
                self.items[self.delete_count_heap[delete_count_index]][1]:
            self.swap(self.delete_count_heap[self.parent(delete_count_index)], self.delete_count_heap[delete_count_index], False)
            delete_count_index = self.parent(delete_count_index)


    def heapify_down(self, heap, index, isInsert):
        size = len(heap)
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        pos = 1
        if not isInsert:
            pos = 2

        if left < size and\
                self.items[heap[left]][pos] < self.items[heap[smallest]][pos]:
            smallest = left
        if right < size and self.items[heap[right]][pos] < self.items[heap[smallest]][pos]:
            smallest = right
        if smallest != index:
            self.swap(smallest, index, isInsert)
            self.heapify_down(heap, smallest, isInsert)

    def heapify_up(self, heap, index, isInsert):
        pos = 1
        if not isInsert:
            pos = 2
        while index > 0:
            parent = (index - 1) // 2
            if self.items[heap[index]][pos] < self.items[heap[parent]][pos]:
                self.swap(parent, index, isInsert)
                index = parent
            else:
                break

            
    def updateMonitored(self, item, val):
        assert item in self.item_to_indices

        insert_heap_index, delete_heap_index = self.item_to_indices[item]

        assert self.items[self.insert_count_heap[insert_heap_index]][0] == item
        assert self.items[self.delete_count_heap[delete_heap_index]][0] == item

        item_arr_index = self.insert_count_heap[insert_heap_index]
        _, prev_insert_count, prev_delete_count = self.items[item_arr_index]
        if val > 0:
            self.items[item_arr_index] = [item,prev_insert_count+val, prev_delete_count]
        else:
            self.items[item_arr_index] = [item,prev_insert_count, prev_delete_count+abs(val)]
        _, insert_count, delete_count = self.items[item_arr_index]
        if insert_count > prev_insert_count:
            self.heapify_down(self.insert_count_heap, insert_heap_index, True)
        if insert_count < prev_insert_count:
            self.heapify_up(self.insert_count_heap, insert_heap_index, True)
        if delete_count > prev_delete_count:
            self.heapify_down(self.delete_count_heap, delete_heap_index, False)
        if delete_count < prev_delete_count:
            self.heapify_up(self.delete_count_heap, delete_heap_index, False)
        
    def update(self, x, val):
        self.total_items += val
        if x in self.item_to_indices:            
            self.updateMonitored(x, val)
        else:
            if self.size < self.k:
                assert(val > 0)
                self.size += 1
                self.insertUnmonitored(x, val)
            else:
                if val > 0:
                    arr_index = self.insert_count_heap[0]
                    min_item, min_insert_count, delete_count = self.items[arr_index]
                    assert self.item_to_indices[min_item][0] == 0
                    self.updateMonitored(min_item, val)
                    if random.random() < 1.0/(1.0+min_insert_count):
                        # print('insert replacement')
                        # Perform Replacement
                        insert_index, delete_index = self.item_to_indices[min_item]
                        arr_index = self.insert_count_heap[insert_index]
                        # item to x
                        self.items[arr_index][0] = x
                        # change delete count to 0
                        self.items[arr_index][2] = 0
                        del self.item_to_indices[min_item]
                        self.item_to_indices[x] = [insert_index, delete_index]

                        # heapify 
                        self.heapify_down(self.delete_count_heap, delete_index, False)
                        self.heapify_up(self.delete_count_heap, delete_index, False)
                if val < 0:
                    arr_index = self.insert_count_heap[0]
                    min_item, min_insert_count, delete_count = self.items[arr_index]
                    assert self.item_to_indices[min_item][0] == 0
                    self.updateMonitored(min_item, val)
                    if random.random() < 1.0/(1.0+delete_count):
                        # print('delete replacement')
                        # Perform Replacement
                        insert_index, delete_index = self.item_to_indices[min_item]
                        arr_index = self.insert_count_heap[insert_index]
                        # item to x
                        self.items[arr_index][0] = x
                        # change delete count to 0
                        self.items[arr_index][1] = 0
                        del self.item_to_indices[min_item]
                        self.item_to_indices[x] = [insert_index, delete_index]

                        # heapify 
                        self.heapify_down(self.insert_count_heap, insert_index, True)
                        self.heapify_up(self.insert_count_heap, insert_index, True)

                    
              
    def query(self, x):
        """
        Return an estimation of the amount of times `x` has ocurred.
        """
        if x in self.item_to_indices:
            insert_index, _ = self.item_to_indices[x]
            _, inserts, deletes = self.items[self.insert_count_heap[insert_index]]
            return inserts - deletes
        return 0

    def __getitem__(self, x):
        """
        A convenience method to call `query`.
        """
        return self.query(x)
    
    def space(self):
        return self.k
    
    def output(self):
        print(self.items)
        print()
        print("insert heap: ", self.insert_count_heap)
        print()
        print("delete heap: ", self.delete_count_heap)
        print()
        print(self.item_to_indices)