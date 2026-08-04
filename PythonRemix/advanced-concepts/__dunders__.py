# Got it — keeping it plain from here on.

# ---

# ## The Python data model

# The core idea: Python doesn't hardcode operators. When you write `len(x)`, `x + y`, `x[0]`, or `for item in x`, Python calls a special method on your object. These methods are the **data model** — also called dunder (double-underscore) methods. Implement them and your class plugs into the language itself.

# The analogy: think of Python as a bank's operating system. Every branch (your class) that wants to support standard operations — deposits, withdrawals, comparisons, printing statements — must implement a standard interface the bank defined. The bank's OS calls those interface methods; it doesn't care how each branch implements them internally.

# ---

# ## Representation: `__repr__` and `__str__`

# `__repr__` is for developers — unambiguous, ideally copy-pasteable. `__str__` is for end users — readable. `print()` calls `__str__`; the REPL calls `__repr__`. If you only define one, define `__repr__` — Python falls back to it for both.

# ```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"

    def __str__(self):
        return f"{self.owner}'s account — ${self.balance:,.2f}"

acc = BankAccount("Xavier", 1500.50)
print(repr(acc))  # BankAccount(owner='Xavier', balance=1500.5)
print(acc)        # Xavier's account — $1,500.50
# ```

# ---

# ## Equality and hashing: `__eq__` and `__hash__`

# By default `==` checks identity (same object in memory). Define `__eq__` to check value equality instead. The rule: if you define `__eq__`, Python sets `__hash__` to `None` — making your object unhashable (can't be used in a set or dict key). Define `__hash__` too if you need that.

# ```python
class BankAccount:
    def __init__(self, account_id: str, balance: float):
        self.account_id = account_id
        self.balance = balance

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self.account_id == other.account_id

    def __hash__(self):
        return hash(self.account_id)  # hash on the immutable identifier

a1 = BankAccount("ACC001", 1000)
a2 = BankAccount("ACC001", 9999)  # same ID, different balance
print(a1 == a2)   # True — same account ID
seen = {a1, a2}
print(len(seen))  # 1 — treated as duplicates in a set
# ```

# Return `NotImplemented` (not `False`) when the type is wrong — it tells Python to try the other operand's `__eq__` instead.

# ---

# ## Arithmetic: `__add__`, `__sub__`, `__iadd__`

# `__add__` handles `a + b`. `__iadd__` handles `a += b` (in-place). If you don't define `__iadd__`, Python falls back to `__add__` and rebinds the name — fine for immutable types, but defining it explicitly is cleaner for mutable ones.

