# Implementation inheritance is bad - the fragile base class problem

One could argue, that implementation inheritance should not be supported at all
by any sane object-oriented programming language.
It should only be allowed to inherit (in the sense of "implement") interfaces.

A common example in favor of this argument is the so-called "fragile base class problem".

Imagine you have written the following class (using Python as an example here):

```python
class Person:
    def __init__(self, name):
        self.name = name

    def say(self, text):
        print(f'{self.name}: {text}')

    def greet_casual(self):
        self.say("Hi.")

    def greet_formal(self):
        self.say("Hi.")
        self.say("How are you?")
```

And at some point you decide to change it like so:

```python
class Person:
    def __init__(self, name):
        self.name = name

    def say(self, text):
        print(f'{self.name}: {text}')

    def greet_casual(self):
        self.say("Hi.")

    def greet_formal(self):
        self.greet_casual()  # <--- Here is the change.
        self.say("How are you?")
```

This should be totally OK. It's fully compatible.
Neither the interface nor the functionality changed.
All unit tests are green.

But with this change, you accidentally broke some other part of the project.
A class is inheriting from your class:

```python
class VeryPolitePerson(Person):
    def greet_casual(self):
        self.greet_formal()


p = VeryPolitePerson("John")
p.greet_casual()
```

Before your change, this worked fine. But now it results in the following:

```text
RecursionError: maximum recursion depth exceeded
```

The occurrence of such a problem should not even be possible.
However, support for inheriting implementation and method overriding
allows for it to happen.

OK, "It's only method overriding, which is evil." you might say.
"Programming languages should make methods `final` or non-`virtual` by default,
so users have to consciously opt-in to this feature when writing a class,
which somebody might inherit from."

Yes, but even without method overriding,
just with implementation inheritance only,
innocent behavior can lead to mean bugs.

Let's say we write the following (this time with type annotations for clarity):

```python
# library code
from typing import List

class ContainerBase:
    def __init__(self, initial_values: List[int]) -> None:
        self._values = initial_values
```

and then we add something:

```python
# library code
from typing import List

class ContainerBase:
    def __init__(self, initial_values: List[int]) -> None:
        self._values = initial_values

    def clear(self) -> None:
        self._values = []


def do_something_with_container_and_clear(container: ContainerBase) -> None:
    # do something
    container.clear()
```

However, in between those two steps, somebody else wrote that:

```python
# client code

class SummingContainer(ContainerBase):
    def __init__(self) -> None:
        super(SummingContainer, self).__init__([])
        self.sum = 0

    def add(self, value: int) -> None:
        self.sum += value
        self._values.append(value)
```

Our new function (`ContainerBase.clear`) will break an invariant
of `SummingContainer`, i.e., `SummingContainer.sum` will no longer
be guaranteed to reflect the sum of all numbers in the container.

Thus `SummingContainer` can not be used with
`do_something_with_container_and_clear`,
This violates the [Liskov substitution principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle),
which is bad.

A language not allowing implementation inheritance
(or at least making every class `final` by default)
could prevent this from happening.

Code reuse can be achieved by other means.
Composition (with [delegation](https://en.wikipedia.org/wiki/Delegation_pattern)) can provide one viable way to do so.
