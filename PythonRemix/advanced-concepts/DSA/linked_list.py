stack = []

#push
stack.append('A')
stack.append('B')
stack.append('C')

print(stack)

#peek

topE = stack[-1]

print(topE)

#pop

remLastE = stack.pop()

print(f"Remove Last Ele: {remLastE}")

print(f"Stack after Pop: {stack}")

# isEmpty
_empty = not bool(stack)

print(f"Is empty {_empty}")

# size
_size = len(stack)
print(f"size stack: {_size}")

class Stack_:
    def __init__(self):
        self.stack = []
        
    # push method
    
    def push(self, element):
        self.stack.append(element)
        
    # pop
    def pop(self):
        if self.isEmpty():
            return "Stack is Empty"
        
        return self.stack.pop()
        
    def peek(self):
        if self.isEmpty():
            return "Stack is Empty"
                
        return self.stack[-1]
    
    def isEmpty(self):
        return self.size == 0
    
    
    def size(self):
        return len(self.stack)
    
    
# create stack 

# myStack = Stack_()
# myStack.push('A')
# myStack.push('B')
# myStack.push('C')
# myStack.push('D')

# print("Stack:", myStack.stack)
# print("Pop: ", myStack.pop())
# print("Stack after Pop: ", myStack.stack)
# print("Peek: ", myStack.peek())
# print("isEmpty: ", myStack.isEmpty())
# print("Size: ", myStack.size())

# STACK IMPLEMENTATION USING A LINKED LIST


class Node:
    def __init__(self,value):
        self.value = value
        self.next = None
        
class Stack:
    def __init__(self):
        self.head = None
        self.size = 0
        
    def push(self, value):
        new_node = Node(value)
        if self.head:
            new_node.next = self.head
        self.head = new_node
        self.size += 1
        
    def pop(self):
        if self.isEmpty():
            return "Stack is empty"
    
        popped_node = self.head
        self.head = self.head.next
        self.size -= 1
        return popped_node.value
    
    def peek(self):
        if self.isEmpty():
            return "Stack is Empty"
        
        return self.head.value
    
    def isEmpty(self):
        return self.size == 0
    
    def stackSize(self):
        return self.size
    
    def traverseAndPrint(self):
        currentNode = self.head
        while currentNode:
            print(currentNode.value, end=" -> ")
            currentNode = currentNode.next
            
        print()
newStack = Stack()

newStack.push('A')
newStack.push('B')
newStack.push('C')
newStack.push('D')

print("Linked list: ", end="")
newStack.traverseAndPrint()

print("Peek ", newStack.peek())
print("POP: ", newStack.pop())
print("Linked list after pop", end="")

newStack.traverseAndPrint()

print("IsEMpty: ", newStack.isEmpty())

print("size: ", newStack.stackSize())



# queue class

# class Queue:
#     def __init__(self):
#         self.queue = []
        
#     def enqueue(self, element):
#         self.queue.append(element)
        
#     def dequeue(self):
#         if self.isEmpty():
#             return "Queue is empty"
#         return self.queue.pop(0)
    
#     def peek(self):
#         if self.isEmpty():
#             return "Queue is Empty"
#         return self.queue[0]
#     def isEmpty(self):
#         return len(self.queue) == 0

#     def size(self):
#         return len(self.queue)
    
# myQueue = Queue()

# myQueue.enqueue('A')
# myQueue.enqueue('B')
# myQueue.enqueue('C')
# myQueue.enqueue('D')

print('--'*10)
# print("Queue: ", myQueue.queue)
# print("Peek: ", myQueue.peek())
# print("Dequeue: ", myQueue.dequeue())
# print("Queue after Dequeue: ", myQueue.queue)
# print("isEmpty: ", myQueue.isEmpty())
# print("Size: ", myQueue.size())
    
print('--'*10, 'Linked List Queuues')  

class Node:
    def __init__(self,data):
        self.data = data
        self.next = None
        
