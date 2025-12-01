class Node:
    def __init__ (self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__ (self, data=None):
        self.front = None
        self.rear = None
        self.size = 0
    
        if data:
            try:
                for d in data:
                    self.enqueue(d)
            except:
                self.enqueue(data)
    def __iter__(self):
        current = self.front
        while current:
            yield current.data
            current = current.next
    
    def enqueue (self, data):
        new_node = Node(data)

        if self.is_empty():
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        
        self.size += 1

    def dequeue (self):
        if self.is_empty():
            raise Exception ("Dequeue from empty queue")
        
        data_out = self.front.data
        self.front = self.front.next

        if not self.front:
            self.rear = None
        
        self.size -= 1

        return data_out
    
    def peek(self):
        if self.is_empty():
            raise Exception ("Peek from empty queue")
        
        return self.front.data

    def is_empty(self):
        return self.front == None
    
    def length(self):
        return self.size
    
class HeapNode:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.parent = None
        self.left = None
        self.right = None

class QHeap:
    def __init__(self):
        self.__root = None
        self.__size = 0
        
    def enqueue(self, key, data):
        new_node = HeapNode(key, data)
        if self.is_empty():
            self.__root = new_node
        else:
            self.__insert_node(new_node)
            self.__bubble_up(new_node)
        
        self.__size += 1

    def dequeue(self):
        if self.is_empty():
            raise Exception("Dequeue from empty queue")
        
        key, data = self.__root.key, self.__root.data  
        if not self.__root.left:  
            self.__root = None
        else:
            last = self.__get_last_node()
            self.__swap(self.__root, last)
            self.__remove_last_node()
            if self.__root:  
                self.__bubble_down(self.__root)
            
        self.__size -= 1
        return key, data
    
    def peek(self):
        if self.is_empty():
            raise Exception("Peek from empty heap")
        return self.__root.data
    
    def __swap(self, n1, n2):
        n1.key, n2.key = n2.key, n1.key
        n1.data, n2.data = n2.data, n1.data
                    
    def __insert_node(self, node):
        path = bin(self.__size + 1)[2:]  
        current = self.__root
        parent = None
        for b in path[1:]:  
            parent = current
            current = current.left if b == '0' else current.right
            if current is None:
                break
        
        node.parent = parent  
        if not parent.left:
            parent.left = node
        else:
            parent.right = node
    
    def __bubble_up(self, node):
        while node.parent and node.key < node.parent.key:  
            self.__swap(node, node.parent)
            node = node.parent
    
    def __bubble_down(self, node):
        while node.left:
            smaller_child = node.left
            if node.right and node.right.key < node.left.key:  
                smaller_child = node.right
                
            if smaller_child.key < node.key:
                self.__swap(node, smaller_child)
                node = smaller_child
            else:
                break
            
    def __remove_last_node(self):
        if self.__size == 1:  
            self.__root = None
            return
        
        last = self.__get_last_node()
        if last.parent.left == last:
            last.parent.left = None
        else:
            last.parent.right = None
    
    def __get_last_node(self):
        if self.__size == 1:
            return self.__root
        
        path = bin(self.__size)[2:] 
        current = self.__root
        for b in path[1:]:  
            current = current.left if b == '0' else current.right
        return current
    
    def print_tree(self):
        def print_rec(node, level=0):
            if node is not None:
                print_rec(node.right, level + 1)
                print("    " * level + f"({node.key}, {node.data})")
                print_rec(node.left, level + 1)
        
        if self.__root is None:
            print("Heap vacío.")
        else:
            print_rec(self.__root)
    
    def is_empty(self):
        return self.__root is None
    
    def length(self):
        return self.__size


class PQueue:
    def __init__(self, data=None):
        self.heap = QHeap()
        self.size = 0
        if data:
            try:
                for item in data:
                    self.enqueue(item)
            except TypeError:
                self.enqueue(data)
    
    def enqueue(self, data):
        if hasattr(data, 'gravedad'): 
            key = -data.gravedad  
        elif isinstance(data, (int, float)):
            key = -data
        else:
            key = data  # fallback
        
        self.heap.enqueue(key, data)
        self.size += 1
    
    def dequeue(self):
        if self.is_empty():
            raise Exception("Dequeue from empty priority queue")
        _, data = self.heap.dequeue()
        self.size -= 1
        return data
    
    def peek(self):
        if self.is_empty():
            raise Exception("Peek from empty priority queue")
        return self.heap.peek()  
    
    def is_empty(self):
        return self.heap.is_empty()
    
    def length(self):
        return self.size
    
    def __repr__(self):
        return f"PQueue(size={self.size}, top={self.peek() if not self.is_empty() else None})"

class Set:
    def __init__(self):
        self.__capacity = 10
        self.__size = 0
        self.__buckets = [[] for _ in range(self.__capacity)]
    
    def add(self, element):
        bucket_index = self._hash(element)
        bucket = self.__buckets[bucket_index] 
        if element not in bucket:
            bucket.append(element)
            self.__size += 1
            
        if self.__size > self.__capacity * 0.7:
            self.__resize()
    
    def _hash(self, element, base=None):
        if not base:
            base = self.__capacity
            
        return hash(element) % base
    
    def __resize(self):
        new_capacity = self.__capacity * 2
        new_buckets = [[] for _ in range(new_capacity)]
        
        for bucket in self.__buckets:
            for e in bucket:
                bucket_index = self._hash(e, new_capacity)
                new_buckets[bucket_index].append(e)
        
        self.__capacity = new_capacity
        self.__buckets = new_buckets
    
    def remove(self, element):
        bucket_index = self._hash(element)
        bucket = self.__buckets[bucket_index]
        
        if element not in bucket:
            raise KeyError(f"{element}")
        
        bucket.remove(element)
        self.__size -= 1
        
    def discard(self, element):
        bucket_index = self._hash(element)
        bucket = self.__buckets[bucket_index]
        
        if element in bucket:
            bucket.remove(element)
            self.__size -= 1
    
    def pop(self):
        if self.__size == 0:
            raise KeyError("pop from empty set")
        for bucket in self.__buckets:
            if bucket:
                elem = bucket.pop()
                self.__size -= 1
                return elem
    
    def clear(self):
        self.__capacity = 10
        self.__size = 0
        self.__buckets = [[] for _ in range(self.__capacity)]
    
    def copy(self):
        new_set = Set()
        
        for b in self.__buckets:
            for e in b:
                new_set.add(e)
        return new_set
    
    def is_empty(self):
        return self.__size == 0
    
    def union (self, s2): 
        result = self.copy()
        for e in s2:
            result.add(e)
        return result
    
    def intersection(self, s2): 
        new_set = Set()
        
        for e in self:
            if e in s2:
                new_set.add(e)
                
        return new_set
        
    def __or__(self, s2):
        return self.union(s2)
    
    def __and__(self, s2):
        return self.intersection(s2)
    
    
    def __iter__(self): 
        for b in self.__buckets:
            for e in b:
                yield e


    def __contains__(self, element): 
        bucket_index = self._hash(element)
        bucket = self.__buckets[bucket_index]
        return element in bucket
    
    def __str__(self):
        if self.is_empty():
            return "{}"
        elements = [str(e) for e in self]
        return "{" + ", ".join(elements) + "}"
    
    def __len__(self): 
        return self.__size

class HashMap:
    def __init__(self, capacity=10, items=None):
        self.__capacity = capacity
        self.__size = 0
        self.__buckets = [[] for _ in range(self.__capacity)]
        
        if items:
            for k, v in items:
                self.put(k, v)

    def put (self, key, value):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self.__size += 1
        
        if self.__size > self.__capacity * 0.7:
            self.__resize()
        
    def __hash(self, element, base=None):
        if not base:
            base = self.__capacity
            
        return hash(element) % base

    def __resize(self):
        new_capacity = self.__capacity * 2
        new_buckets = [[] for _ in range(new_capacity)]
        
        for b in self.__buckets:
            for k, v in b:
                new_bucket_index = self.__hash(k, new_capacity)
                new_buckets[new_bucket_index].append((k, v))
        
        self.__capacity = new_capacity
        self.__buckets = new_buckets
    
    def __get(self, key):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]
        
        for k, v in bucket:
            if k == key:
                return v, True 
        
        return None, False        

    
    def get(self, key):
        v, found = self.__get(key)
        if found:
            return v    
        raise KeyError(f"Key {key} not found")
    
    def remove(self, key):
        bucket_index = self.__hash(key)
        bucket = self.__buckets[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.__size -= 1
                return
            
        raise KeyError(f"Key {key} not found")
    
    def __contains__(self, key):
        v, found = self.__get(key)
        return found
    
    def __iter__(self):
        for bucket in self.__buckets:
            for k, v in bucket:
                yield k, v
    
    def __len__(self):
        return self.__size
    
    def __str__ (self):
        return "{" + ", ".join (f"{k}: {v}" for k, v in self) + "}"
    
    def clear (self):
        self.__capacity = 10
        self.__size = 0
        self.__buckets = [[] for _ in range (self.__capacity)]
    
    def keys (self):
        return [k for k, v in self]
    
    def values (self):
        return [v for k, v in self]
    
    def items (self):
        return [(k, v) for k, v in self]


class DNode:
    def __init__(self, data):
        self.__data = data
        self.__next = None
        self.__prev = None
        
    def set_data(self, data):
        self.__data = data
    
    def get_data(self):
        return self.__data
    
    def set_next(self, node):
        self.__next = node
        
    def get_next(self):
        return self.__next
    
    def set_prev(self, node):
        self.__prev = node
    
    def get_prev(self):
        return self.__prev
    
class DoublyLinkedList:
    def __init__(self, data=None):
        self.__head = None
        self.__tail = None
        self.__size = 0  
    
        if data:
            try:
                for d in data:
                    self.append(d)
            except TypeError:
                self.append(data)
    
    def append(self, data):
        new_node = DNode(data)
        if self.is_empty():
            self.__head = self.__tail = new_node
        else:
            self.__tail.set_next(new_node)
            new_node.set_prev(self.__tail)
            self.__tail = new_node
        self.__size += 1
        
    def prepend(self, data):  
        new_node = DNode(data)
        if self.is_empty():
            self.__head = self.__tail = new_node
        else:
            self.__head.set_prev(new_node)
            new_node.set_next(self.__head)
            self.__head = new_node
        self.__size += 1
    
    def __remove_index(self, index):
        if index < 0 or index >= self.__size:
            raise IndexError("Index out of range")
        
        if index == 0:  
            self.__head = self.__head.get_next()
            if self.__head:
                self.__head.set_prev(None)
            else:
                self.__tail = None
        elif index == self.__size - 1:  
            self.__tail = self.__tail.get_prev()
            if self.__tail:
                self.__tail.set_next(None)
            else:
                self.__head = None
        else:  
            current = self.__head
            for _ in range(index):
                current = current.get_next()
            prev_node = current.get_prev()
            next_node = current.get_next()
            prev_node.set_next(next_node)
            next_node.set_prev(prev_node)
        
        self.__size -= 1
    
    def __remove_value(self, value):
        current = self.__head
        while current:
            if current.get_data() == value:
                if current == self.__head:  
                    self.__head = current.get_next()
                    if self.__head:
                        self.__head.set_prev(None)
                elif current == self.__tail:  
                    self.__tail = current.get_prev()
                    if self.__tail:
                        self.__tail.set_next(None)
                else:  
                    prev_node = current.get_prev()
                    next_node = current.get_next()
                    prev_node.set_next(next_node)
                    next_node.set_prev(prev_node)
                self.__size -= 1
                return  #
            current = current.get_next()
        raise ValueError(f"Value {value} not found")
        
    def remove(self, index=None, value=None):
        if self.is_empty():
            raise Exception("Removing from empty list")
        
        if index is not None and value is not None:
            raise Exception("Index and value must be given exclusively")
        
        if index is not None:
            self.__remove_index(index)
        elif value is not None:
            self.__remove_value(value)
        else:
            raise Exception("Must provide index or value")
    
    def clear(self):
        self.__head = None
        self.__tail = None
        self.__size = 0
    
    
    def sort(self, key=None):
        if self.is_empty() or self.length() < 2:
            return
        sorted_dll = DoublyLinkedList()
        current = self.__head
        while current:
            next_node = current.get_next()
            sorted_current = sorted_dll.__head
            prev = None
            val = key(current.get_data()) if key else current.get_data()
            while sorted_current and (key(sorted_current.get_data()) if key else sorted_current.get_data()) < val:
                prev = sorted_current
                sorted_current = sorted_current.get_next()
            current.set_next(sorted_current)
            current.set_prev(prev)
            if sorted_current:
                sorted_current.set_prev(current)
            if prev:
                prev.set_next(current)
            else:
                sorted_dll.__head = current
            if not current.get_next():
                sorted_dll.__tail = current
            current = next_node
        self.__head = sorted_dll.__head
        self.__tail = sorted_dll.__tail
        
    def is_empty(self):
        return self.__head is None
    
    def length(self):
        return self.__size
    
    def __iter__(self):  
        current = self.__head
        while current:
            yield current.get_data()
            current = current.get_next()
    
    def __repr__(self):  
        if self.is_empty():
            return "Empty List"
        return " <-> ".join(str(d) for d in self)