class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
    
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
        
    
    def __init__(self, value):
        node = Node(value)
        self.head = node
        self.tail = node
        self.length = 1
        
    def prepend(self, value):
        node = Node(value)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head = node
        self.length += 1
            
    def append(self, value):
        node = Node(value)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.length += 1
            
    def __str__(self):
        current = self.head
        result = ''
        while current:
            result += str(current.value)
            if current.next:
                result += '->'
            current = current.next
        return result
    
    def insert(self, index, value):
        if index < 0 or index > self.length:
            return False
        elif index == 0:
            self.prepend(value)
        elif index == self.length:
            self.append(value)
        else:
            node = Node(value)
            prev = self.head
            for _ in range(index-1):
                prev = prev.next
            node.next = prev.next
            prev.next = node 
            self.length += 1  
        return True  
      
    def get(self, index):
        if index < 0 or index >= self.length:
            return None
        else:
            current = self.head
            for _ in range(index):
                current = current.next
            return current
        
    def set(self, index, value):
        if index < 0 or index >= self.length:
            return False
        else:
            current = self.head
            for _ in range(index):
                current = current.next
            current.value = value
            return True
    
    def pop_first(self):
        if self.head is None:
            return None
        current = self.head
        if self.length == 1:
            self.head = None
            self.tail = None
        else:
            self.head = current.next
            current.next = None
        self.length -= 1
        return current
            
    def pop(self):
        if self.head is None:
            return None
        last = self.tail
        if self.length == 1:
            self.head = None
            self.tail = None
        else:
            prev = self.head
            for _ in range(self.length-2):
                prev = prev.next
            prev.next = None
            self.tail = prev
        self.length -= 1
        return last
    
    def remove(self, index):
        if index < 0 or index >= self.length:
            return None
        elif index == 0:
            return self.pop_first()
        elif index == self.length-1:
            return self.pop()
        else:
            prev = self.head
            for _ in range(index-1):
                prev = prev.next
            popped_node = prev.next
            prev.next = popped_node.next
            popped_node.next = None
            self.length -= 1
            return popped_node
    
    def reverse(self):
        prev = None
        current = self.head
        for _ in range(self.length):
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head, self.tail = self.tail, self.head
        
    def mid_element(self):
        slow = self.head
        fast = self.head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
        return slow
        
            
            
ll = LinkedList(5)
ll.append(20)
ll.prepend(10)
ll.append(15)
ll.prepend(25)
ll.insert(2,0)
print(ll.length)
print(ll.head.value)
print(ll.tail.value)
print(ll.get(1).value)
ll.set(5,40)
print(ll)
ll.pop_first()
ll.pop()
ll.remove(1)
print(ll.length)
print(ll.head.value)
print(ll.tail.value)
print(ll)
ll.reverse()
print(ll)
print(ll.mid_element().value)