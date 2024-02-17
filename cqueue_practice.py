class Queue:
    def __init__(self, maxsize):
        self.items = [None] * maxsize
        self.maxsize = maxsize
        self.start = -1
        self.start = -1
        
    def isFull(self):
        if self.start == 0 and self.top == self.maxsize - 1:
            return True
        if self.start == self.top + 1:
            return True
        else:
            return False
        
    def isEmpty(self):
        if self.top == -1:
            return True
        else:
            return False
    
    def enqueue(self, value):
        if self.isFull():
            return "Queue is full."
        else:
            if self.top+1 == self.maxsize:
                self.top = 0
            else:
                self.top += 1
                if self.start == -1:
                    self.start = 0
            self.items[self.top] = value
            
    def dequeue(self):
        if self.isEmpty():
            return "Queue is empoty"
        else:
            retrunVal = self.items[self.start]
            start = self.start
            if self.start == self.top:
                self.start = -1
                self.top = -1
            self.start += 1
            self.items[start] = None
            return retrunVal
                
        
    
    