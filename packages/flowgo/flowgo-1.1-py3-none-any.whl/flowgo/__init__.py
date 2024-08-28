import numpy as np
import sys

class new:
    def __init__(
        self,
        types: float,
        flow: int):
        self.types = types
        self.stack = np.zeros(shape=flow, dtype=self.types)
        self._index = []
        for data in self.stack:
            self._index.append(data)
    def _py_capacity(
        self,
        x:  list):
        self.x = x
        self.size = sys.getsizeof([]) #  --> new.__init__
        print("size of an empty list :", self.size)
        print("size_total", sys.getsizeof(self.x))
        capacity = (sys.getsizeof(self.x)-self.size)//8
        print("capacity of the list is:", capacity)
        return capacity

    def _capacity(
        self,
        size: int):  # how much to increase the stack
        self.stack.resize(size,refcheck=True)
        for data in self.stack:
            self._index.append(data)
            
    def _clear(self,index):
        self.size = len(self._index)
        for i in range(0,self.size,1):
            if i == index:
                self._index.pop(i)
    def _get(self,index):
        self.size = len(self._index)
        for i in range(0,self.size,1):
            self._index[i]
        return self._index[index]
    
    def _set(self,index,item):
        self.size = len(self._index)
        for i in range(0,self.size,1):
            if i == index:
                self._clear(i)
                return self._index.insert(i,item)


