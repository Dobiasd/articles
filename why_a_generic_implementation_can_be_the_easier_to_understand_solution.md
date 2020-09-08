# Why a generic implementation can be the easier-to-understand solution

Following YAGNI, one might avoid implementing a generic version of some algorithm if it is only needed in one place and for one specific type.

In this article, I'll argue that a generic implementation might be easier to understand when maintaining code, and thus should be preferred, if feasible. (I'll use Java in the code examples, but the concept applies to other languages, like C++, Swift, (type-annotated) Python, Kotlin, or C#, too.)

Imagine you're working on the order system of a pizza delivery, which has a hierarchy like this:

```java
interface Customer {
    long getId();
    String getName();
    // ...
}

interface SpecialCustomer extends Customer {
    boolean checkIfIsBirthday(LocalDate today);
    // Some other special things here.
}
```

You're tasked with implementing a feature that prints all special customers, and you implement something like the following:

```java
static void printSpecialCustomers(List<SpecialCustomer> specialCustomers) {
    specialCustomers.forEach((customer) -> {
        System.out.println(String.format("%s: %s", customer.getId(), customer.getName()));
    });
}
```

```java
printSpecialCustomers(ourSpecialCustomers);
```

Since only methods of `Customer` are used, a future maintainer might wonder, why the function takes `List<SpecialCustomer>` and not `List<Customer>`. Since `SpecialCustomer` is a more complex type compared to `Customer`, using it exposes more (but unneeded) possibilities to the function. The maintainer might spend time trying to find out why this was done, just to conclude that is was not needed. The following implementation would have avoided this confusion.

```java
static void printCustomers(List<Customer> customers) {
    customers.forEach((customer) -> {
        System.out.println(String.format("%s: %s", customer.getId(), customer.getName()));
    });
}
```

So even though the function is never used for `Customer`s, which are not `SpecialCustomer`s, it is the better solution, because the parameter type is more restrictive in what possible things the function could do. But it is not just helpful when maintaining the function implementation, but also when just using is, because having `Customer` instead of `SpecialCustomer` already tell the client-code developer about all the things, this function is guaranteed to not be able to do, which is all the particular `SpecialCustomer` things. Thus using `Customer` instead of `SpecialCustomer` has made things simpler.

And we don't need to stop here with this line of reasoning. Let's imagine the typical pizza-delivery-business logic of having a non-reliable order queue shall be implemented. Maybe it swaps order from time to time or even randomly drops an order now and then.

```java
interface Order {
    Customer getCustomer();
    List<OrderLine> getOrderLines();
}
```

```java
class ShittyOrderQueue {
    private List<Order> orders;

    public void add(Order order) {
        // todo: Sometimes just don't add the order.
    }

    public Optional<Order> poll() {
        // todo: Sometimes return not from the front of the queue.
    }
}
```

People using a class that implements this interface, or reading its implementation, might wonder why it is constrained to work with `Order`s. "Wouldn't it also work with arbitrary other Objects? And if so, why isn't it implemented that way? There must be a reason for it, and I should find out to avoid doing something unintended."

So it is much better to implement the queue it in a generic way, even though it will actually be used for `Order`s exclusively.

```java
class ShittyQueue<T> {
    private List<T> items;

    public void add(T item) {
        // todo: Sometimes just don't add the item.
    }

    public Optional<T> poll() {
        // todo: Sometimes return not from the front of the queue.
    }
}
```

(Using a generic type is just like using a maximally general interface.)

Basically, with a bit of squinting, we can look at the version specific to `Order` (`ShittyOrderQueue`) as if it was a generic implementation, just with a very strong constraint.

```java
class ShittyOrderQueue<T extends Order> {
    // ...
}
```

This way makes the issue obvious since you would not use other non-needed constraints, like

```java
class ShittyQueue<T extends Comparable> {
    // ...
}
```

either, because your fellow developers (including future you) would unnecessarily try to understand why `T` needs to implement the `Comparable` interface. (In languages like Scala or Rust, one would have traits here instead, but the concept is the same.)

- constrained type -> unconstrained possibilities -> more cognitive load
- uncontrained type -> constrained possibilities -> less cognitive load

In conclusion, generics, as abstraction in general, can reduce complexity. They can be helpful even if the implemented class/function is never going to be used with more than one type, because being less concrete with the types allows the code to concretely express what it does not do, resulting in decreased cognitive load.
