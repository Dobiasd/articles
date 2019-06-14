# Do A/B tests - because correlation does not imply causation

Let's imagine we (hypothetical) collect habits and health data from people. We find that, on average, people who regularly go to the sauna had less sick days last year.

```text
(totally hypothetical data)

           | number of people | avg sick days / person |
|----------|------------------|------------------------|
| sauna    |             1000 |                      5 |
| no-sauna |            90000 |                     10 |
```

We now might want to conclude that regularly having a sauna prevents one from getting sick, and we start to recommend doing this. But this would be a big mistake!

We don't know at all if the sauna is the cause for being less sick. Some other factor could be making people use the sauna and be less sick.

```text
                 |====> sauna
other_factor ====|
                 |====> being less sick
```


This other factor could be (for example) [socioeconomic status](https://en.wikipedia.org/wiki/Socioeconomic_status#Health), which simply means: Wealthy people are less sick in general, and poor people just don't go to the sauna that much.

The only productive thing we can do with this sauna-less-sick correlation that we found, is to conduct an experiment, i.e., an A/B test. We need to randomly assign (a bunch of) people into two test groups. One group will be compelled to regularly go to the sauna and the other group is forbidden to do so. It's important, that people are not allowed to choose their group. We then let them do their assigned task for some time (quite long in that case), and then we count sick days again. Possible result:

```text
from hypothetical A/B test

           | number of people | avg sick days / person |
|----------|------------------|------------------------|
| sauna    |               50 |                      8 |
| no-sauna |               50 |                      7 |
```

Oh, so sauna does not cause less sick days at all. On the contrary, the sauna-test group had one sick day more per year on average compared to the no-sauna group. Sauna might even cause a bit more sickness. (Remember, this is just a contrived example, and is not related to any real numbers evaluating the effect of sauna.)

When doing such an experiment (A/B test) we are not allowed to separate the two groups in time or space, meaning:

- Both groups have to be measured simultaneously. If we test the sauna-sick days in one year, and the no-sauna-test-sick days the next year, other non-related factors, will have changed.
- The groups may not be separated in space, i.e., move one group to Finland, but not the other one. The individuals have to stay locally mixed as they were before the random assignment.
If we don't adhere to one of these rules, we will measure effects that are caused by some external factors instead of the suggested cause we want to measure (sauna).

---

So when we find a positive correlation between two things `X` and `Y`.

```text
X <----> Y
```

It can mean one causes the other:

```text
X ====> Y
```

or

```text
X <==== Y
```

But it does not have to. Other factors might always be involved:

```text
      |====> X
Z ====|
      |====> Y
```

And we can only find the true causation with randomized controlled trials (A/B tests).

---

Examples showing the absurdity:

1) Countries with more ice-cream consumption (`X`) have more deaths by drowning (`Y`). But eating ice cream does not make you drown. It's just that in colder countries, people eat less ice cream and don't go swimming that much. Because it's cold, duh.

2) `X` might be "Kids watching more TV", and `Y` "Kids being more violent". Watching TV could cause violence or peacefulness. We don't know. Maybe violent kids just tend to watch more TV.

3) "stork population" by region strongly correlates with "human birthrate" by region. However, storks don't deliver babies. People in rural areas (storks don't live in big cities) just have more kids.

In the media, one can find an enormous number of instances of this exact causal fallacy.

---

An example related to web/app development:

Let's say we are developing a mobile (freemium) game, we might find a positive correlation between "actually playing the tutorial level instead of skipping it" and "buying the full version".

Playing the tutorial level *might* cause more purchases, but we can not possibly know this from those statistics. It might be the case that people who are the "buying type of person" for some reason just also (on average) skip tutorials less often.

```text
                 |====> using the tutorial
other_factor ====|
                 |====> purchasing
```

So to really find out if we can make more of our users buy the full version by making playing the tutorial level mandatory, we need to conduct an A/B test with users randomly assigned into two groups. One gets the usual version of the app (default group), the other one gets the force-tutorial version (feature group). After collecting enough data by letting the test run long enough, we can make an informed decision on if we want to fully roll out the feature.