class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.length = 0
        
    def enqueue(self, element):
        new_node = Node(element)
        if self.rear is None:
            self.front = self.rear = new_node
            self.length += 1
            
            return
        self.rear.next = new_node
        self.rear = new_node
        self.length += 1
        
    def dequeue(self):
        if self.isEmpty():
            return "Queue is Empty"
        
        temp = self.front
        self.front = temp.next
        self.length -= 1
        
        if self.front is None:
            self.rear = None
        return temp.data
    
    def peek(self):
        if self.isEmpty():
            return "Queue is empty"
        return self.front.data
    
    def isEmpty(self):
        return self.length == 0
    
    def size(self):
        return self.length
    
    def printQueue(self):
        temp = self.front
        while temp:
            print(temp.data, end=' -> ')
            temp = temp.next
        print()
        
        
# create queue class

# myQueuue = Queue()

# myQueuue.enqueue('A')
# myQueuue.enqueue('B')
# myQueuue.enqueue('C')

# print("Queue: ", end="")
# myQueuue.printQueue()
# print("Peek: ", myQueuue.peek())
# print("Dequeue: ", myQueuue.dequeue())
# print("Queue after Dequeue: ", end="")
# myQueuue.printQueue()
# print("isEmpty: ", myQueuue.isEmpty())
# print("Size: ", myQueuue.size())
        
# TRAVERSE A LINKED LIST



class Nodee:
    def __init__(self, data):
        self.data = data
        self.next = None
        
def traverseAndPrint(head):
    currentNode = head
    leastValue = currentNode.data
    while currentNode:
        print(currentNode.data, end=' -> ')
        if currentNode.data <= leastValue:
            leastValue = currentNode.data
            
        currentNode = currentNode.next
    print('Min Valude: ', leastValue)
    return leastValue
        
node1 = Nodee(7)
node2 = Nodee(11)
node3 = Nodee(3)
node4 = Nodee(2)
node5 = Nodee(9)

node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node5
node4.next = node5

# traverseAndPrint(node1)

# DELETE SPECIFIC NODE

class Node2:
    def __init__(self,data):
        self.data = data
        self.next = None
        
def traverse_and_print(head):
    currentNode = head
    while currentNode:
        print(currentNode.data, end=" -> ")
        currentNode = currentNode.next
    print('null')
    
def deleteSpecificNode(head, nodeToDelete):
    if head == nodeToDelete:
        return head.next
    
    currentNode = head
    while currentNode.next and currentNode.next != nodeToDelete:
        currentNode = currentNode.next
        
    if currentNode.next is None:
        return head
    
    currentNode.next = currentNode.next.next
    
    return head


node1 = Node2(7)
node2 = Node2(11)
node3 = Node2(3)
node4 = Node2(2)
node5 = Node2(9)

node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node5

# print("Before deletion:")
# traverseAndPrint(node1)

# # Delete node4
# node1 = deleteSpecificNode(node1, node4)

# print("\nAfter deletion:")
# traverseAndPrint(node1)

class Node3:
  def __init__(self, data):
    self.data = data
    self.next = None

def traverseAndPrint(head):
  currentNode = head
  while currentNode:
    print(currentNode.data, end=" -> ")
    currentNode = currentNode.next
  print("null")

def insertNodeAtPosition(head, newNode, position):
  if position == 1:
    newNode.next = head
    return newNode

  currentNode = head
  for _ in range(position - 2):
    if currentNode.next is None:
      break
    currentNode = currentNode.next

  newNode.next = currentNode.next
  currentNode.next = newNode
  return head

node1 = Node3(7)
node2 = Node3(3)
node3 = Node3(2)
node4 = Node3(9)

node1.next = node2
node2.next = node3
node3.next = node4

print("Original list:")
traverseAndPrint(node1)

# Insert a new node with value 97 at position 2
newNode = Node3(97)
node1 = insertNodeAtPosition(node1, newNode, 2)

print("\nAfter insertion:")
traverseAndPrint(node1)
    

    
        
        
        
        
        
        
        
        
        
        
        
        
        








            
        
        
        