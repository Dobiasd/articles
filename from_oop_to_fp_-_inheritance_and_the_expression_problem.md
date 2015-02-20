# From Object Oriented Programming to Functional Programming - Inheritance and the Expression Problem

During my currently running undertaking of learning
functional programming (FP) I stumbled upon a challange related to the
[expression problem](http://c2.com/cgi/wiki?ExpressionProblem) while
working on a small
[Elm](http://elm-lang.org/)
[project](https://github.com/Dobiasd/Demoscene-Concentration).
Let's say you write a platform game with different types of enemies.
They all have to respond to certain actions, like being jumped on etc.,
in distinct ways. Also, we want to be able to store them together
in a homogeneous list, so we give them a common base class which defines
their interface. The according class diagram to this could look as follows:

```
             ---------
             | Enemy |
             ---------
                 ^
                 |
    -------------^------------
    |          |             |
 -------   ----------   -----------
 | Boo |   | Goomba |   | Wiggler |
 -------   ----------   -----------
```
The functions every class derived from `Enemy` has to implement
could be `walk`, `jumpedOn`, `spinJumpedOn`, `getPosition`.
The first three would be non const member functions, they mutate the object.
The last one would be a const function, it only returns a property.

To make everything a bit easier,
let's say we just have two derived subclasses:

```
    --------
    | Base |
    --------
        ^
        |
   -----^-----
   |         |
-------   -------
| Foo |   | Bar |
-------   -------
```
And we only have one mutating function `step`
and one constant function `display`.


## C++ solution
Since C++ supports Object Oriented Programming (OOP) we can have a look
at a typical solution with it.

First the interface of the abstract base class (pure virtual).
```c++
// Base.h
#ifndef BASE_H
#define BASE_H
#include <string>
class Base
{
    public:
        virtual ~Base() {}
        virtual void step(int delta) = 0;
        virtual std::string display() const = 0;
};
#endif
```

Now the two derived classes:
```c++
// Foo.h
#ifndef FOO_H
#define FOO_H
#include "Base.h"
class Foo : public Base
{
    public:
        Foo(const int i) : intVal_(i) {}
        // Add delta to internal state.
        void step(int delta) override { intVal_ += delta; }
        std::string display() const override { return std::to_string(intVal_); }
    private:
        int intVal_;
};
#endif
```

```c++
// Bar.h
#ifndef BAR_H
#define BAR_H
#include "Base.h"
class Bar : public Base
{
    public:
        Bar(const std::string& s) : strVal_(s) {}
        // Concat delta as string to internal state.
        void step(int delta) override { strVal_ += std::to_string(delta); }
        std::string display() const override { return strVal_; }
    private:
        std::string strVal_;
};
#endif
```

And finally some code to test all this:

```c++
// main.cpp
#include "Bar.h"
#include "Foo.h"
#include <algorithm>
#include <iostream>
#include <iterator>
#include <memory>
#include <vector>

using namespace std;

typedef unique_ptr<Base> BasePtr;
typedef vector<BasePtr> BasePtrVec;

// Steps every object in l by 1.
void stepAll(BasePtrVec& l)
{
    for (BasePtr& basePtr : l)
    {
        basePtr->step(1);
    }
}

// Displays all objects in l beneath each other.
void displayAll(BasePtrVec& l)
{
    // First get display strings from every object.
    vector<string> dss;
    transform(begin(l), end(l), back_inserter(dss), [](BasePtr& basePtr)
    {
        return basePtr->display();
    });

    // Copy display strings to cout.
    copy(begin(dss), end(dss), ostream_iterator<string>(cout, "\n"));
}

int main()
{
    // Fill a vector with base class pointers to derived instances.
    BasePtrVec l;
    l.push_back(BasePtr(new Foo(0)));
    l.push_back(BasePtr(new Bar("")));

    // Step every object two times.
    stepAll(l);
    stepAll(l);

    // Show result.
    displayAll(l);
}
```

The output of this program is:
```
2
11
```


## A typical Haskell implementation

Since one requirement for a solution is the ability to store objects
of different subtypes in the same list,
[typeclasses](http://codepad.org/6boPlYTK) are not the answer here.
It also would be cool if it can be used in
[Elm](http://elm-lang.org/learn/Syntax.elm) too, so let us
[avoid](http://lukepalmer.wordpress.com/2010/01/24/haskell-antipattern-existential-typeclass/)
[existential types](http://www.haskell.org/haskellwiki/Existential_type)
for now. ^_-)

So the usual haskell approach could look like this:

```haskell
-- Base.hs
module Base where

data Base = Foo Int | Bar String

step :: Base -> Int -> Base

-- Add delta to internal state.
step (Foo intVal) delta = Foo $ intVal + delta

-- Concat delta as string to internal state.
step (Bar strVal) delta = Bar $ strVal ++ show delta

display :: Base -> String
display (Foo intVal) = show intVal
display (Bar strVal) = strVal
```

```haskell
-- Main.hs
import Data.List
import Base

-- Steps every object in l by 1.
stepAll :: [Base] -> [Base]
stepAll l = map (\b -> step b 1) l

-- Displays all objects in l beneath each other.
displayAll :: [Base] -> IO ()
displayAll l = putStrLn $ concat (intersperse "\n" $ map display l)

main :: IO ()
main =
    let
        -- Fill a list with "derived instances".
        l :: [Base]
        l = [Foo 0, Bar ""]

        -- Step every object two times.
        l' = (stepAll . stepAll) l
    in
        -- Show result.
        displayAll l'
```

It's nice and terse and does everything we want.


## The expression problem

```
                              ------------------
-----------         /----->   | A1, A2, B1, B2 |
| A1 | A2 |        /          ------------------
-----------   ----<
| B1 | B2 |        \          ------------------
-----------         \----->   | A1, B1, A2, B2 |
                              ------------------
```

The subtle difference only gets obvious when you want to add new
subclasses/subtypes or new functions to our software:
- **Only the OOP solution makes it easy to add a new class.**
We just have to create one and all our typing will happen in this one file.
- **Only the FP solution makes it easy to add a new function.**
We just have to write it beneath `step` and `display`.

In case `Base.hs` would get too long in our Haskell version
we could split in into `Step.hs` and `Display.hs`.
But still, if we would like to add a new object, we would have to edit
*all* the functions. There would not be one single point to do it.
Vice versa, the OOP solution (without [visitor pattern](http://en.wikipedia.org/wiki/Visitor_pattern)) would make it difficult to add a new
function. We would have to edit the files of all derived classes.

Perhaps this is not a big surprise. In OOP our code is structured by classes,
in FP it is structured by functions.

Depending on whether we more often have to add classes or function,
one or the other approach would be preferable.

But what if we want to have the OOP advantage but still use a purely
functional language? Let's see if we can manage this.


## A naive Haskell attempt

A first attempt could be to move the functions into separate modules for
every "class".

```haskell
-- Base.hs
module Base where

data Base = Foo Int | Bar String
```

```haskell
-- BaseFunctions.hs
module BaseFunctions where

import Base
import Foo
import Bar

-- Dispatch by type and forward to appropriate moduel.
step :: Base -> Int -> Base
step foo@(Foo intVal) = stepFoo foo
step bar@(Bar strVal) = stepBar bar

display :: Base -> String
display foo@(Foo intVal) = displayFoo foo
display bar@(Bar strVal) = displayBar bar
```

```haskell
-- Foo.hs
module Foo where

import Base

-- Add delta to internal state.
stepFoo :: Base -> Int -> Base
stepFoo (Foo intVal) delta = Foo $ intVal + delta

displayFoo :: Base -> String
displayFoo (Foo intVal) = show intVal
```

```haskell
-- Bar.hs
module Bar where

import Base

-- Concat delta as string to internal state.
stepBar :: Base -> Int -> Base
stepBar (Bar strVal) delta = Bar $ strVal ++ show delta

displayBar :: Base -> String
displayBar (Bar strVal) = strVal
```

```haskell
-- Main.hs
import Data.List
import Base
import BaseFunctions
import Foo
import Bar

-- Steps every object in l by 1.
stepAll :: [Base] -> [Base]
stepAll l = map (\b -> step b 1) l

-- Displays all objects in l beneath each other.
displayAll :: [Base] -> IO ()
displayAll l = putStrLn $ concat (intersperse "\n" $ map display l)

main :: IO ()
main =
    let
        -- Fill a list with "derived instances".
        l :: [Base]
        l = [Foo 0, Bar ""]

        -- Step every object two times.
        l' = (stepAll . stepAll) l
    in
        -- Show result.
        displayAll l'
```

Our Main.hs stayed the same. The functionality for our foo type
is now in Foo.hs and everything for our bar type is in Bar.hs.
This is a bit closer to our goal but it still sucks,
because since Haskell does not allow us to distribute our pattern matching
for one single function over several modules,
we have to write this ugly stuff in `BaseFunctions.hs`,
that does nothing but dispatch by type to the appropriate module.
And to make this even worse we would have to manually add new
boilerplate dispatch code for every new class we invent. Not cool.


## The other solution

So perhaps our [ADT](http://en.wikipedia.org/wiki/Algebraic_data_type) is
not of the right kind for this job.
OK, let's try to represent our types just by the functions we need:
(Many thanks to Jeff Smits from the [Elm mailing list](https://groups.google.com/forum/?fromgroups#!forum/elm-discuss) for this idea.)

```haskell
-- Base.hs
module Base where

data Base = Base {step :: (Int -> Base), display :: String}
```
What do we have there? Kind of a recursive ADT, like so often.
`step` represents our mutating function
and `display` our "const member function".
Does this help? Where did our states (the "member variables") go?
They are now encapsulated in the subtype modules:

```haskell
-- Foo.hs
module Foo where

import Base

foo :: Int -> Base
foo i = Base (stepFoo i) (displayFoo i)

-- Add delta to internal state.
stepFoo :: Int -> Int -> Base
stepFoo i delta = foo $ i + delta

displayFoo :: Int -> String
displayFoo i = show i
```

`foo` obviously constructs a `Base` object. The second field is just the
result of displaying the initial state `i`. Haskell's lazyness will take
care that it will not be evaluated unnecessarily. The first field is more
interesting. `stepFoo` is partially applied to the initial state.
If we think of `stepFoo i` as `\delta -> stepFoo i delta`, we see where
the state is stored. It resides inside the
[closure](http://en.wikipedia.org/wiki/Closure_%28computer_science%29)
of our lambda function! This way it is stored in the `Base` ADT without
influencing its type. The fact that Bar's state is not an `Int` but a `String`
does not cause any problems that way:

```haskell
-- Bar.hs
module Bar where

import Base

bar :: String -> Base
bar s = Base (stepBar s) (displayBar s)

-- Concat delta as string to internal state.
stepBar :: String -> Int -> Base
stepBar s delta = bar $ s ++ show delta

displayBar :: String -> String
displayBar s = s
```
In a real world application the state of course could be any arbitrary more
complicated data type (nested records or whatever),
and not just an Int or String as in this example.

Our `Main.hs` only has to be changed in one line, since we now have our
constructor functions `foo` and `bar` (instead of `Foo` and `Bar` in the
naive approach):

```haskell
-- Main.hs
import Data.List
import Base
import Foo
import Bar

-- Steps every object in l by 1.
stepAll :: [Base] -> [Base]
stepAll l = map (\b -> step b 1) l

-- Displays all objects in l beneath each other.
displayAll :: [Base] -> IO ()
displayAll l = putStrLn $ concat (intersperse "\n" $ map display l)

main :: IO ()
main =
    let
        -- Fill a list with "derived instances".
        l :: [Base]
        l = [foo 0, bar ""]

        -- Step every object two times.
        l' = (stepAll . stepAll) l
    in
        -- Show result.
        displayAll l'
```

## Conclusion

Yeah, and that is it.
Of course, we did not *solve* the expression problem, but thanks to the fact
that we can handle functions as data in FP,
at least we can now choose which side of the problem we want to face.
We can have our desired comfort for software that often gets
new types and rarely new functions, despite the presence of a
stong static type system. We now can invent hundreds of new subtypes like
[baz and qux](http://en.wikipedia.org/wiki/List_of_recurring_Mario_franchise_enemies)
and easily add them to our world.
We do not have to edit central monster functions for the actions of all the
different types.
Everything is neatly arranged in the modules of the actual type.

---------------------------------------

If there already is a more idiomatic solution in Haskell for this, or you
have an Idea for a more elegant approach, please [tell](mailto:harry@daiw.de)
[me](https://www.facebook.com/Dohbi). :)

---------------------------------------

## Elm version

In case you are interested to use this in
[Elm](http://elm-lang.org/learn/Syntax.elm), the translation looks as
follows:

```haskell
-- Base.elm
module Base where

type Base = Base {step : (Int -> Base), display : String}
```

```haskell
-- Foo.elm
module Foo where

import Base(Base(Base))

foo : Int -> Base
foo i = Base {step=(stepFoo i), display=(displayFoo i)}

-- Add delta to internal state.
stepFoo : Int -> Int -> Base
stepFoo i delta = foo <| i + delta

displayFoo : Int -> String
displayFoo i = toString i
```

```haskell
-- Bar.elm
module Bar where

import Base(Base(Base))

bar : String -> Base
bar s = Base {step=(stepBar s), display=(displayBar s)}

-- Concat delta as string to internal state.
stepBar : String -> Int -> Base
stepBar s delta = bar <| s ++ toString delta

displayBar : String -> String
displayBar s = s
```

```haskell
-- Main.elm
import List
import Text(plainText)
import String

import Base(Base(Base))
import Foo(foo)
import Bar(bar)

stepOne : Base -> Base
stepOne (Base b) = b.step 1

-- Steps every object in l by 1.
stepAll : List Base -> List Base
stepAll l = List.map (\(Base b) -> b.step 1) l

-- Displays all objects in l beneath each other.
displayAll : List Base -> String
displayAll = List.map (\(Base b) -> b.display) >> String.join "\n"

main =
    let
        -- Fill a list with "derived instances".
        l : List Base
        l = [foo 0, bar ""]

        -- Step every object two times.
        l' = (stepAll >> stepAll) l
    in
        -- Show result.
        displayAll l' |> plainText
```

[Discuss on reddit](http://www.reddit.com/r/haskell/comments/1quhrl/from_object_oriented_programming_to_functional/)