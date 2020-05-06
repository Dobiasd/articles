# Using `fold` to mimic mutation

(This article uses Kotlin to depict the idea with code. However, the actual idea is language-agnostic.)

Usually, when thinking of [`fold`](https://en.wikipedia.org/wiki/Fold_(higher-order_function)), something like the following comes to one's mind:

```kotlin
fun multiply(a: Int, b: Int) = a * b

fun product(xs: List<Int>) = xs.fold(1, ::multiply)
```

I.e., using it to simply combine all elements of some iterable thing with an operator. (`listOf(5, 6, 7).fold(1, ::multiply)` expands to `((1 * 5) * 6) * 7`.)

But it can also be used to simulate mutation in a purely functional style. But before going into this, let's set up a trivial mutation example:

```kotin
data class Foo(
    var bar: Int,
    val baz: String
)

fun mutateTimes2(foo: Foo) {
    foo.bar = foo.bar * 2
}

fun mutatePlus3(foo: Foo) {
    foo.bar = foo.bar + 3
}

fun main() {
    val x = Foo(1, "hi")
    mutateTimes2(x)
    mutatePlus3(x)
    println(x) // Foo(bar=5, baz=hi)
}
```

In a functional setting, we would not mutate our `foo`, but instead, create new instances with a different value for `bar` (because of thread safety and stuff):

```kotlin
data class Foo(
    val bar: Int,
    val baz: String
)

fun withBarTimes2(foo: Foo) =
    foo.copy(bar = foo.bar * 2)

fun withBarPlus3(foo: Foo) =
    foo.copy(bar = foo.bar + 3)

fun main() {
    val x = Foo(1, "hi")
    val temp = withBarTimes2(x)
    val y = withBarPlus3(temp)
    println(y) // Foo(bar=5, baz=hi)
}
```

In our mutation example, let's first put the mutating functions into a list to iterate over:

```kotlin
data class Foo(
    var bar: Int,
    val baz: String
)

fun mutateTimes2(foo: Foo) {
    foo.bar = foo.bar * 2
}

fun mutatePlus3(foo: Foo) {
    foo.bar = foo.bar + 3
}

fun main() {
    var x = Foo(1, "hi")
    listOf(
        ::mutateTimes2,
        ::mutatePlus3
    ).forEach {
        it(x)
    }
    println(x) // Foo(bar=5, baz=hi)
}
```

Now, when squinting hard enough, we can see how to express this analogously in our functional code by using a (left) [`fold`](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/fold.html):

```kotlin
data class Foo(
    val bar: Int,
    val baz: String
)

fun withBarTimes2(foo: Foo) =
    foo.copy(bar = foo.bar * 2)

fun withBarPlus3(foo: Foo) =
    foo.copy(bar = foo.bar + 3)

fun main() {
    val x = Foo(1, "hi")
    val y = listOf(
        ::withBarTimes2,
        ::withBarPlus3
    ).fold(x, { x, f -> f(x) })
    println(y) // Foo(bar=5, baz=hi)
}
```

This pattern can become quite useful if the collection of functions to apply is not yet known at compile-time, and is built dynamically.
