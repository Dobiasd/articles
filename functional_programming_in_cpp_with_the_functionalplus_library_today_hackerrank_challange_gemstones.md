# Functional programming in C++ with the FunctionalPlus library; today: HackerRank challange "Gemstones"


Functional programming becomes more prominent even in C++ these days, but sometimes the resulting code can feel awkward - especially with all the iterators one has to provide for the STL algorithms. **[FunctionalPlus](https://github.com/Dobiasd/FunctionalPlus)** (a small header-only library) can help overcome this issue and make your code concise and readable again.

This article is targeted towards C++ programmers new to FunctionalPlus and with little experience in functional programming. It will show how the [HackerRank challange "Gemstones"](https://www.hackerrank.com/challenges/gem-stones) can be solved elegantly with the FunctionalPlus approach.


## The challange

The (slightly modified) challange boils down to

> Find the number of characters present in every line of an input text.

As an example, the following input

    Lorem ipsum
    dolor sit amet,
    consectetur,
    adipisci velit

should produce the following output

    2

since only `e` and `s` can be found in all four lines. The challange calls these characters "gems".


## Getting the data

Assuming we already have the input in one single `std::string`, we first need to split it into lines. FunctionalPlus provides a convenient function (actually in form of a template) to do this:

```c++
// split_lines : (String, Bool) -> [String]
vector<string> fplus::split_lines(const string& str, bool allow_empty);
```

Using it looks like this:

```c++
const auto lines = fplus::split_lines(input, false);
```


## Type annotations and API search

The strange looking comment above the function declaration is a type annotation.

```haskell
split_lines : (String, Bool) -> [String]
```

simply says

> split_lines is a function taking a string and a bool and returns a container (i.e. `list`/`vector`/etc. ) of strings.

Type annotations make it easier to find and understand function templates in `fplus` with some practice. If you are looking for a function implementing a certain small task, you can use the [API-search website](http://www.editgym.com/fplus-api-search/), where you can search by name, description or aforementioned annotation. Later we will see, why searching by type can come in very handy.


## The core algorithm

OK, now that we have our data prepared, let's think about the core algorithm. If we regard every line as a set of characters, we need to calculate the [set intersection](https://en.wikipedia.org/wiki/Intersection_(set_theory)) of all given sets, since this would exactly contain the characters present in every line.

So let's convert our `std::vector<std::string> lines` into a set of characters.

```c++
typedef std::set<std::string::value_type> character_set;
```

The function

```c++
// fplus::convert_container<character_set, string> string -> character_set
fplus::convert_container<character_set, string>
```

can convert a `std::string` into a `character_set`. To apply it to all lines, we could write a for loop, but we have something better:

```haskell
fplus::transform : ((a -> b), [a]) -> [b]
```

Let's disect its type annotation first.
`fplus::transform` takes two parameters, the first one `(a -> b)` is a function taking a value of type `a` and returning a value of type `b`. These types could be anything from simple `int`s to complex classes. The second parameter is a container (e.g. `std::vector`) full of `a`s. `transform` applies the given function to all elements in the container and returns a container with the resulting elements.

Using it to perform the conversion of all lines looks as follows:

```c++
const auto sets = fplus::transform(
    fplus::convert_container<character_set, std::string>,
    lines);
```

So in our case the `(a -> b)` for `fplus::transform` is `(std::string -> character_set)`, which leads to:

```haskell
fplus::transform : ((std::string -> character_set), [std::string]) -> [character_set]
```

Now that we have our sets, we need to intersect them. [`std::set_intersection`](http://en.cppreference.com/w/cpp/algorithm/set_intersection) can be used to calculate the intersection of two sets. FunctionalPlus provides a wrapper around this with `fplus::set_intersection`, which is easier to use, since one does not need to care about providing iterators.

```c++
// example
fplus::set_intersection(set({1,2,3}), set({1,3,4})) == set({1,3});
```

Now we need to intersect not only two but all sets that resulted from the lines of the input. We could write a loop to repeatedly call `set_intersection`, but the functional paradigm provides a more elegant solution.

For easier visualisation let's write `fplus::set_intersection` as a binary infix operator called `^`. So `^` is a function that takes two sets and returns one set. In the type notation mentioned above, this would be:

    (^) : (Set, Set) -> Set

(read: "`(^)` is a function taking two sets and returning a set.")

So what we eventually want is:

    set1 ^ set2 ^ set3 ^ set4 ...

This means we need something that combines a list of sets to one set by joining them via applications of our operator. If this would be a distinct function, it would take the operator and a list of sets and return a set. So its type would be:

    (Operator, [Set]) -> Set

with

    Operator == (Set, Set) -> Set

resulting in

    ((Set, Set) -> Set, [Set]) -> Set

Wouldn't it be nice, if FunctionalPlus already provided such a thing? ;-) A quick request to the [API search](http://www.editgym.com/fplus-api-search/) gives the following result:

![api_search_fold_left_1_001](/functional_programming_in_cpp_with_the_functionalplus_library_today_hackerrank_challange_gemstones/api_search_fold_left_1_001.png)

`fold_left_1` is just what we need!

Actually, a [`fold` (sometimes known as `reduce`)](https://en.wikipedia.org/wiki/Fold_(higher-order_function)) is quite common in functional programming. With [`std::accumulate`](http://en.cppreference.com/w/cpp/algorithm/accumulate) the STL provides something similar, but like with `set_intersection`, the version from `fplus` is easier to use.

And that is everything we need. With `fold_left_1` and `set_intersection` we can calculate the overall intersection set succinctly:

```c++
const auto gem_elements = fplus::fold_left_1(
    fplus::set_intersection<character_set>, sets);
```


## Input/Output

The only missing piece is getting the text from standard input and writing the result to standard output. To avoid writing this boilderplate code, we can use `fplus::interact`, which already provides this functionality.

```haskell
interact : (String -> String) -> Io ()
```

`Io ()` simply says that we receive a function performing some side effects.

`interact` - like our `fold` and `transform` - is a [higher-order function](https://en.wikipedia.org/wiki/Higher-order_function), because it takes a function as an argument. In our case we give it the instructions on how to process the input and it uses it to handle all the I/O stuff for us.


## Wrapping up

Putting everything together, our solution looks like this:

```c++
#include <fplus/fplus.hpp>

std::string process(const std::string& input)
{
    using namespace fplus;

    typedef std::set<std::string::value_type> character_set;

    // Get lines from input.
    const auto lines = split_lines(input, false);

    // Convert string lines into sets of chars.
    const auto sets = transform(
        convert_container<character_set, std::string>,
        lines);

    // Build the intersection of all character sets.
    const auto gem_elements = fold_left_1(
        set_intersection<character_set>, sets);

    // Convert gem_elements.size() into a std::string.
    return show(size_of_cont(gem_elements));
}

int main()
{
    fplus::interact(process)();
}
```

What do you think? Is this code you personally would like to maintain compared to what an imperative version could look like? I would be happy to read your comments in the [reddit discussion](https://www.reddit.com/r/programming/comments/543rav/functional_programming_in_c_with_the/).

By the way, if you liked this write-up my video course ["Functional Programming using C++" on Udemy](https://www.udemy.com/functional-programming-using-cpp) might be something for you.