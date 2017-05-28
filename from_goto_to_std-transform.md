# C++ - From goto to std::transform

In nearly every programming languages there are often many different possibilities to write code that in the end does exactly the same thing. In most cases we want to use the version that is the easiest to understand to a human reader.

Let's say we have a vector of integers and want another one with all elements being the square of the elements in the first one.
`[4, 1, 7] -> [16, 1, 49]`


## Goto
Sure, one could use gotos for this, but I guess nobody in their right mind would do this voluntarily, unless for trolling:

```c++
vector<int> squareVec1(vector<int> v)
{
    auto it = begin(v);
    loopBegin:
    if (it == end(v))
        goto loopEnd;
    *it = *it * *it;
    ++it;
    goto loopBegin;
    loopEnd:
    return v;
}
```
On the first look you have no idea what this code is doing. You have to kind of interpret it in your head and follow the control flow manually to find out what's going on.


## While loop
The next more readable step would be to use a loop as control structure.
```c++
vector<int> squareVec2(vector<int> v)
{
    auto it = begin(v);
    while (it != end(v))
    {
        *it = *it * *it;
        ++it;
    }
    return v;
}
```
This is bit better, at least you can immediatly see that there is some kind of loop, but most people would probably use a


## For loop
```c++
vector<int> squareVec3(vector<int> v)
{
    for (auto it = begin(v); it != end(v); ++it)
    {
        *it = *it * *it;
    }
    return v;
}
```
Here you can immediately see that the algorithm iterates ofter the elements of `v` but you still have to read the whole line `for (auto it = begin(v); it != end(v); ++it)` until you know that every single element is used and not e.g. every second, since the increase could also be `it += 2` or something else instead of `++it`. Still a `++it` could be hidden somewhere in the loop body.


## Range-based for loop
```c++
vector<int> squareVec4(vector<int> v)
{
    for (int& i : v)
    {
        i = i * i;
    }
    return v;
}
```

This time the `for` line already tells the reader that probably every element of `v` is used, but still only probably. One still has to look into the body of the for loop and look for `if`, `continue` or even `break` statements to really know that every single elemnt in `v` will be iterated over the end. Also the header does not tell what will happen to the elements.

Many people stop here, but we can continue do better in terms of readability ease.


## std::transform
OK, how can we express more clearly without explicit comments what our code does, i.e. make it self explaining?

```c++
vector<int> squareVec5(vector<int> v)
{
    transform(begin(v), end(v), begin(v), [](int i)
    {
        return i*i;
    });
    return v;
}
```
`std::transform` tells the reader at one glance that all `v.size()` elements of `v` will be transformed into something else.
Now one just has to look at `return i*i` and he directly knows everything.
This should be much easier than decyphering a for loop every single time.


## Range-based for vs. [`<algorithm>`](http://en.cppreference.com/w/cpp/algorithm)
A for loop also beginning with `for (int i : v)` could do something totally unrelated to `std::transform`. E.g. it could implement a filter:
```c++
vector<int> result;
for (int i : v)
{
    if (i % 2 == 0)
        result.push_back(i);
}
```

Here a more expressive version would be:
```c++
vector<int> result;
copy_if(begin(v), end(v), back_inserter(result), [](int i)
{
    return i % 2 == 0;
});
```

`transform` and `copy_if` show the [map](http://en.wikipedia.org/wiki/Map_%28higher-order_function%29) [filter](http://en.wikipedia.org/wiki/Filter_%28higher-order_function%29) difference more clearly than the two range-based for loops with the same header and just a differing body.

`copy_if` immediately tells the reader of our code that only elements from `v` will show up in `result` and that `result.size() <= v.size()`. Additionally bugs caused by inattentiveness like infinite loops or invalid iterators are ruled out automatically by this style compared to `for (auto it = ...)` versions.

This higher level ob abstraction not only gives our code a self-documenting flavour but also makes it easier to perhaps later replace `copy_if` with a hypothetical `copy_if_multithread` or something like that.


"But the range-based for loop is shorter and thus more readable." you say? In this very small example, this may be the case, but if the loop body would be much longer, the character count difference dissolves and you will be happy that you do not have to look at the body at all in the `transform`/`find_if` version to figure out what it is doing.

Also passing along a strategy in form of a [`std::function`](http://en.cppreference.com/w/cpp/utility/functional/function) will become easier, since you can just plug it in.


## Convenience wrappers
If you just can not stand the manual usage of `begin(v)` and `end(v)` you are free to write a wrapper in case you have to use `transform` often enough:
```c++
template<typename Container, typename Functor>
Container transformCont(Container xs, Functor op)
{
    transform(begin(xs), end(xs), begin(xs), op);
    return xs;
}

vector<int> squareVec6(const vector<int>& v)
{
    return transformCont(v, [](int i)
    {
        return i*i;
    });
}
```

## Performance
"But I have to use the hand written for loop for better performance!" - Nope, you do not have to.
Even if the `std::transform` version looks like much abstraction induced function call overhead, especially with the lambda function, there is none. It is all optimized away by the compiler.

For 50000 runs over 10000 values the different implementations ([source code](https://gist.github.com/Dobiasd/839acc2bc7a1f48a5063)) took the following cpu times on my machine:
```
goto                    - elapsed time: 0.538397s
while                   - elapsed time: 0.538062s
for                     - elapsed time: 0.537738s
range-based for         - elapsed time: 0.538066s
std::transform          - elapsed time: 0.537909s
wrapped std::transform  - elapsed time: 0.537213s
```


## Conclusion
Sure, readability also has something to with taste or to be precise familiarity, but in my opinion you should avoid explicit loops and make use of the cool stuff in the [`<algorithm>` header](http://en.cppreference.com/w/cpp/algorithm) for better maintainability of your C++ software. Once you get used to the odd lambda syntax in C++ you will enjoy every for loop you do *not* have to read. ;-)


## Further reading
With [effective stl](http://www.amazon.com/dp/0201749629) Scott Meyers has written a very nice book covering this and more in depths.
Herb Sutter's [talk about lambdas](https://www.youtube.com/watch?v=rcgRY7sOA58) can also help to get more into this topic.
Also you can discuss this article on [reddit](http://redd.it/22q18m) or [Hacker News](https://news.ycombinator.com/item?id=7571490).

By the way, if you are interested in learning more about functional programming using C++ you might enjoy [my video course on Udemy](https://www.udemy.com/functional-programming-using-cpp).