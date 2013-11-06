From imperative to functional game design
=========================================

Imperative programming was my thing since I was a school boy. Most of the time it was C++ and some Python. During the last year, [David](https://raw.github.com/quchen), a good friend and Haskell guru, tried to evangelize me with the benefits of functional programming. So I read [SICP](http://mitpress.mit.edu/sicp) and LYAH (http://learnyouahaskell.com). I actually understood some parts, alghough not all, and solved few and very small [toy problems](http://projecteuler.net/problems) in Scheme and Haskell, but I did not understand, how one could use such a programming style voluntarily, because the imperative solutions came about orders of magnitide quicker to my mind as the functional ones did.

Of course, in C++ I now used a bit more from the [algorithm header](http://en.cppreference.com/w/cpp/algorithm) and also tried [some functional things](http://docs.python.org/3/howto/functional.html) in Python, but I just did not feel how digging deeper into this paradigm could really be worth the trouble. In retrospect is was perhaps also the uncomfortable situation of again being a complete newbie.

Whatever it was, I more or less accidentally stumbled upon [Elm](http://elm-lang.org). The [examples](http://elm-lang.org/Examples.elm) did not look so scary like many type theory filled Haskell tutorials, so I gave it a shot and read trough all the [tutorials](http://elm-lang.org/Learn.elm) while constantly [playing around](http://elm-lang.org/try) with the stuff I just found out.

After solving the challenges in the [pong tutorial](http://elm-lang.org/blog/games-in-elm/part-0/Making-Pong.html) I decided to write a [Breakout clone](https://github.com/Dobiasd/Breakout), which turned out to be a very interesting and fun undertaking. :-)

The rest of the article will describe my learning experience with this project, how it is structured and why it finally convinced me of the advantages of functional (reactive) programming.