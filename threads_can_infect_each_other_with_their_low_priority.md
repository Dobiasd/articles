# Threads can infect each other with their low priority

Imagine having something like the following situation:

```c++
ThreadSafeQueue queue;

void thread_a() {
    // Infinite loop just for the sake of this example.
    while(true) {
        ...
        queue.push(...);
        ...
    }
}

void thread_b() {
    while(true) {
        ...
        x = queue.pop();
        ...
    }
}
```
(Pseudo C++, but the concept applies to other languages too.)

Both functions (`thread_a` and `thread_b`) are running concurrently on different OS threads. It's a typical producer-consumer situation.

Maybe `thread_a` is doing something that should not have too much latency, e.g., communicating with a PLC, and `thread_b` does some work, that is allowed to have high latency, e.g., updating some UI elements.

Of course, if you had hard real-time requirements, you would use a real-time OS. Nevertheless, since the job of `thread_a` is more urgent than the job of `thread_b`, you decide to change the priorities:

- `thread_a`: `HIGH` priority (low latency)
- `thread_b`: `LOW` priority (high latency)

So with the help of the preemptive scheduler of the OS, you now should have low latency on `thread_a`, because with its priority it's not only preferred over `thread_b` but also over all other threads (not shown above) with priority `NORMAL` (the default).

Seems fine, right? But in reality, it likely is not. Assuming our `ThreadSafeQueue` isn't a specially designed lock-free with all its quirks, but protected by a mutex instead, with a bit of manual inlining, the code reveals more of what it is doing:

```c++
Mutex queue_mutex;

void thread_a() {
    while(true) {
        ...
        queueMutex.lock();
        // push
        queueMutex.unlock();
        ...
    }
}

void thread_b() {
    while(true) {
        ...
        queueMutex.lock();
        // pop
        queueMutex.unlock();
        ...
    }
}
```

(Exception-safety using RAII purposely ignored for clarity.)

This means the following might (read "will") happen at some point:

- `thread_b` locks the mutex.
- The scheduler interrupts it's execution and gives the CPU to some other thread.
- It might take quite long until `thread_b` gets its next time slice. Some other threads with priority `NORMAL`, which can also live in other processes running on the same machine, might have quite some time-consuming work to do, so the scheduler prefers them over `thread_b`.
- `thread_a` thus will be forced to wait on it's blocking `.lock()` call for quite long.
- Consequently, `thread_a` has lost its low-latency property.

So you thought you have the following:

---

![1](threads_can_infect_each_other_with_their_low_priority/1.png?raw=true)

---

But in reality, you have:

---

![2](threads_can_infect_each_other_with_their_low_priority/2.png?raw=true)

---

`thread_b` infected `thread_a` with its low priority.

This brings us to a new theorem:

**A thread's observed priority is not higher than the lowest priority of any thread it shares a mutex with.**

The strength of the effect this ([priority inversion](https://en.wikipedia.org/wiki/Priority_inversion)) has on latency may differ depending on what OS/scheduler is used, but in general, it holds that, as soon as thread priorities are changed deliberately for any reason, one suddenly is forced to investigate the thread-mutex graph of one's application and check for lower-prioritized neighbors. OS schedulers might implement [different techniques](https://en.wikipedia.org/wiki/Priority_inversion#Solutions) to lessen the severity of this problem, each of them with different upsides and downsides.

Naturally, the question arises, if this spreading can be transitive too, i.e., if, in the following graph example, the priority of `thread_e` can have an influence on the latency / observes priority of `thread_c`:

---

![3](threads_can_infect_each_other_with_their_low_priority/3.png?raw=true)

---

The answer is: Yes, it can. It depends on how the acquisitions of the locks in `thread_d` are intertwined.

```cpp
Mutex mutex_1;
Mutex mutex_2;

// prio HIGH
void thread_c() {
    while(true) {
        ...
        mutex_1.lock();
        ...
        mutex_1.unlock();
        ...
    }
}

// prio NORMAL
void thread_d() {
    while(true) {
        ...
        mutex_1.lock();
        ...
        mutex_2.lock();
        ...
        mutex_2.unlock();
        ...
        mutex_1.unlock();
        ...
    }
}

// prio LOW
void thread_e() {
    while(true) {
        ...
        mutex_2.lock();
        ...
        mutex_2.unlock();
        ...
    }
}
```

(The situation in `thread_d` might be hidden in calls so some other functions.)

So, what can happen here?

- `thread_e` does its `mutex_2.lock()`.
- The scheduler interrupts `thread_e`.
- `thread_d` does its `mutex_1.lock()`.
- `thread_d` wants to do its `mutex_2.lock()`, but is blocked, because `thread_e` is already sleeping inside `mutex_2`.
- `thread_c` tries do it its `mutex_1.lock()`, but is blocked, because `thread_d` already has acquired `mutex_1`.

Thus, `thread_c` is blocked at least as long as `thread_e` does not reach its `mutex_2.unlock()`. And this, again, can take quite a while.

So, the latency of `thread_c` was ruined, transitively, by `thread_e`,

and you end up with the following:

---

![4](threads_can_infect_each_other_with_their_low_priority/4.png?raw=true)

---

This can haunt you not only when using classical mutexes, but with other [types of mutual exclusion devices](https://en.wikipedia.org/wiki/Mutual_exclusion#Types_of_mutual_exclusion_devices) too.

Conclusion: **If possible, avoid headaches by just not fiddling around with thread priorities.**

([discussion on reddit](https://www.reddit.com/r/programming/comments/e7sb5p/threads_can_infect_each_other_with_their_low/))
