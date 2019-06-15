# A personal, generic, things-I-learned-as-a-software-developer list

With this article, I'd like to contribute my two subjective cents
to the vast space of wisdom-offering mumblings. :)

## On the job

### Write code for humans

Your code should clearly describe how it solves the domain problem
in a way optimized for readability.
The fact that a computer also has to be able to
run it, is important of course, but secondary.
Write and refactor for expressiveness first,
and then, when your code is almost self-documenting,
you might even only rarely need comments, and if so
only to explain the "why" and not the "what" or "how".

### Consider the cost when deciding about optimizations

We know "premature optimization is the root of all evil".
But what if you have profiled your code and found a performance bottleneck?
If it's a library and you don't know how it will be used, go crazy with fancy optimizations.
But if the scope is known, consider the cost (initial development and maintenance) of
implementing an optimization.
Sometimes CPUs and RAM modules are cheaper than man-hours.

### Prototyping vs. production code

When quickly hacking together a prototype
it might make sense to write your code "bottom-up",
i.e., start with some tricky implementation details to prove the feasibility of a solution's core.

Also make it clear, that this is just a prototype,
and later write new, clean and maintainable code for production.
You might want to try to use the top-down approach here,
so think from the outside in to obtain tidy interfaces and good abstraction layers.

### Don't blindly follow some methodology

Some very project was developed using test-driven development? Great! Give it a try,
but if it's not a good fit for your project, team or domain, work differently.

> Research your own experience. Absorb what is useful, reject what is useless, add what is essentially your own.

And while we are talking about testing:
The usual testing pyramid might work perfectly in many situations:

```text
      /--------------
     / system tests  \
    /------------------
   / integration tests \
  /----------------------
 /      unit tests       \
---------------------------
```

But maybe you don't need that many unit tests and better cover with integration tests if:

- Your simple CRUD application does not have much logic to test.
- You are using a programming language with a strong static type system, which already catches a whole class of bugs automatically.

Other examples:

- Some teams might be totally productive with weekly sprints and burn down charts, but that does not mean that this way of working is ideal for every team.
- If you are working with multiple people on a project and you deploy regularly, using feature branches in your VCS might be mandatory. But in an earlier project stage with maybe just one or two devs, the simplicity of pushing to master directly might make sense.

### Learn about the domain

Most software solves some real-world problems.
Do not only focus on transforming some specifications into code.
Try to understand the problem on a domain level.
Speaking the same language as the experts not only helps in avoiding
costly misunderstandings, but often by collaborating with
the customer or product owner an even better solution might emerge.

When I was developing image recognition software used in the processing
of unsold newspapers, I learned a lot of helpful stuff
by actually going on site and
being confronted with the everyday problems arising in handling absurd amounts
of sometimes fringed, wet or shrink-wrapped paper.

Occasionally it even turns out the best solution does not even involve code at all.
And if you are not working for an agency, this might be great,
because the code with the least complexity and defects is no code.
Finding this such a maximally simple solution however is rarely easy and
involves a "consultant" mindset.

> It seems that perfection is attained not when there is nothing more to add, but when there is nothing more to remove.

### Weight technical dept economically

When writing the code we usually want to have it nice and clean,
so it can easily be maintained and extended.

However technical debt is not something that is always bad.
Sometimes you get a loan to buy a house, and you pay to it, including interest.
It's the same with technical debt.
You just have to be aware of the fact that you are creating it and why,
so you can make conscious decisions about refactoring your code until it's perfect,
or leaving a part of it in a messy state because:

- the mess is isolated
- the whole thing might be dropped soon anyways
- there is something more valuable you can do with your time right now

### When stuck, create a minimal example

Even if you might not post it as a question on stackoverflow.com
creating a minimal example of your problem in a way that others
could quickly understand it, often helps tremendously in finding
the solution already.
This kind of "Rubber duck debugging" helps to isolate the essence of the issue
and can bring a deep understanding of the topic with it.

## Personal advancement

### Basics > shiny things

Having mastered just the very basics of computer science, different paradigms
and engineering, in general, will help a lot in better using all these fancy new tools
coming out every few months.
If you understand the principles of
concurrency, caching, design patterns, higher-order functions and SOLID
you will see much more similarities between different languages/libraries/frameworks
and thus have a much better learning curve.

But this also involves low-level craftsmanship like being able to comfortably work
with a Linux command line, git, a debugger,
knowing your way around the shortcuts of a text editor, etc.

### Leave your comfort zone, regularly

In order to grow, don't be afraid of something new
that is guaranteed to make you feel uncomfortable
because you will be a total newbie again.
If you have worked with PHP and Symfony for years,
spend some time to learn a bit of Kotlin, C or Haskell.
Even if you not (yet?) use these things professionally,
they will still make you better at your day-to-day tasks
by expanding your perspective and bringing joy.

So, don't be a "[programming-language-X] developer".
Be a software engineer who just happens to currently use language X most,
because it is the right tool for the job at hand.

And if you don't know something, don't be scared to openly admit it.

### Be a jack of all trades

Even if you specialize in something by building up deep knowledge about
some technology, domain or abstraction level,
try to also learn more broadly.
This involves not only knowing about low-level implementations in Fortran and
high-level code in Ruby, but also understanding systems architecture
and the business in general.

### Immerse yourself in the culture, at least a bit

You don't have to constantly go to conferences and read Hacker News all the time.

But checking the top posts of the last month on /r/programming now and then might be a good idea.

Now only will at least know about the most important new tools and technologies,
but you will also absorb some idioms and unconsciously develop a map in your head
about what is possible. This, in turn, will help you make better decisions in your
daily work.

### Consciously devote some time to learning

Just a few hours of explicit learning a week can not only boost your
excitement, but also your productivity in a profitable way. This can involve:

- browsing interesting questions and answers on stackoverflow.com
- reading some articles
- watching a talk or listening to a podcast
- playing with a toy project
- reading one of the classics like [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882), [Design Patterns](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612), [Domain driven design](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
  - [The Mythical Man-Month](https://www.amazon.com/Mythical-Man-Month-Software-Engineering-Anniversary/dp/0201835959)
  - [The Pragmatic Programmer](https://www.amazon.com/Pragmatic-Programmer-Journeyman-Master/dp/020161622X)
  - [Structure and Interpretation of Computer Programs](https://www.amazon.com/Structure-Interpretation-Computer-Programs-Engineering/dp/0262510871)

### Don't treat social skills as something special

They can, and should in order to be successful, be improved like
technical skills too by theory and practice. Since many problems,
one has to solve as a developer, are not purely technical
(code reviews are only one of many examples)
reading [Dale Carnegie](https://www.amazon.com/How-Win-Friends-Influence-People/dp/0671027034)
or something similar should pay off quickly.

### Don't clutter your brain

To think of cool and creative solutions, you need some space in your head.
Try to use "external memory devices" for personal things too when possible, e.g.:

- Kanban apps like Trello
- Notes like Google Keep
- Some calendar thingy
- etc.

The less stuff you have to keep in your head, the more freely you can think.

Also when you are totally stuck on a problem, leave it alone for some time
and do something completely unrelated, away from the desk.
Your brain might suddenly come up with a solution it would not have been
able to generate while consciously focusing.
