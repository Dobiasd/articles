# Avoid methods to reduce coupling

The following uses Python only as an example to show some code. The logic applies in many other programming languages too.

## Global variables (make things complicated, yada yada yada)

```python3
def foo():
    x = 21
    bar()
    print(2 * x)

def bar():
    # imagine something very long nobody wants to read
    pass

foo()
```

This is fine. No matter what `bar` does (ignoring exceptions, infinite loops, etc.), we know that `foo` will print `42`. `bar` can not influence that by changing the value of `x`.

This would be different if `x` were a global variable:

```python3
x = 21

def foo():
    bar()
    print(2 * x)

def bar():
    # imagine something very long nobody wants to read
    pass

foo()
```

`bar` could change the value of x, so we're not sure what `foo` will print.

So, of course, if not really needed, we try to avoid global variables (**rule 1**).


## Nested functions

```python3
def foo():
    x = 21

    def bar():
        # imagine something very long nobody wants to read
        pass

    bar()
    print(2 * x)

foo()
```

With `bar` being inside `foo`, here, again, `bar` could change the value of x (e.g., `nonlocal x; x = 1`), so we're not sure what `foo` will print.

So, if not really needed, we should try to avoid nested functions (**rule 2**).


## Methods

```python3
class Thing():
    def __init__(self):
        self.x = 21

    def foo(self):
        self.bar()
        print(2 * self.x)

    def bar(self):
        # imagine something very long nobody wants to read
        pass

my_thing = Thing()
my_thing.foo()
```

With `bar` being inside `Thing`, here, again, `bar` could change the value of x (e.g., `self.x = 1`), so we're not sure what `foo` will print.

So, in case `bar` does not use `self`, we should move it out of `Thing` and make it a free function.

But even if it does use `self.something`, like this

```python3
class Thing():
    def __init__(self):
        self.x = 21
        self.y = 2

    def foo(self):
        self.bar()
        print(self.y * self.x)

    def bar(self):
        print(self.y)

my_thing = Thing()
my_thing.foo()
```

we should move it out of `Thing`

```python3
class Thing():
    def __init__(self):
        self.x = 21
        self.y = 2

    def foo(self):
        bar(self.y)
        print(self.y * self.x)

def bar(y):
    print(y)

my_thing = Thing()
my_thing.foo()
```

or, make it static (which basically is the same thing in this context, despite the changed syntax at the call site)

```python3
class Thing():
    def __init__(self):
        self.x = 21
        self.y = 2

    def foo(self):
        Thing.bar(self.y)
        print(self.y * self.x)

    @staticmethod
    def bar(y):
        print(y)

my_thing = Thing()
my_thing.foo()
```

because this:
- gives us the guarantee that `bar` will not mutate any of the member variables of our `Thing`.
- makes the dependency (`bar` depends on a value for `y`) visible and explicit.
- shows the reader that `bar` does not depend on something else from `Thing`.

It simply makes it easier to reason about our code, because `bar` no longer is potentially coupled to all member variables (like a free function is couples to global variables). Also testing `bar` will be simpler, because we don't need to instantiate a `Thing` object anymore, just to invoke `bar`.

So, if not really needed, we should try to avoid (non-static) methods (**rule 3**) too!

When no fancy OOP stuff (implementation inheritance/polymorphism) is needed, the best idea might be to use the class only as a plain struct and keep the logic out. `Thing` can now even become a `NamedTuple`.

```python3
from typing import NamedTuple

class Thing(NamedTuple):
    x: int = 21
    y: int = 2
    z: int = 3

# Or use a normal class and @staticmethod
def foo(x, y):
    bar(y)
    print(y * x)

def bar(y):
    print(y)

my_thing = Thing()
foo(my_thing.x, my_thing.y)
```

## Conclusion

When using methods functions, we suffer from a similar problem as we do when using nested functions or global variables, i.e., we lose guarantees about what a function will definitely **not** do. And the more of such guarantees we have, the lower the cognitive load is when maintaining (understanding/fixing/refactoring/extending) the code later. :-)