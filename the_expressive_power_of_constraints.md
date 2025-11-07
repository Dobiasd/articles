# The expressive power of constraints

Since we write code not primarily for the machine to execute, but mainly for the human reader to understand, we want our code to easily state what it does. One great way to achieve this is to let it state what it does *not*! When somebody looks into existing source code, initially, they don't know which of the endless things that could be going on, actually are. Reading the code allows them to narrow down their mental model to exactly one (hopefully the correct) possibility. Constraints can help a lot with that.


## Some examples


### Type annotations (trivial)

Something like (fantasy language syntax)

```
function switch_something_on_or_off(x: Any)
```

allows `x` to be anything. It's better to restrict it

```
function switch_something_on_or_off(x: int)
```

and if we only need "on" and "off", using a type that only allows these two options is even better:

```
function switch_something_on_or_off(x: bool)
```

By reducing the cardinality of the set (the type), we reduce the possible states the program can have.


### Immutability (simple)

When a variable (primitive or a complex object) is declared as constant, the reader immediately knows that it will never be mutated, because the type system guarantees it.


### Private fields/methods (basic)

Every non-public thing in a class is guaranteed not to be accessed from the outside.


### Principle of Least Knowledge (classic)

Given

```
class Foo
    name: string
    age: int
    ...
```

this

```
function say_hello_to(name: string)
    print("Hello, {name}.")
```

is better than

```
function say_hello_to(foo: Foo)
    print("Hello, {foo.name}.")
```

because passing only the data that the function actually needs to operate already tells the reader about all the things that the function does not do, e.g., doing something with `.age`, etc.


### Avoiding generic loops (functional)

Given a list

```
xs = [1, 23, 42]
```

and we want to only keep the even elements.

```
ys = []
i = 0
while i < length(xs)
    if is_even(xs[i])
        ys.append(xs[i])
    i += 1
```

is one way to do it, but obviously not the most obvious one.

```
ys = []
for x in xs:
    if is_even(x)
        ys.append(x)
```

already is better, because the `for` header already guarantees that no element of `xs` will be skipped or visited out of order by this loop. In the `while` version above, one needed to read the loop body to know this.

A declarative

```
ys = filter(is_even, xs)
```

is even better, not just because it's shorter than the imperative options, but it guarantees that `ys` will never contain any element that was not present in `xs`. For this, one does not even need to know what `is_even` does. In the `for` example, one needed to look into the loop body to learn about that restriction.


### Abstraction with generics (fancier)

If we implement a `filter` function like the one used above, we could have

```
function filter(predicate: (int -> bool), xs: List[int]) -> List[int]
    ...
```

however, the reader might wonder why it's specific to this list-element type, i.e., does the function utilize some special properties of `int`s?

A generic version like this

```
function filter<T>(predicate: (T -> bool), xs: List[T]) -> List[T]
    ...
```

on the other hand, states that the function does not do anything that is specific to some list-element type. Since the function knows nothing about `T` except what the type variable guarantees (in this case, just that it's some type), it cannot perform int-specific operations like arithmetic or comparison. In this case, it's somewhat the other way around than in the "type annotation" example: The less we know about the parameter type, the fewer things the function can possibly do.


### Library/tool selection (beyond code)

When using some library (or any other tool), using one that is specialized for the task at hand can be a good idea. If some huge framework is pulled in to do something simple, the reader might ask themselves why this is the case, and that maybe some other things are happening in the code that they don't yet know about. By using a lib/tool that does just one thing, the possibilities are restricted, which is (according to this article) good for readability.

For example, if you just need to parse dates, using a dedicated date-parsing library immediately tells the reader that only date parsing is happening. Suppose instead you import a full web framework that happens to include date utilities. In that case, the reader might wonder whether HTTP requests, database operations, or other framework features are also being used elsewhere in the code.


## Conclusion

We've seen a common pattern: By restricting what our code *can* do, we make it clearer what our code *does* do. Whether through types, immutability, or specialized abstractions, constraints communicate intent. The reader spends less time wondering about possibilities and more time understanding reality.
