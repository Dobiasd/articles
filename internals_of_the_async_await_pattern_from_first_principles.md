# Internals of the async/await pattern from first principles

Many of us are using the async/await pattern, but understanding how it works under the hood is a different beast. This article sheds some (language-agnostic) light on how the needed machinery can be implemented. These insights are helpful when usage does not go according to plan, and I find it aesthetically pleasing too.

A normal function (also known as a subroutine) returns once:

```java
// Using an imaginary programming language here to avoid being too specific.
function foo()
    x = 21
    x = 2 * x
    return x

assert foo() == 42
```

A Generator (also known as a semicoroutine, a special case of a coroutine) can return multiple times and preserve its state between invocations:

```java
function foo()
    x = 21
    yield x
    x = 2 * x
    yield x

g = foo()
assert g.step() == 21
assert g.step() == 42
```

In many programming languages, the above generator is internally (by the interpreter or compiler) converted to a state machine as follows:

```java
class foo_generator
    _state = 0
    running = true
    x = 21
    method step()
        if _state == 0
            _state = 1
            return x
        if _state == 1
            x = 2 * x
            _state = null
            running = false
            return Stopped x
        explode
```

And `g = foo()` simply obtains a new instance/object of that class.

An additional (third) `g.step()` in the code above would return the special `Stopped` value. Some languages implement this as throwing an exception instead (`StopIteration` in Python for example).

Even if your language does not actually transform the generator into a state machine, it probably does something with equivalent behavior, so it's a good mental model to hold on to.

For our async/await pattern, we don't need to `yield` values from our generators, we just use it to suspend our function.

```java
function foo()
    x = 21
    yield
    x = 2 * x
    return x
```

```java
class foo_generator
    _state = 0
    running = true
    x = 21
    method step()
        if _state == 0
            _state = 1
            return // ignoring the return type here for simplicity
        if _state == 1
            x = 2 * x
            _state = null
            running = false
            return Stopped x
        explode
```

So to get our answer from `foo`, we do something like this:

```java
g = foo()
g.step()
answer = g.step()
```

From the outside, our function suspended itself during execution and continued where it left off to finally return the result.

Composing such functions (including the suspend points) could look as follows:

```java
function bar()
    x = 1
    yield
    x = 40 * x
    return x

function foo()
    // Step through the whole thing, yielding (suspending) in between steps.
    await_gen = bar()
    await_result = await_gen.step()
    while await_gen.running
        yield
        await_result = await_gen.step()
    x = await_result
    x = x + 2
    return x
```

So `foo` would suspend itself once while awaiting `bar`.

But this is syntactically rather clumsy. Luckily the designers of our imaginary language introduced the `await` keyword, which expands to something like the boilerplate above:

```java
function foo()
    b = await bar()
    x = x + 2
    return x
```

(In reality, `await` might additionally do exception/error handling/propagation, but for compactness, we skip this here.)

So the generator (calling it "coroutine" from here on) obtained from `foo()` now also operates step-wise, i.e., suspends itself before obtaining the result from `bar`.

Btw., this way of suspending is called "suspend by return" (or sometimes "suspend up"), because `foo` and `bar` suspend themselves by returning to their caller. This is in contrast to normal function calls, in which a function "suspends" itself by calling some other function ("suspend by call" or "suspend down"). (When zooming in to the Assembly level, the return address might be passed to the callee via a pointer pushed to the stack, so when the callee is done, it knows where to jump to in the caller function.) The coroutines we're using here are called "stackless". The resume information is not stored on a call stack but in the (probably allocated on the heap) coroutine, each only knowing its own "stack frame".

Let's get to the "co" (cooperative) in "coroutines". We now know how suspending/resuming works, so we'll look into how the implementation of an async library uses these building blocks. While we want things like IO to run in parallel in the background, our own functions only run concurrently, but not parallelly. I.e., we only use one thread, and the coroutines cooperate by purposely suspending to then be automatically resumed again later. To not manually resume them all the time, we need some executor to do this for us.

```java
class Executor
    current = null
    _ready = empty list

    method submit(coroutine)
        _ready.push_right(coroutine)

    method run()
        while _ready.not_empty
            current = _ready.pop_left()
            current.step()
            if current.running
                submit(current)

// Yes, it has to be global (or a Singleton) in this case. We'll see why in the next section.
executor = Executor()
```

