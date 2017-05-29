# Creating a replacement for the switch statement in C++ that also works for strings

The [switch statement](http://en.cppreference.com/w/cpp/language/switch) in C++ only works for `int`s, `enum`s or a values convertible to one of them. This probably will not change in the C++ standard soon, since some [low-level optimizations](https://en.wikipedia.org/wiki/Branch_table) of these statements depend on it.

So the following chatbot, that likely passes every Turing test, sadly does not compile.

```c++
#include <iostream>
#include <string>

void say(const std::string& text)
{
    std::cout << text << std::endl;
}

void quit(const std::string& msg, bool* running_flag)
{
    if (running_flag)
        *running_flag = false;
    say(msg);
}

int main()
{
    bool running = true;
    while (running)
    {
        std::string input;
        std::cin >> input;

        switch(input) {
            case "hi": say("hey"); break;
            case "whazzup": say("wazzuuuup"); break;
            case "bye": quit("see ya", &running); break;
            default: say("wat?"); break;
        }
    }
}
```

Sure, we could [hash the string](https://stackoverflow.com/a/16388610/1866775) to an integral, but using it [probably](https://en.wikipedia.org/wiki/Murphy%27s_law) will give us [headaches](https://en.wikipedia.org/wiki/Hash_table#Collision_resolution) at some point in the future. Long `if - else if` chains also are not always nice to read.

So let's - just out of curiosity - create a replacement `switch`, that at least is suitable for our particular use case. Perhaps we learn something interesting on our way.

OK, what does a `switch` actually do? It takes a mapping from possible values to statements, a default statement and of course the value to match. Since functions are first-class citizens in C++, we should be able to write our `switch2` without ugly [macros](http://en.cppreference.com/w/cpp/preprocessor/replace).

A possible implementation could look as follows:

```c++
template<typename Key_t>
void switch2(const Key_t& key,
    const std::unordered_map<Key_t, std::function<void()>>& dict,
    const std::function<void()>& def)
{
    const auto it = dict.find(key);
    if (it != dict.end())
        it->second();
    else
        def();
}
```

It takes the following three parameters
* `key` is simply the value we want to switch on, `input` in our example from above.
* `dict` is the mapping from possible values to functions that should be executed. Such a function can of course include multiple statements and execute an arbitrary number of side effects.
* `def` is the function that should be executed if `key` is not present in `dict`.

`switch2` then simply looks up `key` in `dict` and acts accordingly.

Naively we could try to use it like that:

```c++
        switch2(input, {
            {"hi", say("hey")},
            {"whazzup", say("wazzuuuup")},
            {"bye", quit("see ya", &running)}},
            say("wat?"));
```

But even if it would compile (which it does not), it would immediately run all three calls do `say` and the call to `quit` before any switching happens.

It could be done using lambdas:

```c++
        switch2(input, {
            {"hi", [](){ say("hey"); }},
            {"whazzup", [](){ say("wazzuuuup"); }},
            {"bye", [&](){ quit("see ya", &running); }}},
            [](){ say("wat?"); });
```

But that adds quite some syntactical noise. So let's try to find a way to defer a function call in some other way. This is surprisingly easy in C++. We just need a function that takes another function `f` and a list of arguments and returns a nullary function, that runs f with the given arguments when called.

```c++
template<typename F, typename... Args>
std::function<void()> defer(F f, Args ... args)
{
    return [f, args...]()
    {
        f(args...);
    };
}
```

Now we are in the lucky situation to be able to do the following:

```c++
        switch2(input, {
            {"hi", defer(say, "hey")},
            {"whazzup", defer(say, "wazzuuuup")},
            {"bye", defer(quit, "see ya", &running)}},
            defer(say, "wat?"));
```

This reads not *that* bad. We need to write `defer` but we do not need `break` statements any more, which can accidentally be forgotten easily in usual `switch` blocks. But the most important thing is we can now talk to our awesome AI for hours.

Is there an advantage over an `if - else if` chain like the following you ask?

```c++
        if (input == "hi") say("hey"); else
        if (input == "whazzup") say("wazzuuuup"); else
        if (input == "bye") quit("see ya", &running); else
            say("wat?");
```

And that is a very good question. Up to now there was none, but one fruit is hanging quite low.

In longer chains it can happen that one case is covered more than once, which produces strongly unwanted run-time behavior. With our `switch2` we can prevent this from happening - not at compile time but at least at run time.

```c++
template<typename Key_t>
void switch2(const Key_t& key,
    const std::vector<std::pair<Key_t, std::function<void()>>>& pairs,
    const std::function<void()>& def)
{
    std::unordered_map<Key_t, std::function<void()>> dict;
    for (const auto& entry : pairs)
        dict.insert(entry);
    assert(dict.size() == pairs.size());
    const auto it = dict.find(key);
    if (it != dict.end())
        it->second();
    else
        def();
}
```

Now `switch2` takes a `vector` with key-function pairs. If the resulting dictionary does not have the same number of entries as the vector, at least one key was present more than once and our debugger will tell us immediately on the first call of switch with this invalid set of keys.

Remember that some run-time overhead (hashing, lookup, no perfect forwarding in `defer`) is involved in using `switch2`, and that it possibly could show up in your profiler if used in a time-critical section of your code.

If you are interested in learning more about functional programming using C++ you might enjoy [my video course on Udemy](https://www.udemy.com/functional-programming-using-cpp). I promise it contains code more useful in everyday usage than this article. ;)

What do you think about our little switch replacement? I would be happy to read your comments in the [reddit discussion](https://www.reddit.com/r/programming/comments/6e0hzr/creating_a_replacement_for_the_switch_statement/).



---

full code:

```c++
#include <cassert>
#include <functional>
#include <iostream>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

template<typename Key_t>
void switch2(const Key_t& key,
    const std::vector<std::pair<Key_t, std::function<void()>>>& pairs,
    const std::function<void()>& def)
{
    std::unordered_map<Key_t, std::function<void()>> dict;
    for (const auto& entry : pairs)
        dict.insert(entry);
    assert(dict.size() == pairs.size());
    const auto it = dict.find(key);
    if (it != dict.end())
        it->second();
    else
        def();
}

template<typename F, typename... Args>
std::function<void()> defer(F f, Args ... args)
{
    return [f, args...]()
    {
        f(args...);
    };
}

void say(const std::string& text)
{
    std::cout << text << std::endl;
}

void quit(const std::string& msg, bool* running_flag)
{
    if (running_flag)
        *running_flag = false;
    say(msg);
}

int main()
{
    bool running = true;
    while (running)
    {
        std::string input;
        std::cin >> input;

        switch2(input, {
            {"hi", defer(say, "hey")},
            {"hi", defer(say, "wazzuuuup")},
            {"bye", defer(quit, "see ya", &running)}},
            defer(say, "wat?"));
    }
}
```
