# "A monad is just a monoid in the category of endofunctors." - explained

## Introduction

The quote in the title sparked my curiosity after I had read it in a [a blog](http://james-iry.blogspot.com/2009/05/brief-incomplete-and-mostly-wrong.html) using it jokingly. (Originally it's from a [math book](https://en.wikipedia.org/wiki/Categories_for_the_Working_Mathematician).)

Despite good existing explanations on the web, achieving a level of at least somewhat satisfying understanding, however, turned out to be quite a ~~struggle~~ journey for me. This article is an attempt to ease this process for other software developers a bit, and to consolidate the things I learned for myself. ;-)

(Disclaimer: The given explanations contain nasty shortcuts, some used consciously, some probably just based on my lack of deeper understanding.)

## Syntax

First, let's agree on some syntax to use in the rest of the article.

```kotlin
x : Int // x is a variable of type Int
xs : List<Int> // xs is a list of integers
f : Int -> String // f is a function from Int to String.
```

In functional programming, functions are first-class citizens. They can be passed around, and they can be returned from functions (higher-order functions).

```kotlin
// isEven is a function taking and integer and returning a boolean.
isEven : Int -> Boolean

// The function keepIf takes two parameters.
// The first one is a function taking an A and returning Boolean.
// The second one is a list of elements of type A.
// Finally, keepIf returns a sequence of elements of type A.
keepIf : (A -> Boolean, List<A>) -> List<A>
```

`A` being a type variable, we could call `keepIf(isEven, [1, 2, 3, 4, 5])` and get `[2, 4]`. (Here, `A` is `Int`.)

### Currying

While

```kotlin
keepIf : (A -> Boolean, List<A>) -> List<A>
```

is a function that takes two parameters (a function and a list) and returns a list, we could also only apply the first parameter and get a function taking a `List<A>` and returning a `List<B>`. (partial function application)

```kotlin
keepIf : (A -> Boolean) -> (List<A> -> List<A>)
```

This converts every function of arbitrary arity into a function of arity 1.

We call this process currying.

`->` is right-associative, so the above is equivalent to:

```kotlin
keepIf : (A -> Boolean) -> List<A> -> List<A>
```

This way of thinking will help us in the rest of the article.

## What is a category?

A category is a bunch of objects with a set of morphisms (arrows).

```
-----   f   -----
| A | ----> | B |
-----       -----
              |
              | g
              |
              v
            -----
            | C |
            -----
```

Morphisms must be composable, so if there is a morphism `f` from `A` to `B` and a morphism `g` from `B` to `C`, then a morphism `h` from `A` to `C` must exist too.

```kotlin
f : A -> B
g : B -> C

h : A -> C
```

with

```kotlin
h(x) = g(f(x))
```

```
-----   f   -----
| A | ----> | B |
-----       -----
     \        |
      \       | g
       \ h    |
        \     v
         \  -----
           >| C |
            -----
```

Let's write that kind of (forward) function composition as `h = f >> g`.

```kotlin
>> : (A -> B) -> (B -> C) -> (A -> C)
```

And finally, there is an identity morphism (endomorphism) for every object.

```
    ------
   /      \
  |       | identity
  v       |
-----    /
| A | --/
-----
```

The category we work with in programming is the category of types, i.e., each object represents the set of possible values for the particular type. The morphisms are our functions.
Since in functional programming functions are data too (they can be passed around, etc.) the function types themselves are also objects.

Even though in this special category we can know something about the "content" objects (types) and what the concrete morphisms (functions) do to them, from a pure category-theoretical point of view, this is not needed.


## What is a functor?

A functor is a structure-preserving mapping between categories.

But for now, let's think about a functor in terms of a box. A typical example is the `Maybe` functor, which can either hold a value or nothing. (You might know it as `class Optional<T>` or similar, depending on the programming languages you're familiar with.)

For `Maybe` to become a functor, we must provide a function `lift` that converts a function of type `A -> B` to one of type `Maybe<A> -> Maybe<B>`:

```kotlin
lift : (A -> B) -> Maybe<A> -> Maybe<B>
```

`lift` "lifts" a function `A -> B` from the world of normal types into the world of `Maybe`s. That's the structure-preserving property. The graph of morphisms in the original category also exists in the functor category.

Since `Maybe<T>` is also a type in our normal category of types, we call `Maybe` an endofunctor, i.e., it maps from our original category to a subcategory of it, not making us leave the source category.

`lift` for `Maybe` returns a function that is implemented such that it applies the function `A -> B` to the value in `Maybe<A>` if a value is present. In case there is nothing inside, it returns a `Maybe<B>` with nothing inside. So the box can hold a value or be empty.

Another generic type, which can be a functor, is `List<T>`. For it, `lift` is usually implemented like `map`:

```kotlin
map : (A -> B) -> List<A> -> List<B>
```

I.e., we can use it with a function `f: A -> B` and a `List<A>`, and we get a `List<B>`, with `f` applied to each original element.

A functor must preserve identity morphisms:

```kotlin
lift(identity) = identity
```

and composition of morphisms
```kotlin
lift(f >> g) = lift(f) >> lift(g)
```


## What is a monoid?

A monoid is an algebraic structure consisting of:
- a set, which in our case is a type, i.e., an object in the category of types
- a binary operation (`<>`)
- a neutral element for that operation (`neutral`)

It must have the following properties:
- closure: Combining two elements with the binary operation must return an element of the same type. (`<> : (A, A) -> A`)
- associativity: `(x <> y) <> z = x <> (y <> z)`

For the neutral element, the following must be true:
- `x <> neutral = x`
- `neutral <> x = x`

A simple example of a monoid is the set of numbers under addition (`+`) with `0` as the neutral element:
- `<> = +`
- `neutral = 0`