All this event loop does is advance (`step`) the coroutine (state machine) that is the most left in its `_ready` list, and in case it's not finished after that, put it back in the list. Once there is no more work left, it exits.

We can already use this to run two coroutines concurrently!

```java
function foo()
    yield
    print "a"
    yield
    print "b"
    yield
    print "c"

function bar()
    yield
    print "x"
    yield
    print "y"
    yield
    print "z"

executor.submit(foo())
executor.submit(bar())
executor.run()
```

Output (The two functions nicely take alternating turns.):

```
a
x
b
y
c
z
```

But how about things that take a bit longer, like IO? To get there, we start with a simple `sleep`:

```java
function foo()
    await async_sleep(1 second)
    print "moin"
```

We need to extend our executor:

```java
class Executor
    current = null
    _ready = empty list
    _scheduled = empty priority queue

    method submit(coroutine)
        _ready.push_right(coroutine)

    method schedule(timestamp, coroutine)
        _scheduled.put(timestamp, coroutine)

    method run()
        while _ready.not_empty or _scheduled.not_empty
            if _ready.empty
                wakeup_time, coroutine = _scheduled.pop()
                sync_sleep(wakeup_time - now)
                submit(coroutine)

            current = _ready.pop_left()
            current.step()
            // We only re-submit the coroutine when it was not removed/scheduled by async_sleep.
            if current and current.running
                submit(current)

executor = Executor()

function async_sleep(duration)
    executor.schedule(now + duration, executor.current)
    executor.current = null
```

`run` has become more involved. If is nothing ready, it will sleep (actually block) until the next scheduled coroutine needs to be awakened.

Since we're single-threaded, no urgent new tasks will be inserted "from the side", i.e., we will not oversleep. New tasks can only be added from inside a coroutine advanced from without the event loop.

Finally, let's get to IO.

When we submit a task waiting for IO, our `Executor` needs to do additional bookkeeping while handles are to be awaited. When no task is ready, it cancels its sleep when one of the handles becomes ready (`epoll` on Linux, `WaitForMultipleObjects` on Windows).


```java
class Executor
    ...

    _io_pending = empty dictionary, mapping from handles to coroutines

    method run()
        while _ready.not_empty or _scheduled.not_empty or _io_pending.not_empty
            if _ready.empty
                timeout = null
                if _scheduled.not_empty
                    wakeup_time, coroutine = _scheduled.first.timestamp
                    timeout = wakeup_time - now

                // Sleep till the timeout expires or a handle becomes ready.
                io_ready = wait_for_handles(_io_pending.handles, timeout)
                for handle in io_ready
                    submit(_io_pending.pop(handle))

            current = _ready.pop_left()
            current.step()
            if current and current.running
                submit(current)

    // A coroutine sets itself as waiting for the socket.
    method recv(socket) -> bytes
        _io_pending[socket] = current
        current = null
        yield
        return sock.recv()
```

While the above only shows async input (for brevity), async output works analogously.

[Here, you can find a (Python) implementation of all things discussed in this article](internals_of_the_async_await_pattern_from_first_principles/internals_of_the_async_await_pattern_from_first_principles.py), including an echo-ing TCP server (heavily inspired by [an amazing workshop](https://www.youtube.com/watch?v=Y4Gt3Xjd7G8) of David Beazley).

Now you should have a rough idea of what happens with coroutines on the language level and the tooling the async libraries provide us with. I suggest to play around with (and purposely break) the linked example Python implementation to get a better feeling for everything.

To put the treated concept into perspective, here is a spectrum of different multitasking approaches (from heavyweight to lightweight):
- processes (OS, preemptive, stackful)
- (OS) threads (OS, preemptive, stackful)
- green threads (language VM, preemptive, stackful)
- fiber (language VM, cooperative, stackful)
- coroutines (async/await, cooperative, stackless, what this article is about)

Some advantages of the coroutines approach described here are:
- no synchronization mechanisms like locks/mutexes are needed to avoid data races
- fast, suitable for some real-time use cases
- light, it scales easily to thousands of concurrent tasks

A downside is, that it sometimes can be hard to reason about.

So choose wisely. ;)
