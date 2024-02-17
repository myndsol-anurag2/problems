class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        

class LinkedList :
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
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        
    def __str__(self):
        temp_node = self.head
        result = ''
        while temp_node is not None:
            result += str(temp_node.value)
            if temp_node.next is not None:
                result += ' -> '
            temp_node = temp_node.next
        return result
    
    def search(self, target):
        temp_node = self.head
        index = 0
        while temp_node is not None:
            if temp_node.value == target:
                return index
            temp_node = temp_node.next
            index += 1
        return -1
    
    def get(self, index):
        if index == -1:
            return self.tail
        if index < -1 or index >= self.length:
            return None
        current = self.head
        for _ in range(index):
            current = current.next
        return current
    
    def set(self, value, index):
        temp = self.get(index)
        if temp:
            temp.value = value
            return True
        return False
    
    def prepend(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1
        
    def insert(self, value, index):
        if index < 0 or index > self.length:
            return False
        else:
            if index == 0:
                self.prepend(value)
            elif index == self.length:
                self.append(value)
            else:
                new_node = Node(value)
                temp_node = self.head
                for _ in range(index-1):
                    temp_node = temp_node.next
                new_node.next = temp_node.next
                temp_node.next = new_node
                self.length += 1
            return True   
        
    def pop_first(self):
        if self.length == 0:
            return None
        popped_node = self.head
        if self.length == 1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next
            popped_node.next = None
        self.length -= 1
        return popped_node
    
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
        
    def delete_all(self):
        self.head = None
        self.tail = None
        self.length = 0
        
    def reverse(self):
        prev_node = None
        current_node = self.head
        while current_node is not None:
            next_node = current_node.next
            current_node.next = prev_node
            prev_node = current_node
            current_node = next_node
        self.head, self.tail = self.tail, self.head
        
class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
        
    def createCSLL(self, value):
        node = Node(value)
        node.next = node
        self.head = node
        self.tail = node
        self.length = 1
        
    def insertCSLL(self, value, location):
        if self.head is None:
            return False
        else:
            new_node = Node(value)
            if location == 0:
                new_node.next = self.head
                self.head = new_node
                self.tail.next = new_node
            elif location == 1:
                new_node.next = self.head
                self.tail.next = new_node
                self.tail = new_node
            else:
                temp_node = self.head
                for _ in range(location-1):
                    temp_node = temp_node.next
                new_node.next = temp_node.next
                temp_node.next = new_node
            self.length += 1
            return True
    
    def __str__(self):
        current = self.head
        result = ''
        while True:
            result += str(current.value)
            current = current.next
            if current != self.head:
                result += '->'
            else:
                break
        return result    
                

ll = LinkedList()
ll.append(10)
ll.append(20)
ll.prepend(5)
ll.prepend(25)
ll.insert(12,4)
print(ll.search(20))
print(ll.get(1).value)
print(ll.set(15,1))
print(ll.length)
print(ll.head.value)
print(ll.tail.value)
print(ll)
# ll.pop()
# ll.pop_first()
# ll.remove(1)
# print(ll)
ll.reverse()
print(ll.head.value)
print(ll.tail.value)
print(ll)
cl = CircularLinkedList()
cl.createCSLL(1)
cl.insertCSLL(2,1)
cl.insertCSLL(3,0)
cl.insertCSLL(4,2)
print(cl.head.value)
print(cl.tail.value)
print(cl.length)
print(cl)

