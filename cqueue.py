class Queue:
    def __init__(self, maxSize):
        self.items = [None] * maxSize
        self.maxSize = maxSize
        self.start = -1
        self.top = -1

    def __str__(self):
        values = [str(x) for x in self.items]
        return ' '.join(values)
    
    def isFull(self):
        if self.start == 0 and self.top == self.maxSize - 1:
            return True
        elif self.start == self.top + 1:
            return True
        else:
            return False
        
    def isEmpty(self):
        if self.top == -1:
            return True
        else:
            return False
    
    def enqueue(self,value):
        if self.isFull():
            return "Queue is full."
        else:
            if self.top + 1 ==self.maxSize:
                self.top = 0
            else:
                self.top += 1
                if self.start == -1:
                    self.start = 0
            self.items[self.top] = value
            
    def dequeue(self):
        if self.isEmpty():
            return "Empty Queue."
        else:
            retrunVal = self.items[self.start]
            start = self.start
            if self.start == self.top:
                self.start = -1
                self.top = -1
            self.start +=1
            self.items[start] = None
            return retrunVal
            
                
             