# ```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance

    def __add__(self, amount: float):
        # Returns a NEW account — like a ledger entry
        return BankAccount(self.owner, self.balance + amount)

    def __sub__(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        return BankAccount(self.owner, self.balance - amount)

    def __iadd__(self, amount: float):
        # Mutates in-place — like a real deposit
        self.balance += amount
        return self  # must return self

    def __repr__(self):
        return f"BankAccount({self.owner!r}, {self.balance})"

acc = BankAccount("Xavier", 1000)
new_acc = acc + 500     # new object
print(new_acc)          # BankAccount('Xavier', 1500)
print(acc)              # BankAccount('Xavier', 1000) — unchanged

acc += 200              # mutates in place
print(acc)              # BankAccount('Xavier', 1200)
# ```

# ---

# ## Comparisons: `__lt__`, `__le__`, `__gt__`, `__ge__`

# These power `<`, `<=`, `>`, `>=` and — critically — `sorted()`. You can implement all four, or use `functools.total_ordering` to derive the rest from just `__eq__` and `__lt__`.

# ```python
from functools import total_ordering

@total_ordering
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance

    def __eq__(self, other):
        return self.balance == other.balance

    def __lt__(self, other):
        return self.balance < other.balance

    def __repr__(self):
        return f"{self.owner}(${self.balance})"

accounts = [
    BankAccount("Alice", 500),
    BankAccount("Xavier", 2000),
    BankAccount("Bob", 1200),
]

print(sorted(accounts))          # [Alice($500), Bob($1200), Xavier($2000)]
print(max(accounts))             # Xavier($2000)
print(accounts[0] < accounts[1]) # True
# ```

# ---

# ## Container protocol: `__len__`, `__getitem__`, `__contains__`

# Implement these and your object works with `len()`, indexing `[]`, and `in`. This is how you make a custom portfolio object feel like a built-in sequence.

# ```python
class Portfolio:
    def __init__(self, accounts: list):
        self._accounts = accounts

    def __len__(self):
        return len(self._accounts)

    def __getitem__(self, index):
        return self._accounts[index]   # supports slicing too: portfolio[1:3]

    def __contains__(self, account):
        return account in self._accounts

    def __iter__(self):
        return iter(self._accounts)    # makes it work in for loops

portfolio = Portfolio([
    BankAccount("Alice", 500),
    BankAccount("Xavier", 2000),
])

print(len(portfolio))         # 2
print(portfolio[0])           # Alice($500)
for acc in portfolio:
    print(acc)                # iterates naturally
alice = BankAccount("Alice", 500)
print(alice in portfolio)     # True (uses __eq__ we defined)
# ```

# ---

# ## Boolean truth: `__bool__`

# Controls `if obj:`. Python falls back to `__len__` (truthy if non-zero) if `__bool__` isn't defined. Define it explicitly when you want a clear semantic.

# ```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance

    def __bool__(self):
        return self.balance > 0   # account is "truthy" only if it has money

acc = BankAccount("Xavier", 0)
if not acc:
    print("Account is empty")    # prints this

acc2 = BankAccount("Alice", 500)
if acc2:
    print("Active account")      # prints this
# ```

# ---

# ## Callable objects: `__call__`

# Makes an instance callable like a function. Useful for stateful callables — things that behave like functions but remember state.

# ```python
class TransactionFee:
    """A fee calculator that remembers its rate."""
    def __init__(self, rate: float):
        self.rate = rate
        self.total_collected = 0.0

    def __call__(self, amount: float) -> float:
        fee = amount * self.rate
        self.total_collected += fee
        return fee

charge_fee = TransactionFee(0.02)  # 2% fee

print(charge_fee(1000))  # 20.0
print(charge_fee(500))   # 10.0
print(charge_fee.total_collected)  # 30.0  — state persisted
# ```

# ---

# ## `__del__`: the finalizer (use carefully)

# Called when the object's reference count hits zero. Not a destructor in the C++ sense — Python doesn't guarantee *when* it runs. Use context managers (`__enter__`/`__exit__`) for deterministic cleanup. `__del__` is only for logging/debugging or truly last-resort cleanup.

# ```python
class BankAccount:
    def __init__(self, owner):
        self.owner = owner

    def __del__(self):
        print(f"Account for {self.owner} garbage collected")

acc = BankAccount("Xavier")
del acc   # prints: Account for Xavier garbage collected
# ```

# ---

# ## The full picture

# | Operation | Dunder called |
# |---|---|
# | `repr(x)` | `__repr__` |
# | `print(x)` / `str(x)` | `__str__` → falls back to `__repr__` |
# | `x == y` | `__eq__` |
# | `hash(x)` | `__hash__` |
# | `x + y` | `__add__` |
# | `x += y` | `__iadd__` → falls back to `__add__` |
# | `x < y` | `__lt__` |
# | `len(x)` | `__len__` |
# | `x[i]` | `__getitem__` |
# | `i in x` | `__contains__` → falls back to iterating |
# | `for i in x` | `__iter__` → falls back to `__getitem__` |
# | `if x:` | `__bool__` → falls back to `__len__` |
# | `x()` | `__call__` |
# | object freed | `__del__` |

# The key insight: Python's operators aren't magic — they're just well-named method calls. Every time you write `a + b`, Python is literally calling `type(a).__add__(a, b)`. Once that clicks, the whole data model becomes a single coherent idea rather than a list of special cases to memorize.

# What's next — descriptors, `__getattr__`, or ABCs/Protocol?
