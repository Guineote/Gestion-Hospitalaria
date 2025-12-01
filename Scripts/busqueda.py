from collections import Counter

class Cadenas:
    def __init__(self):
        pass
    
    @staticmethod
    def levenshtein(s1, s2):
        dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        
        for i in range(1, len(s1) + 1):
            dp[i][0] = i
            
        for j in range(1, len(s2) + 1):
            dp[0][j] = j

        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,      # eliminación
                    dp[i][j - 1] + 1,      # inserción
                    dp[i - 1][j - 1] + cost  # sustitución
                )

        return dp[-1][-1]

    @staticmethod
    def hamming(s1, s2):
        if len(s1) != len(s2):
            raise Exception("Strings must be equal length")
        return sum(s1[i] != s2[i] for i in range(len(s1)))

    @staticmethod
    def bmh(text, pattern):
        n, m = len(text), len(pattern)
        if m == 0:
            return 0
        if n < m:
            return -1
        
        bad_chars = {}
        for i in range(m - 1):
            bad_chars[pattern[i]] = m - 1 - i
        
        i = 0
        while i <= n - m:
            j = m - 1
            while j >= 0 and text[i + j] == pattern[j]:
                j -= 1
            if j < 0:
                return i
            shift = bad_chars.get(text[i + m - 1], m)
            i += shift
        
        return -1

    @staticmethod
    def build_kmp(pattern):
        m = len(pattern)
        pi = [0] * m
        j = 0
        for i in range(1, m):
            while j > 0 and pattern[i] != pattern[j]:
                j = pi[j - 1]
            if pattern[i] == pattern[j]:
                j += 1
            pi[i] = j
        return pi

    @staticmethod
    def kmp(text, pattern):
        n, m = len(text), len(pattern)
        if m == 0:
            return 0
        if n < m:
            return -1
        
        pi = Cadenas.build_kmp(pattern) 
        q = 0
        for i in range(n):
            while q > 0 and text[i] != pattern[q]:
                q = pi[q - 1]
            if text[i] == pattern[q]:
                q += 1
            if q == m:
                return i - m + 1
        return -1

    @staticmethod
    def find(text, pattern):
        return Cadenas.kmp(text, pattern)
    
    @staticmethod
    def parse_campos(text):
        campos = {}
        current_key = ""
        current_val = ""
        reading_key = True
        i = 0
        n = len(text)

        while i < n:
            c = text[i]

            # Detectar ": " como separador clave/valor
            if reading_key and i + 1 < n and text[i] == ':' and text[i+1] == ' ':
                reading_key = False
                i += 2
                continue

            # Detectar ", " como separador de campos
            if not reading_key and i + 1 < n and text[i] == ',' and text[i+1] == ' ':
                campos[current_key] = current_val
                current_key = ""
                current_val = ""
                reading_key = True
                i += 2
                continue

            if reading_key:
                current_key += c
            else:
                current_val += c

            i += 1

        # guardar el último campo
        if current_key:
            campos[current_key] = current_val

        return campos


    @staticmethod
    def extract_between(text, p1, p2):
        i1 = Cadenas.find(text, p1)
        if i1 == -1:
            return ""
        i1 += len(p1)

        i2 = Cadenas.find(text, p2)
        if i2 == -1:
            return ""

        # Recorrer manualmente para obtener substring
        result = ""
        for i in range(i1, i2):
            result += text[i]
        return result

    
class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

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

def build_huffman_tree(text):
    if not text:
        return None
    
    freq = Counter(text)
    heap = QHeap()
    for char, f in freq.items():
        node = HuffmanNode(char, f)
        heap.enqueue(f, node) 
    
    while heap.length() > 1:
        _, left = heap.dequeue() 
        _, right = heap.dequeue()
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heap.enqueue(merged.freq, merged)
    
    _, root = heap.dequeue()  
    return root

def generate_codes(node, current_code="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return codes
    
    if node.char is not None:
        codes[node.char] = current_code
        return codes
    
    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)
    return codes

def huffman_encode(text):
    if not text:
        return "", {}
    
    tree = build_huffman_tree(text)
    codes = generate_codes(tree)
    encoded = "".join(codes[char] for char in text)
    return encoded, codes

def huffman_decode(encoded, codes):
    reverse_codes = {code: char for char, code in codes.items()}
    decoded = ""
    current_code = ""
    for bit in encoded:
        current_code += bit
        if current_code in reverse_codes:
            decoded += reverse_codes[current_code]
            current_code = ""
    return decoded