# Implementation inheritance is bad - the fragile base class problem

One can argue, that implementation inheritance should not be supported at all
in any same object-oriented programming language.
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
        self.greet_casual()
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
However, support for inheriting implementation allows for it to happen.

If you are unlucky, and the programming language you are using does support it,
you might still want to try to avoid that feature.
