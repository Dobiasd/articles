# Refactoring - an Example (using Kotlin)

After your customer has given you perfectly clear requirements
you quickly came up with a sound architecture and implement everything in beautiful code.
While you were just about to fly home on your rainbow-colored unicorn,
you wake up and realize, you're actually fighting with adding a new feature to a piece of software,
which has become quite a mess over time internally. It's not even the fault of anyone in particular,
It's just that the use-cases have changed slightly over the lifetime of the application,
and the originally well-meant architecture no longer fits. It has to evolve.

In such a situation it's often helpful to refactor the code before trying to
squeeze the next feature in.
Refactoring means improving the structure of some program without altering its externally observable behavior.
This activity should not be performed just to please the artistic taste of us as developers.
Quite the opposite - it should be the best thing to do economically,
because it will enable us to implement new functionality much faster and with fewer bugs.

This article will depict the process of applying multiple small refactorings to some exemplary piece of code
to end up with a much more maintainable design. While doing so, the code will not break, but its intended behavior will be preserved in between the steps.
(This article is heavily inspired by Martin Fowler. Also many thanks to [Benjamin Zikarsky](https://github.com/bzikarsky) for reviewing this article, and also for constantly helping me learn in general.)

OK, let's dive in. A part of the order system of a pizza delivery looks as follows:

```kotlin
import java.time.DayOfWeek

fun summarize(order: Order): String {
    var result = ""
    var sum = 0
    val weekday = order.date.dayOfWeek
    for (orderLine in order.lines) {
        val article = orderLine.article
        var quantity = orderLine.quantity
        var price = quantity * article.price
        if (weekday == DayOfWeek.TUESDAY && article.type == Article.Type.PIZZA) {
            price = quantity * 500
        }
        if (weekday == DayOfWeek.WEDNESDAY) {
            quantity += quantity / 3
        }
        result += "$quantity * ${article.name} - ${price / 100} $\n"
        sum += price
    }
    if (weekday == DayOfWeek.SATURDAY && sum >= 2500) {
        result += "1 * ${redWine.name} - 0 $\n"
    }
    result += "_____\n"
    result += "total: ${sum / 100} $"
    return result
}
```

With some auxiliary data structures:

```kotlin
import java.time.LocalDate

typealias ArticleId = Long
typealias Cents = Int

class Article(
    val articleId: ArticleId,
    val name: String,
    val price: Cents, // In a real-world project this might be BigDecimal instead
    val type: Type
) {
    enum class Type { PIZZA, PASTA, DRINK }
}

class OrderLine(
    val article: Article,
    val quantity: Int
)

class Order(
    val date: LocalDate,
    private val quantities: Map<ArticleId, Int>
) {
    val lines: List<OrderLine>
        get() = quantities.map { (articleId, quantity) ->
            OrderLine(findArticleById(articleId), quantity)
        }
}

val redWine = Article(4, "Red wine", 300, Article.Type.DRINK)

// Think of this as a repository function accessing an actual database.
fun findArticleById(articleId: Long) =
    listOf(
        Article(1, "Pizza Margherita", 600, Article.Type.PIZZA),
        Article(2, "Pizza Quattro Stagioni", 800, Article.Type.PIZZA),
        Article(3, "Spaghetti Bolognese", 650, Article.Type.PASTA),
        redWine
    ).associateBy(Article::articleId)[articleId] ?: error("Unknown article")
```

For each order, the software prints as summary, respecting weekday-specific discounts.

Two new requirements shall be implemented:

- Format the output not just as plain text but optionally also as markdown instead.
- A new discount mechanism shall replace the default weekday-based ones on certain special days of the year, like New Year's Eve, the Super Bowl weekend and Thanksgiving.

Trying to add this to the existing code without improving it first,
would result in a health-threatening pile of spaghetti code.
So let's prepare the code to make adding those features a breeze.
To make sure we don't destroy anything along the way,
we make sure the functionality is covered by automated unit tests. In case it's not, we create the needed test cases.
Assuming the current implementation works fine,
we can just use its output as the expected results in our test cases:

```kotlin
import java.time.LocalDate
import kotlin.test.assertEquals

// This would use JUnit in a real-world project.
fun testTuesday() {
    assertEquals(
        """
            1 * Pizza Margherita - 5 $
            2 * Pizza Quattro Stagioni - 10 $
            _____
            total: 15 $
        """.trimIndent(),
        summarize(
            Order(
                LocalDate.of(2020, 11, 17),
                mapOf(
                    1L to 1,
                    2L to 2
                )
            )
        )
    )
}

fun testWednesday() {
    assertEquals(
        """
            1 * Pizza Margherita - 6 $
            4 * Spaghetti Bolognese - 19 $
            1 * Red wine - 3 $
            _____
            total: 28 $
        """.trimIndent(),
        summarize(
            Order(
                LocalDate.of(2020, 11, 18),
                mapOf(
                    1L to 1,
                    3L to 3,
                    4L to 1
                )
            )
        )
    )
}

fun testSaturday() {
    assertEquals(
        """
            4 * Pizza Quattro Stagioni - 32 $
            1 * Red wine - 0 $
            _____
            total: 32 $
        """.trimIndent(),
        summarize(
            Order(
                LocalDate.of(2020, 11, 21),
                mapOf(
                    2L to 4
                )
            )
        )
    )
}
```

We run the tests (they should be green), and then we commit them to our [VCS](https://en.wikipedia.org/wiki/Version_control).

To tackle the actual implementation, we first need to identify what
the original code is doing by reading it or maybe even stepping through it with a debugger.
We should persist the new understanding, we gain from this, directly into the code.
We do this by simply just renaming some variables and by using comments:

![diff_a_b](refactoring_-_an_example_using_kotlin/diff_a_b.png?raw=true)

Result:

```kotlin
import java.time.DayOfWeek

fun summarize(order: Order): String {
    var result = ""
    var total: Cents = 0
    val weekday = order.date.dayOfWeek
    for (orderLine in order.lines) {
        val article = orderLine.article
        var quantity = orderLine.quantity
        var charge = quantity * article.price
        // Tuesday: Every Pizza for 5 bucks
        if (weekday == DayOfWeek.TUESDAY && article.type == Article.Type.PIZZA) {
            charge = quantity * 500
        }
        // Wednesday: Buy 3, get 4.
        else if (weekday == DayOfWeek.WEDNESDAY) {
            quantity += quantity / 3
        }
        result += "$quantity * ${article.name} - ${charge / 100} $\n"
        total += charge
    }
    // Saturday: Give out red whine as a gift for large orders.
    if (weekday == DayOfWeek.SATURDAY && total >= 2500) {
        result += "1 * ${redWine.name} - 0 $\n"
    }
    result += "_____\n"
    result += "total: ${total / 100} $"
    return result
}
```

(After this step, as after every step, we again run the tests and commit our code.)

In the next step we should try to separate the observed concerns, i.e.:

- accumulating the (possibly discount-affected) charges
- and formatting the lines and the total to strings

To help with this, we can convert the imperative code into something a bit more functional:

![diff_b_c](refactoring_-_an_example_using_kotlin/diff_b_c.png?raw=true)

```kotlin
import java.time.DayOfWeek

fun summarize(order: Order): String {
    val weekday = order.date.dayOfWeek
    var summaryLines = order.lines.map { orderLine ->
        val article = orderLine.article
        var quantity = orderLine.quantity
        var charge = quantity * article.price
        // Tuesday: Every Pizza for 5 bucks
        if (weekday == DayOfWeek.TUESDAY && article.type == Article.Type.PIZZA) {
            charge = quantity * 500
        }
        // Wednesday: Buy 3, get 4.
        else if (weekday == DayOfWeek.WEDNESDAY) {
            quantity += quantity / 3
        }
        Pair("$quantity * ${article.name} - ${charge / 100} $", charge)
    }
    val total = summaryLines.sumBy { it.second }
    // Saturday: Give out red whine as a gift for large orders.
    if (weekday == DayOfWeek.SATURDAY && total >= 2500) {
        summaryLines = summaryLines + Pair("1 * ${redWine.name} - 0 $", 0)
    }
    return (summaryLines.map { it.first } +
            "_____" +
            "total: ${total / 100} $")
        .joinToString("\n")
}
```

(test, commit)

This phase split reveals, that we are actually converting the `OrderLine`s into something else.
Right now it's just a `Pair<String, Cents>`.
So, let's call it `SummaryLines` to express this concept explicitly in our domain by using value objects:

![diff_c_d](refactoring_-_an_example_using_kotlin/diff_c_d.png?raw=true)

```kotlin
import java.time.DayOfWeek

class SummaryLine(
    private val quantity: Int,
    private val article: Article,
    val charge: Cents
) {
    fun show() = "$quantity * ${article.name} - ${charge / 100} $"
}

fun summarize(order: Order): String {
    val weekday = order.date.dayOfWeek
    var summaryLines = order.lines.map { orderLine ->
        val article = orderLine.article
        var quantity = orderLine.quantity
        var charge = quantity * article.price
        // Tuesday: Every Pizza for 5 bucks
        if (weekday == DayOfWeek.TUESDAY && article.type == Article.Type.PIZZA) {
            charge = quantity * 500
        }
        // Wednesday: Buy 3, get 4.
        else if (weekday == DayOfWeek.WEDNESDAY) {
            quantity += quantity / 3
        }
        SummaryLine(quantity, article, charge)
    }
    val total = summaryLines.sumBy(SummaryLine::charge)
    // Saturday: Give out red whine as a gift for large orders.
    if (weekday == DayOfWeek.SATURDAY && total >= 2500) {
        summaryLines = summaryLines + SummaryLine(1, redWine, 0)
    }
    return (summaryLines.map(SummaryLine::show) +
            "_____" +
            "total: ${total / 100} $")
        .joinToString("\n")
}
```

(...)

That's a lot better because we already separated the calculations from the output formatting.
It can now easily be moved into a separate function,
making it simple to add the desired Markdown support later.

Next, we see a quite low-hanging fruit.
The logic to format a monetary amount as a string exists in more than one place.
We can extract it out into a function,
making the code more [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).

![diff_d_e](refactoring_-_an_example_using_kotlin/diff_d_e.png?raw=true)

```kotlin
import java.time.DayOfWeek

class SummaryLine(
    private val quantity: Int,
    private val article: Article,
    val charge: Cents
) {
    fun show() = "$quantity * ${article.name} - ${showMoney(charge)}"
}

fun List<SummaryLine>.total() = sumBy(SummaryLine::charge)

fun showMoney(amount: Cents) = "${amount / 100} $"

fun summarize(order: Order): String {
    val weekday = order.date.dayOfWeek
    var summaryLines = order.lines.map { orderLine ->
        val article = orderLine.article
        var quantity = orderLine.quantity
        var charge = quantity * article.price
        // Tuesday: Every Pizza for 5 bucks
        if (weekday == DayOfWeek.TUESDAY && article.type == Article.Type.PIZZA) {
            charge = quantity * 500
        }
        // Wednesday: Buy 3, get 4.
        else if (weekday == DayOfWeek.WEDNESDAY) {
            quantity += quantity / 3
        }
        SummaryLine(quantity, article, charge)
    }
    // Saturday: Give out red whine as a gift for large orders.
    if (weekday == DayOfWeek.SATURDAY && summaryLines.total() >= 2500) {
        summaryLines = summaryLines + SummaryLine(1, redWine, 0)
    }
    return (summaryLines.map(SummaryLine::show) +
            "_____" +
            "total: ${showMoney(summaryLines.total())}")
        .joinToString("\n")
}
```

The introduction of the extension function `List<SummaryLine>.total` also brings
us one step closer to the goal of avoiding to work on multiple levels of abstraction at once.

Now, the discount logic should become more modular to help to add new policies,
like "One free Margharita on Thanksgiving", later.
We realize, that, basically,
we are just choosing a different (and isolated) discount strategy depending on the weekday.
The new discount requirements, mentioned in the introduction, also fit into this concept.
The strategies all convert a list of some `OrderLine`s into a list of `SummaryLine`s.
Expressing this insight in code might look as follows:

![diff_e_f](refactoring_-_an_example_using_kotlin/diff_e_f.png?raw=true)

```kotlin
import java.time.DayOfWeek

class SummaryLine(
    private val quantity: Int,
    private val article: Article,
    val charge: Cents
) {
    fun show() = "$quantity * ${article.name} - ${showMoney(charge)}"
}

fun List<SummaryLine>.total() = sumBy(SummaryLine::charge)

fun showMoney(amount: Cents) = "${amount / 100} $"

fun noDiscount(orderLines: List<OrderLine>) = orderLines.map {
    SummaryLine(it.quantity, it.article, it.quantity * it.article.price)
}

fun everyPizzaFor5Bucks(orderLines: List<OrderLine>) = orderLines.map {
    when (it.article.type) {
        Article.Type.PIZZA ->
            SummaryLine(it.quantity, it.article, it.quantity * 500)
        else ->
            SummaryLine(it.quantity, it.article, it.quantity * it.article.price)
    }
}

fun buy3Get4(orderLines: List<OrderLine>) = orderLines.map {
    SummaryLine(
        it.quantity + it.quantity / 3,
        it.article,
        it.quantity * it.article.price
    )
}

fun freeWineForLargeOrders(orderLines: List<OrderLine>) =
    orderLines.map {
        SummaryLine(it.quantity, it.article, it.quantity * it.article.price)
    }.let {
        if (it.total() >= 2500)
            it + SummaryLine(1, redWine, 0)
        else
            it
    }

fun summarize(order: Order): String {
    val summaryLines = when (order.date.dayOfWeek) {
        DayOfWeek.TUESDAY -> everyPizzaFor5Bucks(order.lines)
        DayOfWeek.WEDNESDAY -> buy3Get4(order.lines)
        DayOfWeek.SATURDAY -> freeWineForLargeOrders(order.lines)
        else -> noDiscount(order.lines)
    }
    return (summaryLines.map(SummaryLine::show) +
            "_____" +
            "total: ${showMoney(summaryLines.total())}")
        .joinToString("\n")
}
```

To avoid the duplication of calculating `charge` as the product of `quantity` and `article.price`,
we move this into a secondary constructor of our `SummaryLine` class:

![diff_f_g](refactoring_-_an_example_using_kotlin/diff_f_g.png?raw=true)

```kotlin
import java.time.DayOfWeek

class SummaryLine(
    private val quantity: Int,
    private val article: Article,
    val charge: Cents
) {
    constructor(orderLine: OrderLine) : this(
        orderLine.quantity,
        orderLine.article,
        orderLine.quantity * orderLine.article.price
    )

    fun show() = "$quantity * ${article.name} - ${showMoney(charge)}"
}

fun List<SummaryLine>.total() = sumBy(SummaryLine::charge)

fun showMoney(amount: Cents) = "${amount / 100} $"

fun noDiscount(orderLines: List<OrderLine>) = orderLines.map(::SummaryLine)

fun everyPizzaFor5Bucks(orderLines: List<OrderLine>) = orderLines.map {
    when (it.article.type) {
        Article.Type.PIZZA ->
            SummaryLine(it.quantity, it.article, it.quantity * 500)
        else ->
            SummaryLine(it)
    }
}

fun buy3Get4(orderLines: List<OrderLine>) = orderLines.map {
    SummaryLine(
        it.quantity + it.quantity / 3,
        it.article,
        it.quantity * it.article.price
    )
}

fun freeWineForLargeOrders(orderLines: List<OrderLine>) =
    orderLines.map(::SummaryLine).let {
        if (it.total() >= 2500)
            it + SummaryLine(1, redWine, 0)
        else
            it
    }

fun summarize(order: Order): String {
    val summaryLines = when (order.date.dayOfWeek) {
        DayOfWeek.TUESDAY -> everyPizzaFor5Bucks(order.lines)
        DayOfWeek.WEDNESDAY -> buy3Get4(order.lines)
        DayOfWeek.SATURDAY -> freeWineForLargeOrders(order.lines)
        else -> noDiscount(order.lines)
    }
    return (summaryLines.map(SummaryLine::show) +
            "_____" +
            "total: ${showMoney(summaryLines.total())}")
        .joinToString("\n")
}
```

The decision which [strategy](https://en.wikipedia.org/wiki/Strategy_pattern)
to use can now be separated out into some kind of [factory](https://en.wikipedia.org/wiki/Factory_method_pattern).

![diff_g_h](refactoring_-_an_example_using_kotlin/diff_g_h.png?raw=true)

```kotlin
import java.time.DayOfWeek
import java.time.LocalDate

class SummaryLine(
    private val quantity: Int,
    private val article: Article,
    val charge: Cents
) {
    constructor(orderLine: OrderLine) : this(
        orderLine.quantity,
        orderLine.article,
        orderLine.quantity * orderLine.article.price
    )

    fun show() = "$quantity * ${article.name} - ${showMoney(charge)}"
}

fun List<SummaryLine>.total() = sumBy(SummaryLine::charge)

fun showMoney(amount: Cents) = "${amount / 100} $"

fun noDiscount(orderLines: OrderLines) = orderLines.map(::SummaryLine)

fun everyPizzaFor5Bucks(orderLines: OrderLines) = orderLines.map {
    when (it.article.type) {
        Article.Type.PIZZA ->
            SummaryLine(it.quantity, it.article, it.quantity * 500)
        else ->
            SummaryLine(it)
    }
}

fun buy3Get4(orderLines: OrderLines) = orderLines.map {
    SummaryLine(
        it.quantity + it.quantity / 3,
        it.article,
        it.quantity * it.article.price
    )
}

fun freeWineForLargeOrders(orderLines: OrderLines) =
    orderLines.map(::SummaryLine).let {
        if (it.total() >= 2500)
            it + SummaryLine(1, redWine, 0)
        else
            it
    }

fun createDiscountStrategy(date: LocalDate) =
    when (date.dayOfWeek) {
        DayOfWeek.TUESDAY -> ::everyPizzaFor5Bucks
        DayOfWeek.WEDNESDAY -> ::buy3Get4
        DayOfWeek.SATURDAY -> ::freeWineForLargeOrders
        else -> ::noDiscount
    }

fun summarize(order: Order): String {
    val summaryLines = createDiscountStrategy(order.date)(order.lines)
    return (summaryLines.map(SummaryLine::show) +
            "_____" +
            "total: ${showMoney(summaryLines.total())}")
        .joinToString("\n")
}
```

We could create an interface for our strategy, e.g.:

```kotlin
interface DiscountStrategy {
    fun execute(orderLines: OrderLines): SummaryLines
}
```

and embed the different strategies in classes that implement it,
but since each strategy just needs one method,
we can also treat the function [first-class](https://en.wikipedia.org/wiki/First-class_function)
and use the function type (signature),
i.e., `(List<OrderLine>) -> List<SummaryLine>` in our case, as our interface directly.

The code now looks very nice. Yes, it's a bit longer than the original,
and usually shorter is better.
However, we converted the entangled spaghetti code to concern-separated ravioli.
Also, most of the new code is declarative, which is good,
because it's harder to make mistakes in it. The type system helps us here.
It will now be much simpler to not only to add markdown output,
but also to add new discount strategies, because they are nicely isolated.
In addition, the understanding of what is happening is now embedded in the code,
such that it can be understood without the need for comments,
that might accidentally become outdated with subsequent changes.

Of course, we could implement a more complex invoice representation with customer profiles,
taxes, shipping, and whatnot.
But applying the [YAGNI principle](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it) here,
we don't need to do this until future requirements impose such a change.

If this happens, we can still happily continue to refactor then. :)
