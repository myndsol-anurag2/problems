class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self, value):
        new_node = Node(value)
        self.head = new_node
        self.tail = new_node
        self.length = 1
        
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
    
    def append(self, value):
        new_node = Node(value)
        if self.length == 0:            
            self.head = new_node
            self.tail = new_node
        else:            
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        
    def __str__(self):
        cur_node = self.head
        strr = ''
        while cur_node:
            strr += str(cur_node.value) + '->'
            cur_node = cur_node.next
        return strr
            
    def get(self, index):
        temp_node = self.head
        for _ in range(index):
            temp_node = temp_node.next
        return temp_node
    
    def set(self, index, value):
        temp_node = self.get(index)
        if temp_node:
            temp_node.value = value
    
    def prepend(self, value):
        new_node = Node(value)
        if self.length == 0:
            self.head = new_node
            self.tail = new_node     
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1
        
        
    def insert(self, index, value):
        if index == self.length:
            self.append(value)
        elif index == 0:
            self.prepend(value)
        elif index > self.length:
            return None
        else:
            temp_node = self.get(index - 1)
            print(temp_node.value)
            new_node = Node(value)
            new_node.next = temp_node.next
            temp_node.next = new_node
            self.length += 1
            
    def pop(self):
        if self.length == 0:
            return None
        popped_node = self.tail
        if self.length == 1:
            self.head = self.tail = None
        else:
            temp = self.head
            while temp.next is not self.tail:
                temp = temp.next
                print(temp.value)
            self.tail = temp
            temp.next = None
        self.length -= 1
        return popped_node
    
    
    def remove(self, index):
        if index < 0 or index >= self.length:
            return None
        if index == 0:
            self.pop_first()
        elif index == self.length - 1:
            self.pop()
        else:
            
            prev_node = self.get(index - 1)
            popped_node = prev_node.next
            prev_node.next = popped_node.next
            popped_node.next = None
            self.length -= 1
            return popped_node
        
    def mid(self):
        slow = self.head
        fast = self.head
        while fast and fast.next:
            slow=slow.next
            fast = fast.next.next
        return slow.value
    
    def reverese(self):
        prev_node = None
        cur_node = self.head
        while cur_node:
            next_node = cur_node.next
            cur_node.next = prev_node
            prev_node = cur_node
            cur_node = next_node
        self.head, self.tail = self.tail, self.head
            
        
        
ll = LinkedList()
ll.append(1)
ll.append(3)
# ll.append(2)
ll.prepend(0)
ll.insert(2,4)
ll.insert(2,5)
print(ll.mid())
ll.reverese()
print(ll)
