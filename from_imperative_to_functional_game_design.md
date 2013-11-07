# From imperative to functional game design

Imperative programming was my thing since I was a school boy. Recently it was mainly C++ and some Python. During the last year, [David](https://raw.github.com/quchen), a good friend and Haskell guru, tried to evangelize me with the benefits of functional programming (FP). So I read [SICP](http://mitpress.mit.edu/sicp) and LYAH (http://learnyouahaskell.com). I actually understood some parts, alghough not all, and solved few and very small [toy problems](http://projecteuler.net/problems) in Scheme and Haskell, but I did not see, how one could use such a programming style voluntarily, because the imperative solutions came about an order of magnitide quicker to my mind than the functional ones did.

Of course, in C++ I now used a bit more from the [algorithm header](http://en.cppreference.com/w/cpp/algorithm) and also tried [some functional things](http://docs.python.org/3/howto/functional.html) in Python, but I just did not feel how digging deeper into this paradigm could really be worth the trouble. E.g. why should I `foldr` a list if I can `for`-loop over an array? In retrospect it perhaps also was the uncomfortable situation of again being a complete newbie, that kept me from continuing.

Whatever it was, I more or less accidentally stumbled upon [Elm](http://elm-lang.org). The [examples](http://elm-lang.org/Examples.elm) did not look so scary like many type theory filled Haskell tutorials, so I gave it a shot and read trough all the [tutorials/articles](http://elm-lang.org/Learn.elm) while constantly [playing around](http://elm-lang.org/try) with the stuff I just found out.

After solving the challenges in the [pong tutorial](http://elm-lang.org/blog/games-in-elm/part-0/Making-Pong.html) I decided to write this [Breakout clone](https://github.com/Dobiasd/Breakout), which turned out to be a very interesting and fun undertaking. :-)

The rest of the article will describe my learning experience with that project, how it is structured and why it finally convinced me of the advantages of functional (reactive) programming, and motivated me to immediately continue with [a second game project](https://github.com/Dobiasd/Maze).


## Differences to a hypothetical imperative implementation in C++

If I had written this game (resp. a non browser version of it) in C++, I probably would have used [SFML](http://www.sfml-dev.org), which is a very good library for making games like this. I already used it to write a [Snake like game](https://github.com/Dobiasd/Dron). My cost estimations for that project would have been about 10 man-days, I guess. Surprisingly it took me less time to do it in Elm, a language I had no experience with at all!

One reason for that is the much shorter edit/complie cycle in Elm, which reduces to just one click in your browser. But OK except the [hot-swapping](http://elm-lang.org/blog/Interactive-Programming.elm) that is also possible with some imperative languages.
The much more astonishing fact for me was, that I did not need many of these cycles. Sometimes I wrote code for nearly an hour, and as soon as [Elm's Haskell like type system](http://elm-lang.org/learn/Getting-started-with-Types.elm) did not give me errors any more while compiling, the code just worked! There was very rarely a need to debug it at all! I guess this comes from the notion, that if you look at a pure functions, you just have to think about what it stands for and not what I will do to something else under certain circumstances etc. Also when just thinking in expressions and no more in statements, there is not so much control flow you have to emulate in your head. And it is easier to structure your code. The temptation to write spaghetti code functions is not that big and if one still grows too long, it is very easy to factor out the parts that can stand meaningful for their own.

Also many design patterns involving inheritance and boilerplate code in C++ just disintegrate into thin air when you have functions as first class citizen in FP.

Dont't get me wrong. I still think C++ is a great language if it comes to performance critical system programming, and I will continue to use it for appropriate tasks, but the high control over nearly every byte in your system comes at the cost of increased developement time. So every tool has its usage, and you can probably get a screw into a wall using a hammer, but if you feel that a big part of your effort is wasted energy, there is probably a better solution. ;-)

Sure, with Python things would have probably been much different compared to C++, but also the advantages of pure FP can not be utilized so easy, and still targetting the browser so easily in a very clean and abstract way is as far is I know a unique characteristic of Elm.


## Concept

OK, now we eventually come to the actual game. ;-)
The pureness of Elm forces us to split it into three parts.

*   The *model* includes all the state of our game like the positions and speed of the objects. We also have to think about the user input we are interested in.
*   The *updates part* describes how the game state transitions from one point in time to a subsequent one, given a certain set of inputs.
*   The *view* finally brings the game state onto the screen.

Let us have a look at how this can look in a [very much simplified version](http://share-elm.com/sprout/527ac4dde4b06194fd2d16ed) of our desired game:

```haskell
import Keyboard
import Window


-- model

direction : Signal Int
direction = lift .x Keyboard.arrows

type Input = { dir:Int, delta:Time }

input : Signal Input
input = (Input <~ direction ~ fps 60)

type Positioned a = { a | x:Float, y:Float }

type Player = Positioned {}

player : Float -> Float -> Player
player x y = { x=x, y=y }

type Game = { player:Player }

defaultGame : Game
defaultGame = { player = player 0 0 }


-- updates

stepGame : Input -> Game -> Game
stepGame {dir,delta} ({player} as game) =
  let
    player' = { player | x <- player.x + delta * toFloat dir }
  in
    { game | player <- player' }

gameState : Signal Game
gameState = foldp stepGame defaultGame input


-- view

main = lift asText gameState
```


### Model

OK, the import stuff should be clear. Now, `direction` is a signal, that has a value of -1, 0 or 1 and updates if the user presses or releases a key. If it is not clear to you what a signal is, I suggest you first read Evan's article [What is Functional Reactive Programming?](http://elm-lang.org/learn/What-is-FRP.elm) before continuing here. I will wait for you to return. =)

`type Input = { dir:Int, delta:Time }` just tells us, that all the inputs we are interested in, is the direction the user is going to with the arrow keys and a time delta. This delta holds the time passed since the last update. We aim for 60 [frames per second](http://elm-lang.org/edit/examples/Reactive/Fps.elm).

For now our Player is a positioned nothing. We use the syntax for [extensible records](http://elm-lang.org/learn/Records.elm) here and define a constructor for it.

Our game just holds the players information, nothing else, and the default game has a player positioned at 0/0.


### Updates

`stepGame` is the one function describing all the changes our game state can ever experience. Given an input and the current game state, it returns the next one.
All we do here is to update the players x position with the direction the user choosed. The direction is multiplied by delta, because we want the game to run at the same speed, even at machines that can not provide the full 60 fps.


### View

For now the view just displays the players coordinates as text. Not very fancy, but enough to see that `stepGame` correctly updates our model.


## Making the game a game

Changing the x value of our player with the keyboard is of course already quite awesome, and we could spend countless hours exploring all corners of this deep new gaming concept, but at some point, we want more. We want bricks and a ball to smash them into pieces.

OK, how do we now get from [this skeleton](http://share-elm.com/sprout/527ac4dde4b06194fd2d16ed) to [the final game](https://github.com/Dobiasd/Breakout)?

First let's complete our model and our view, and then write the update code to will everyhing with life.


### Model

In the final version our `game` record contains not just the player, but also the bricks still left in the game, the ball, the number of spare balls and the number of spare balls left. It should be obvious for what they stand, and their particular types are in the [source](https://github.com/Dobiasd/Breakout). (`contacts` ist just used to count the number of paddle ball collisions for the overall score.)
`type Game = { state:State, gameBall:Ball, player:Player, bricks:[Brick] , spareBalls:Int, contacts:Int }`

The `state` is a more interesting (especially later in the update section). Our game can wait to begin (`Serve`), be in the actual playing phase (`Play`) or be over, and thus be `Won` or `Lost`.

This leads to the following ADT:

`data State = Play | Serve | Won | Lost`

The rest is quite trivial, I guess. Please [tell](mailto:harry@daiw.de) [me](https://www.facebook.com/Dohbi) if I am wrong with this assumption. ;-)


### View

Most parts of the view are quite boring. The function `display` just defines how a given game state will look like on the screen. Most of the techniques used there are covered nicely in [Introduction to Graphics](http://elm-lang.org/learn/courses/beginner/Graphics.elm).

More interesting is how we get the game to always use the browser windows maximally while preserving the correct aspect ratio. In the view configuration we defined `(gameWidth,gameHeight) = (600,400)` but on some devices this may be too small or even too big. Elm makes the scaling very easy. `display` just creates a form with the default game width, but the function we actually lift to handle our `gameState` signal is `displayFullScreen`

```haskell
main = lift2 displayFullScreen Window.dimensions <| dropRepeats gameState

displayFullScreen : (Int,Int) -> Game -> Element
displayFullScreen (w,h) game =
  let
    gameScale = min (toFloat w / gameWidth) (toFloat h / gameHeight)
  in
    collage w h [display game |> scale gameScale]

main = lift2 displayFullScreen Window.dimensions <| dropRepeats gameState
```

`displayFullScreen` just calls [`scale`](http://docs.elm-lang.org/library/Graphics/Collage.elm#scale) with our filled `Form` and the needed scale factor.
This does not mean, that the game is rendered to 600x400 and then the resulting image is scaled, but the whole game is scaled before it is actually rendered onto the sceen. This means that there will be no image scaling artifacts, even on displays with scale factors far from one. :)


### Updates

The Updates should be the coolest part, since it is here where all the action actually happens.











## Conclusion
Writing Breakout in Elm was surprisingly easy and very fun. I am really looking forward to how this awesome language will develop in the next years.

And David, you were right. FP really rocks. ;-)