# How touch typing and keyboard shortcuts can improve the quality of the software you create

Recently on [proggit](http://www.reddit.com/r/programming/comments/2nvt2w/the_case_for_slow_programming/) I found an [article](https://ventrellathing.wordpress.com/2013/06/18/the-case-for-slow-programming/) advocating a well thought out design process in software development. I mostly agreed. But one sentence made me cringe:

> I'm Glad I'm not a Touch-Typist.

First of all, I do not think that being able to touch type is an indispensable prerequisite for being a good programmer since we often write [astonishing few lines of code per day](http://skeptics.stackexchange.com/questions/17224/do-professional-software-developers-write-an-average-of-10-lines-of-code-per-day) and have many of our ideas while not sitting in front of our computer. Yet, I'm very glad I can use **touch typing**, because it [makes one type faster](http://en.wikipedia.org/wiki/Touch_typing#Speed), and I think even though this does not improve development speed significantly in the short run, it **improves the quality of the software one produces**. In this short article, I will explain why I believe this. Although it is just a gut feeling probably based on subjective observation, and I do not have empirical evidence, I still hope you will find some points here that make sense to you.

## Nano decisions and threshold

In our everyday lives, we unconsciously make very small decisions all the time. Every few seconds we do something that can be done in many different ways, but we mostly stick to our habits, and the skill set we have and the environment we live in influences our nano decisions.

Take cooking as an example: You are in the middle of preparing a delicious dinner and you want to cut your veggies in a special way. A [tourné knife](http://cooking.stackexchange.com/questions/37818/what-is-a-tourne-knife-used-for) would be ideal for this, but yours is somewhere in the conservatory from you having your last snack there. You probably will just use your paring knife, because it already is right in front of you on your chopping board, and using it instead will decrease the quality of your meal only very slightly.

Being a slow typist is like having your kitchen tools badly organized.

You are writing some code that is partly self-explanatory. It would be nicer with an additional comment, but not really disastrous without it. The cost of making that tiny change, measured in time of thought-interruption and thus cognitive load, is lower if you are able to type fast. So the benefit-cost ratio can end up below the "write the comment" threshold if you are a slow typist and above it otherwise. Other thresholds could be about "use a more descriptive name for that function/variable", "make this small refactoring", "ask a question on [stackoverflow](http://stackoverflow.com)" or anything along these lines.


## Keyboard shortcuts

Perhaps even more important than fast typing is the skill to use keyboard shortcuts efficiently. Not having to look at your fingers while using them also helps, since you can react much better. If I see someone looking at his keyboard while editing text, I always think of a tennis player not watching the ball and his opponent, but staring at his racket the whole game. It gets even more [funny](http://steve-yegge.blogspot.de/2008/09/programmings-dirtiest-little-secret.html), if their IDE is constantly providing the correct autocomplete suggestions, but they just don't notice it.
The keyboard should not feel like an external device you are trying to manipulate but like a natural extension of your body, that enhances your capabilities.
In this condition, your typing is less likely to destructively interrupt your train of thought due to its duration and shift of focus.


So if you do not have to carry the constant burden of having to watch your fingers, some things become much easier. If you know the shortcuts, you automatically start to use "ctrl+f, F3" for searching something instead of scrolling with your mouse, write stuff in text files instead of paper ([greppability](http://en.wiktionary.org/wiki/greppable) is a big advantage.), etc.

This again influences your software development decisions. Say you are not 100% sure about a fact. You could just assume it or look it up, e.g. in a log file or online API documentation. If you are able to open the file/page and navigate to the right spot in a few seconds, you are more likely to really do it, which reduces the risk of making a mistake by relying on a wrong assumption.


## Pair programming and alike

If you are at the computer with somebody else, it can even improve your relationship if you are skilled in the things mentioned above. If you are, and the other person is not, you are a good example, and perhaps even an inspiration if you are really impressive.
On the other hand, if the person by your side would be much faster than you, they can get really annoyed by just having to watch you using the PC unnecessary slowly.


## Conclusion

Fast typing (+blind, +shortcuts) can not only improve your speed but particularly also the quality you produce.

Having your flow interrupted while programming is rarely a good thing. Causes for this include disruptive colleagues/managers, slow hardware (compile times, etc.) and tying disability. If you not yet have eliminated the third one (and I've seen it many times even in experienced developers), I suggest the following:

* Learn to type without looking at your fingers. Just using a Sharpie to paint your keys black can work wonders. Perhaps use a game like [Z-Type](http://phoboslab.org/ztype/).
* Find and Memorize the keyboard shortcuts for your operating system and software.
* Put your mouse away and operate the PC without it for a few days to practice the shortcuts and to evaluate which of them are helpful and which are not.
* Use the console/terminal more.
* Additionally, become a master at rearranging text (select, copy, paste, etc.) with your keyboard only. To practice it you can go to the [EditGym](http://www.editgym.com/text-editing-training/).


So, do you think CEOs should give their developers [black keyboards](http://www.daskeyboard.com/daskeyboard-4-ultimate/) and throw their mice out of the window to increase their productivity in the long run? ;-) ([comment on reddit](http://www.reddit.com/r/programming/comments/2q3uwe/how_touch_typing_and_keyboard_shortcuts_can/))
