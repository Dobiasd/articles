# Switching from imperative to functional programming with games in Elm

Imperative programming was my thing since I was a school boy. I wrote
some small games and [demoscene](http://en.wikipedia.org/wiki/Demoscene)
effects, and now develop software (primarily computer vision stuff) for a living.
Recently it was mainly C++ and some Python I worked with. During the last
year, [David](https://github.com/quchen), a good friend and Haskell
expert, tried to evangelize me with the benefits of functional programming
(FP). So I read [SICP](http://mitpress.mit.edu/sicp) and
[LYAH](http://learnyouahaskell.com). I actually understood some parts,
although not all, and solved few and very small [toy
problems](http://projecteuler.net/problems) in Scheme and Haskell. But I did
not see how one could use such a programming style voluntarily, because the
imperative solutions came about an order of magnitude quicker to my mind than
the functional ones did.

Of course, in C++ I now used a bit more from the
[algorithm header](http://en.cppreference.com/w/cpp/algorithm) and also tried
[some functional things](http://docs.python.org/3/howto/functional.html) in
Python, yet I just did not feel how digging deeper into this paradigm could
really be worth the trouble. E.g. why should I `foldr` over a list if I can
`for`-loop over an array? In retrospect it perhaps also was the uncomfortable
situation of again being a complete newbie that kept me from
continuing.

Whatever it was, I more or less accidentally stumbled upon
[Elm](http://elm-lang.org). The [examples](http://elm-lang.org/Examples.elm)
did not look so scary like many type theory filled Haskell tutorials, so I
gave it a shot and read trough all the
[tutorials/articles](http://elm-lang.org/Learn.elm) while constantly [playing
around](http://elm-lang.org/try) with the stuff I just found out.

After solving the challenges in the [pong tutorial]
(http://elm-lang.org/blog/Pong.elm) I
decided to write this [Breakout clone](https://github.com/Dobiasd/Breakout),
which turned out to be a very interesting and fun undertaking. **[Try it
out!](http://daiw.de/games/breakout)** :-)

Even though some of the following things will sound naive to experienced
FP developers (or even to me in some months or years),
the rest of this little essay will describe my learning experience
with that project, how it is structured and why it finally convinced me of the
advantages of functional (reactive) programming and motivated me to
immediately continue with [a second game project]
(https://github.com/Dobiasd/Maze). It is not meant to serve as a
full FP or game development tutorial, but perhaps it can inspire you to have
a deeper look into the FP paradigm and then maybe share my excitement. :-)


## Differences to a hypothetical imperative implementation in C++

If I had written this game (resp. a non browser
version of it) in C++, I probably would have used
[SFML](http://www.sfml-dev.org), which is a very good library for making games
like this. I already used it to write a [Snake like
game](https://github.com/Dobiasd/Dron). My cost estimations for that project
would probably be more man-days than it surprisingly took me to do it in Elm,
a language I had no experience with at all!

One reason for that is the much
shorter edit/compile cycle in Elm, which reduces to just one click in your
browser. But OK, except the
[hot-swapping](http://elm-lang.org/blog/Interactive-Programming.elm), that is
also possible with some imperative languages.
The much more astonishing fact
for me was, that I did not need many of these cycles. Sometimes I wrote code
for nearly an hour and as soon as [Elm's Haskell like type
system](http://elm-lang.org/learn/Understanding-Types.elm) did not give
me errors any more while compiling, the code just worked! There was very
rarely a need to debug it at all! I guess this comes from the notion, that if
you look at a pure functions you just have to think about what it stands for
and not what I will do to something else under certain circumstances etc. Also
when just thinking in [expressions and no more in
statements](http://stackoverflow.com/questions/4728073/what-is-the-difference-between-an-expression-and-a-statement-in-python),
there is not so much control flow you have to emulate in your head. And it is
easier to structure your code. The temptation to write spaghetti code
functions is not that big and if one still grows too long, it is very easy to
factor out the parts that can stand meaningful for their own. Furthermore the
refactoring is not scary at all. I didn't introduce one single bug while
factoring out stuff to add new functionality, like the traction between the
paddle and the ball.

Also everything is much more concise. Just compare the
two following snippets:

```c++
std::list<int> l;
for ( int i = 1; i <= 10; ++ i )
    l.push_back( i * i );
```

```haskell
l = map ((^)2) [1..10]
```

Sure, what is more readable/pretty is also a matter or habit/taste. But
beside the terseness there come other benefits with the abstract separation
of the control structure, e.g. if you want to decide from the outside
what to do with the values:

```haskell
buildPairs l f = map2 (,) l <| map f l
l1 = buildPairs [1..5] ((^)2)
l2 = buildPairs [1..5] sqrt
l3 = buildPairs [1..5] ((*)2)
l4 = buildPairs [1..5] ((+)1)
```

You can also decide which direction you prefer to read:

```haskell
la = map ((^)2) [1..10]    -- normal function application
lb = ((^)2) `map` [1..10]  -- infix notation
lc = [1..10] |> map ((^)2) -- forward application
```

And many design patterns involving inheritance and boilerplate
code in C++ just disintegrate into thin air when you have functions as [first
class citizen](http://en.wikipedia.org/wiki/First-class_function) in FP.

Don't get me wrong. I don't want to bash C++, and I
still think it is a great language if it comes to performance critical system
programming, and I will continue to use it for appropriate tasks. But the high
control over nearly every byte in your system comes at the cost of increased
development time. So every tool has its usage. You probably *can* get a screw
into a wall using a hammer, but if you feel that a big part of your effort is
wasted energy, there is presumably a better solution. ;-)

Sure, with Python things would likely have been much different
compared to C++, but also there the [advantages of pure FP]
(http://www.haskell.org/haskellwiki/Functional_programming#Benefits_of_functional_programming)
can not always be utilized fully, and still targetting the browser so easily
in a very clean and abstract way is as far is I know a unique characteristic
of Elm.


## Concept

OK, now we eventually come to
the actual game. ;-)
The pureness of Elm forces us to split it into three
parts.

*   The **model** includes all the state of our game like the
positions and speed of the objects. We also have to think about the user input
we are interested in.
*   The **updates** part describes how the game states
transition from one point in time to a subsequent one, given a certain set of
inputs.
*   The **view** finally brings the game state onto the
screen.

Let's examine how this can look in a very much simplified version of our desired game:

```haskell
-- skeleton

import List exposing (map, map2)

import Graphics.Element exposing (show, Element)
import Keyboard
import Text
import Time exposing (Time, fps)
import Signal exposing (Signal, (<~), (~), foldp)
import Signal
import Window


-- model

direction : Signal Int
direction = Signal.map .x Keyboard.arrows

type alias Input = { dir:Int, delta:Time }

input : Signal Input
input = (Input <~ direction ~ fps 60)

type alias Positioned a = { a | x:Float }

type alias Player = Positioned {}

player : Float -> Player
player x = { x=x }

type alias Game = { player:Player }

defaultGame : Game
defaultGame = { player = player 0 }


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

main : Signal Element
main = Signal.map show gameState
```


### Model

OK,
the import stuff should be clear. Now, `direction` is a signal that has a
value of -1, 0 or 1 and updates if the user presses or releases a key. If it
is not clear to you what a signal is, I suggest you first read Evan's article
[What is Functional Reactive
Programming?](http://elm-lang.org/learn/What-is-FRP.elm) before continuing
here. I will wait here for you to return. =)

`type alias Input = { dir:Int,
delta:Time }` just tells us, that all the inputs we are interested in are the
direction the user is going to with the arrow keys and a time delta. This
delta holds the time passed since the last update. We aim for 60 [frames per
second](http://elm-lang.org/edit/examples/Reactive/Fps.elm).

For now our
`Player` is a `positioned` nothing. We use the syntax for [extensible
records](http://elm-lang.org/learn/Records.elm) here and define a constructor
for it.

Our `Game` just holds the players information, nothing else, and
the default game has a player positioned at 0/0.


### Updates

`stepGame` is the one function describing all the changes our game
state can ever experience. Given an input and the current game state, it
returns the next one.
All we do for now is to update the players x position
with the direction the user chooses. The direction is multiplied by `delta`,
because we want the game to always run at the same absolute speed, even at
machines that can not provide the full 60 fps.


### View

At the moment
the view just displays the players coordinates as text. Not very fancy, but
enough to see that `stepGame` correctly updates our model.


## Making the game a game

Changing the x value of our player with the keyboard is of
course already extremely awesome, and we could spend countless hours exploring
all corners of this deep new gaming concept, but at some point we want more.
We want bricks and a ball to smash them into pieces.

So how do we now get
from our skeleton to
[the final game](https://github.com/Dobiasd/Breakout/blob/master/Main.elm)?

First let
us complete our model and our view, and then write the update code to will
everything with life.


### Model

In the final version our `game` record
contains not just the player, but also the bricks still left in the game, the
ball and the number of spare balls.

```haskell
type alias Game = { state:State
                  , gameBall:Ball
                  , player:Player
                  , bricks:List Brick
                  , spareBalls:Int
                  , contacts:Int }
```

It should be obvious for what the single record entries stand, and
their particular types are in the
[source](https://github.com/Dobiasd/Breakout/blob/master/Main.elm).
(`contacts` is just used to count the number of paddle ball collisions for the
overall score.)

The `state` is a more interesting (especially later in the
update section). Our game can wait to begin (`Serve`), be in the actual
playing phase (`Play`) or be over and thus be `Won` or `Lost`.

This leads
to the following ADT:

`type State = Play | Serve | Won | Lost`

The rest
is quite trivial, I guess. Please [tell](mailto:harry@daiw.de)
[me](https://www.facebook.com/Dohbi) if I am wrong with this assumption.
;-)


### View

Most parts of the view are somewhat boring, because Elm
makes all this *very* easy. The function `display` just defines how a given
game state will look like on the screen. Most of the techniques used there are
covered nicely in [Introduction to
Graphics](http://elm-lang.org/learn/courses/beginner/Graphics.elm).

More
interesting is how we get the game to always use the browser windows maximally
while preserving the correct aspect ratio. In the view configuration we
defined `(gameWidth,gameHeight) = (600,400)` but on some devices this may be
too small or even too big. Elm makes the scaling a charm. We define everything
in out default size, but use `displayFullScreen` to fit it to our screen.

```haskell
displayFullScreen : (Int,Int) -> Form -> Element
displayFullScreen (w,h) content =
  let
    gameScale = min (toFloat w / gameWidth) (toFloat h / gameHeight)
  in
    collage w h [content |> scale gameScale]
```

`displayFullScreen` just
calls [`scale`](http://package.elm-lang.org/packages/elm-lang/core/1.0.0/Graphics-Collage#scale)
with our filled `Form` and the needed scale factor.
This does not mean, that
the game is rendered to 600x400 and then the resulting image is scaled, no.
The whole game is scaled before it is actually rendered onto the screen. This
means that there will be no image scaling artifacts, even on displays with
scale factors far away from '1.0'. :)


### Updates

The Updates are the coolest part since it is here where all the action actually
happens.

Let's see, we
[`foldp`](http://package.elm-lang.org/packages/elm-lang/core/1.0.0/Signal#foldp) over our
`defaultGame` with `stepGame`, so let's look at this.

```haskell
stepGame : Input -> Game -> Game
stepGame ({dir,delta} as input) ({state,player} as game) =
  let
    func = if | state == Play  -> stepPlay
              | state == Serve -> stepServe
              | otherwise      -> stepGameOver
  in
    func input { game | player <- stepPlayer delta dir player }
```

Since the paddle can be moved regardless of the game state, the
players position is already updated here. All the other actions are state
specific, so the remaining tasks are dispatched by the current
state.

`stepServe` and `stepGameOver` do nothing special, so let's look at
`stepPlay`:

```haskell
stepPlay : Input -> Game -> Game
stepPlay {delta} ({gameBall,player,bricks,spareBalls,contacts} as game) =
  let
    ballLost = gameBall.y - gameBall.r < -halfHeight
    gameOver = ballLost && spareBalls == 0
    spareBalls' = if ballLost then spareBalls - 1 else spareBalls
    state' = if | gameOver -> Lost
                | ballLost -> Serve
                | List.isEmpty bricks -> Won
                | otherwise -> Play
    ((ball', bricks'), contacts') =
      stepBall delta gameBall player bricks contacts
  in
    { game | state      <- state'
           , gameBall   <- ball'
           , bricks     <- bricks'
           , spareBalls <- max 0 spareBalls' -- No -1 when game is lost.
           , contacts   <- contacts' }
```

If our ball is lost and we do not have any
spare balls left, the game is over. Simple. `stepBall` seems to be the place
where the collision is handled.
It's type already tells us a lot about
it:
`stepBall : Time -> Ball -> Player -> [Brick] -> Int -> ((Ball,[Brick]),
Int)`
Using a time delta, it takes values of the ball, player and bricks and
returns new values for them. The number of paddle ball contacts may also be
increased.

```haskell
stepBall : Time.Time -> Ball -> Player -> List Brick -> Int
           -> ((Ball, List Brick), Int)
stepBall t ({x,y,vx,vy} as ball) p bricks contacts =
  let
    hitPlayer = (ball `within` p)
    contacts' = if hitPlayer then contacts + 1 else contacts
    newVx = if hitPlayer then
               weightedAvg [p.vx, vx] [traction, 1-traction] else
               stepV vx (x < (ball.r-halfWidth)) (x > halfWidth-ball.r)
    hitCeiling = (y > halfHeight - ball.r)
    ball' = stepObj t { ball | vx <- newVx ,
                               vy <- stepV vy hitPlayer hitCeiling }
  in
    (List.foldr goBrickHits (ball',[]) bricks, contacts')
```

First it checks for paddle player
collisions and updates the ball's velocity and the contact count
accordingly.

The return type (`((Ball,List Brick), Int)`) may look somewhat
odd at first glance, but thanks to [pattern
matching](http://elm-lang.org/learn/Union-Types.elm) it did not pose a
problem for the caller (stepPlay):
`((ball', bricks'), contacts') =
stepBall ...`
And it renders itself quite handy when looking at `(foldr
goBrickHits (ball',[]) bricks, contacts')`

OK, what does `foldr
goBrickHits (ball',[])` do?
I will not explain the behaviour of [folds in general]
(http://www.haskell.org/haskellwiki/Fold#List_folds_as_structural_transformations)
here, but in our case the used function `goBrickHits` takes one single brick
at a time and the accumulator, which we initially set to `(ball',[])`. It
contains the already changed ball and at first no bricks at
all:

```haskell
goBrickHits : Brick -> (Ball,List Brick) -> (Ball,List Brick)
goBrickHits brick (ball,bricks) =
  let
    hit = ball `within` brick
    bricks' = if hit then bricks else brick::bricks
    ball' = if hit then { ball | vy <- -ball.vy } else ball
  in
    (if hit then speedUp ball' else ball', bricks')
```

Initially it checks if the
ball is colliding with the current brick, and if this is true we do not put
this brick in our accumulator since it just was destroyed by the ball. We also
invert the balls vertical speed. If no hit occurred, we just
[cons](http://en.wikipedia.org/wiki/Cons) the brick to the bricks that are
still in the game. Et voilà. Who needs `for`-loops anymore?
:-)

---------------------------------------

OK, that's it. Since at the moment of writing I'm quite new to all this,
I guess there is still much room for improvement of the code and this
article.
If you have suggestions please [let me know](mailto:harry@daiw.de). :-)


## Conclusion

Writing
Breakout in Elm was surprisingly easy and a lot of fun. It was the one
experience I needed to get practice and thus gain confidence in programming
purely functional. I am really looking forward to learning more about Elm (and
FP in general) and how this awesome language will develop during the next
years.

And David, you were right. FP really rocks. ;-)

[Discuss on reddit](http://www.reddit.com/r/programming/comments/1q4exc/switching_from_imperative_to_functional/)