Take a minute to convince yourself that this fulfills the monoid requirements.

Other examples of monoids in the category of types are:
- numbers under multiplication (`*`) with `1` as the neutral element
- sets under the union operation with the empty set as the neutral element

These monoids so far were all commutative, i.e., `x <> y = y <> x` but that does not need to be true.

Examples for non-commutative monoids are:
- strings under concatenation with the empty string as the neutral element (similarly, lists under concatenation with the empty list as the neutral element)
- endomorphism (`f : a -> a`) under composition (`>>`) with `identity` as the neutral element


## What is a monad?

Let's say we want to read a text file containing a bunch of integers and calculate the median value of them.
We have some functions that can fail, and thus they don't return a plain type, but a `Maybe<T>`. 

```kotlin
// Takes a file path and returns the contents of the file, or nothing if the file can't be read.
read_file : String -> Maybe<String>

// Takes a text and returns a list of the contained integers, or nothing if the parsing failed.
parse_text : String -> Maybe<List<Int>>

// Calculates the median value of a list of integers, which fails for empty lists.
calc_median : List<Int> -> Maybe<Int>
```

We'd like to compose these functions, but normal function composition (`>>`) can't be used here, i.e., the types do not align.

```kotlin
>> : (A -> B) -> (B -> C) -> (A -> C)
```

So we need some other kind of composition, a monadic one (called "(forward) Kleisli composition"):

```kotlin
// The "fish" operator
>=> : (A -> Functor<B>) -> (B -> Functor<C>) -> (A -> Functor<C>)
```

If we provide (that is, implement) `>=>` for `Maybe`, our `Maybe` (endo)functor is now also a monad. So let's write it as:

```kotlin
>=> : (A -> Monad<B>) -> (B -> Monad<C>) -> (A -> Monad<C>)
```

In addition, we need to provide the "trivial" function `inject : A -> Monad<A>` (also known as `pure` or `return`), which simply allows us to bring a value from the category of types to a value in the category of `Maybe` types. In that case, it's just the constructor of `Maybe`.

In our original example, we can now write

```kotlin
program : String -> Maybe<Int> = read_file >=> parse_text >=> calc_median
```

and are done.

Composing functions this way is nice. In the case of `Maybe` we can think of it like so:
- As long as we have an actual value, we apply the next function to it.
- Once we divert to the `nothing` track, we stay there and just fall through to the end skipping the later functions.

We spare all the boilerplate-like plumbing code by defining it only once (generically) in the implementation of `>=>`.

Btw, instead of providing `>=>`, we could also provide `>>=` ("bind") (`>>= : Monad<A> -> (A -> Monad<B>) -> Monad<B>`) or `join` (`join : Monad<Monad<A>> -> Monad<A>`). If `lift` and just one of the three (`>=>`/`>>=`/`join`) is given, the other two can always be derived from it, which is a fun exercise, but not needed here.

Also, a monad must satisfy some laws:
- `inject >=> f = f` (`inject(x) >>= f = f(x)`)
- `m >=> inject = m` (`m >>= inject = m`)
- `(f >=> g) >=> h = f >=> (g >=> h)`

Staring at them long enough, they hopefully start to make sense. ;-)

To summarize, a monad is a functor equipped with `>=>` (and `inject`).

## A monoid in the category of endofunctors

The final piece in the puzzle is to understand, how this renders a monad a monoid in the category of endofunctors.

The category of endofunctors is a category with the objects being the endofunctors and the morphisms being functions that map from one functor to another. (They are called natural transformations, and they, of course, must also satisfy the requirement of composability, for the whole thing to be a proper category. But their details are not important here.)

```
------------    NT    -----------
| Maybe<A> | -------> | List<A> |
------------          -----------
                     
                ...
```

How would a monoid in this category look like?

For a monoid, we need an object, which is an endofunctor now, e.g., `Maybe<T>`.

(Usually, the mathematically clean way now involves a product category to create a monoidal category and functor composition, but we fiercely simplify here. ("Mathematicians hate this one (weird) trick."))

We can think of this object in terms of a function creating such a functorial value, `A -> Maybe<T>`. So that's the first thing we use to form the monoid that we'd like to obtain.

Second, we need a binary operation. Let's use our Kleisli composition, `>=> : (A -> Monad<B>) -> (B -> Monad<C>) -> (A -> Monad<C>)`.

Last, we need a neutral element for the operation. Let's use `inject : A -> Monad<A>`.

Does this algebraic structure fulfill our monoid requirements?
- Closure (`<> : (A, A) -> A`)? Yes, because with `>=>` we don't suddenly land in a different monad, e.g., jump from `Maybe` to `List` or something like that.
- Associativity (`(x <> y) <> z = x <> (y <> z)`)? Yes, because the monad laws already state that `>=>` must be associative (like normal function composition).
- `x <> neutral = x` and `neutral <> x = x`? Yes, because `inject >=> f = f` (from the monad laws) and `f >=> inject = f` with `f : A -> Monad<B>`.

So there we have it!

A monad in the category of types is (just) a monoid in the category of endofunctors. :tada:

Data lives in a monad, monadic functions live in a monoid.

## Conclusion

I hope the initial quote now sounds less alien. And maybe you also appreciate the beauty of it, because, in the end, compositionality is the essence of programming, i.e., building bigger things from simple things. And this provides a framework to formally think about this.

Such insights can help to write leaner code, expressing the high-level logic clearly, without being blinded by implementation-specific (repeated) details/boilerplate. Implementers of compilers/libraries might even use such semantics (functors, monoids, monads) to perform certain optimizations based on the guarantees provided by the laws associated with these abstractions.