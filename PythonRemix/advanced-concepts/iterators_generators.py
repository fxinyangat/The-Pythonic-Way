_iterator = iter([1,2,3,4])

while True:
    try:
        item = next(_iterator)
        # print(item)
    except StopIteration:
        break
    
class CountDown:
    def __init__(self, start:int):
        self.current = start
        
    def __iter__(self):
        return self
    
    def __next__(self)-> int:
        if self.current <= 0:
            raise StopIteration #signnals the end of the loop
        
        value = self.current
        self.current -= 10
        
        return value
    

countdown = CountDown(500)

for number in countdown:
    pass
    # print(number)
    
    
class CountUp:
    def __init__(self, start_number,end_number):
        self.end_number = end_number
        self.current = start_number
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.end_number:
            raise StopIteration
        
        value = self.current
        self.current += 1
        
        return value
    

countup = CountUp(0,100)

for number in countup:
    # print(number)
    pass
    
class StatementPages:
    def __init__(self, transactions:list, page_size:int):
        self._transactions = transactions
        self._pagesize = page_size
        self._index = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index >= len(self._transactions):
            raise StopIteration
        
        current_page = self._transactions[self._index : self._index + self._pagesize]
        self._index += self._pagesize
        
        return current_page
    

transactions = [f"INV_{i}" for i in range(100)]

pages = StatementPages(transactions=transactions, page_size=5)

for page in pages:
    # print(page)
    pass

# GENERATORS - same statment-print example

def  statement_pages(transactions:list, page_size:int, i:int):
    while i <= len(transactions):
        yield transactions[i: i+page_size]
        i += page_size
        
    # for i in range(0, len(transactions), page_size):
    #     yield transactions[i: i+page_size]
        
        
transactions = [f"INV-{i}" for i in range(50+1)]
for page in statement_pages(transactions, page_size=5,i = 0):
    print(page)
    # pass


def count_down_generator(start: int):
    current = start
    while current > 0:
        yield current
        current -= 1
        
 
for number in count_down_generator(20):
    # print(number)
    pass


import sys
def balance_list(n):
    return [i*1.05 for i in range(n)]

def balance_gen(n):
    for i in range(n):
        yield i*1.05
        
lst = balance_list(1_000_000)
gen = balance_gen(1_000_000)

print(sys.getsizeof(lst))   # ~8,000,000 bytes — the whole list
print(sys.getsizeof(gen))   # ~200 bytes — just the generator object

"""Generator expressions
Just as a list comprehension builds a list, a generator expression 
builds a generator — same syntax, but with parentheses instead of square brackets. 
Lazy, memory-efficient, one value at a time."""

# List comprehension — builds the whole list immediately
squares_list = [x**2 for x in range(1_000_000)]   # ~8 MB in memory

# Generator expression — lazy, nothing computed yet
squares_gen = (x**2 for x in range(1_000_000))    # ~200 bytes

# Perfect for feeding aggregate functions that consume one at a time
total = sum(x**2 for x in range(1_000_000))       # no intermediate list built
print(total)

# Filtering large data without ever holding it all
# large_deposits = (t for t in transaction_stream() if "deposit" in t)

#REALISTIC USECASE : READING LARGE FILE

"""The canonical production pattern — process a file too large to load into memory, line by line:
pythondef read_large_statement(filepath: str):
       with open(filepath) as f:
        for line in f:                    # file objects are themselves iterators
            line = line.strip()
            if not line:
                continue
            date, amount, description = line.split(",", 2)
            yield {
                "date": date,
                "amount": float(amount),
                "description": description,
            }"""

# Process a 10 GB file using constant memory
"""total_deposits = sum(
    txn["amount"]
    for txn in read_large_statement("statements.csv")
    if txn["amount"] > 0
)
The file is read one line at a time, each line parsed and yielded, then discarded before the next is read. Memory stays flat regardless of file size.

The four things to always remember
A generator is a one-shot iterator. Once exhausted it's done — you can't rewind it. If you need to iterate twice, either build a list from it or call the generator function again to get a fresh one.
Nothing runs until you pull. Calling a generator function doesn't execute its body — it returns a paused generator. Execution advances only on next() or a for loop.
Use generator expressions ( ) over list comprehensions [ ] when feeding aggregates or loops. You get the same result with near-zero memory when you don't need the materialised list.
yield from delegates cleanly. When composing or chaining generators, yield from other_gen() is clearer and faster than looping and re-yielding manually.

Next — itertools deep-dive, coroutines and send(), or async generators?"""

# GENERATORS AS COROUTINES

def echo_coroutine():
    while True:
        recieved = yield
        print(f"Recieved: {recieved}")
        
        if recieved == 'withdraw':
            print("Running Withdrawal")
        elif recieved == 'deposit':
            print("Running Deposit")
            
        
coro = echo_coroutine()

next(coro)

coro.send("deposit")

coro.send("withdraw")