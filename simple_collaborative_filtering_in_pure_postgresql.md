# Simple collaborative filtering in pure PostgreSQL

Many apps/websites must decide which items to show their users to maximize engagement. Examples include:

- streaming (e.g. Netflix)
- e-commerce (e.g. Amazon)
- jobs boards (e.g. Indeed)
- dating (e.g. Tinder) (Let's temporarily ignore that labeling human beings as "items" is not poetic/romantic/nice/accurate.)

The main approaches to obtain these recommendations are:

- **content-based filtering**: Based on the features of each user and each item, we make predictions about which items the user might like, and recommend them.
- **collaborative filtering**:
  - **user-user**: Find similar users and recommend items they liked.
  - **item-item**: Find items similar to the ones already liked by the user and recommend them.

(For the pros and cons of each approach, just ask your favorite ~[bullshit machine](https://thebullshitmachines.com/)~ ~LLM~ AI.)

This article demonstrates user-user collaborative filtering (with support for negative engagement signals) using only PostgreSQL.

(An item-item approach can be implemented similarly.)

## Data model

The sum of all user-item interactions gives a signal. Any interval could be chosen (e.g., 1 to 5 stars). In our case, we use:

- `-1.0`: most negative (If you don't intend to provide negative signals, e.g. "dislikes", `0.0` works fine too.)
- ` 1.0`: most positive

```sql
CREATE TABLE signals (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    signal REAL NULL CHECK (signal >= -1.0 AND signal <= 1.0),
    UNIQUE (user_id, item_id)
);
CREATE INDEX signals_user_id_index ON signals (user_id) INCLUDE (item_id, signal);
CREATE INDEX signals_item_id_index ON signals (item_id) INCLUDE (user_id, signal);
CREATE INDEX signals_user_id_item_id_index ON signals (user_id, item_id) INCLUDE (signal);
```

The application would continuously insert rows into the table or [update existing signals](https://gist.github.com/Dobiasd/e12fbbb702e7da4c7677f65716fa2a27) on repeated interactions.

## Example data

Let's insert some minimal test data for experimentation:

```sql
INSERT INTO signals (user_id, item_id, signal) VALUES
(10, 20,  0.9),
(10, 21, -0.4),
(10, 22,  0.7),
(10, 23, -0.5),
(15, 20,  0.8),
(15, 21, -0.3)
;
```

So our user-item-interaction matrix looks like this:

| user/item | 20  | 21   | 22  | 23   |
| --------- | --- | ---- | --- | ---- |
| 10        | 0.9 | -0.4 | 0.7 | -0.5 |
| 15        | 0.8 | -0.3 |     |

Meaning:

- User `10` likes items `20` and `22`, but dislikes items `21` and `23`.
- User `11` also likes item `20` and dislikes item `21`.

So, users `10` and `11` seem to have a similar taste, and we would thus expect user `11` to also like item `22`, but not `23`.

## Calculating user similarity

To get to this prediction, we first need to calculate how similar these two users are. Since we will later have more users, let's calculate the similarity for all possible user pairs:

```sql
CREATE VIEW user_similarities AS (
  WITH pairs AS (
    SELECT
      a.user_id user_id_a,
      b.user_id user_id_b,
      COUNT(1) overlap,
      AVG(1.0 - ABS(a.signal - b.signal)) agreement
    FROM signals a JOIN signals b ON a.item_id = b.item_id
    WHERE a.user_id != b.user_id
    GROUP BY a.user_id, b.user_id
  )
  SELECT *, overlap * agreement user_similarity -- in PROD, only user_similarity is needed
  FROM pairs
);
```

In the above:

- `overlap` counts the number of items, both users in a pair already have interacted with.
- `agreement` is the Manhattan distance of the two interaction vectors, normalized to `[-1.0, 1.0]`. (Other similarity metrics would also be possible, e.g., euclidean distance or cosine similarity.)
- `user_similarity` is `agreement` weighted by `overlap`.

This gives a matrix of size `u × u` with `u` being the number of users. Example (not from the `INSERT` above):

| user | 1    | 2   | 3    |
| ---- | ---- | --- | ---- |
| 1    | 1.0  |     | -0.2 |
| 2    |      | 1.0 | 0.6  |
| 3    | -0.2 | 0.6 | 1.0  |

The diagonal of this matrix is not interesting, because it's just the fact, that a user is 100% similar to themselves.

Also, the matrix is symmetric (because our user similarity metric is commutative), so only one half (top-right triangle) is needed. But later queries will become simpler by not getting rid of the second half, so we keep it.

For bigger datasets, this matrix is likely very sparse, i.e., many user pairs have no overlap, and thus no similarity between them can be calculated.

Negative user similarities can only occur when you use negative signals (`signals.signal < 0.0`). They mean, that this other user has opposite preferences.

## Generating recommendations

Having this user-user-similarity matrix, we can derive our recommendations:

```sql
CREATE VIEW user_recommendations AS (
  WITH candidates AS (
    SELECT DISTINCT a.user_id, b.item_id FROM signals a CROSS JOIN signals b
  )
  SELECT
    candidates.user_id,
    candidates.item_id,
    AVG(user_similarity * s.signal) score
  FROM candidates
  JOIN user_similarities o ON o.user_id_a = candidates.user_id
  JOIN signals s ON s.user_id = o.user_id_b AND s.item_id = candidates.item_id
  LEFT JOIN signals known ON (candidates.user_id = known.user_id AND candidates.item_id = known.item_id)
  WHERE known.item_id IS NULL
  GROUP BY candidates.item_id, candidates.user_id
);
```

In the above:

- `candidates` is the cartesian product, giving all potential user-item pairs.
- We join with `user_similarities` to get all users with a known similarity.
- We join with `signals` to collect the signals from these other users.
- `signals` as `known` is only used to remove items the user already interacted with (`WHERE known.item_id IS NULL`). It's a "`LEFT ANTI JOIN`".

## Example recommendations

Let's look into it:

```sql
SELECT * FROM user_recommendations;
```

```
 user_id | item_id |        score
---------+---------+---------------------
      15 |      22 |  1.2600000077486033
      15 |      23 | -0.9000000208616257
```

Indeed, it gives the prediction we were hoping for. :D

And that's already it!

## Load test

Let's put some load on it:

```sql
TRUNCATE signals;
```

```sql
INSERT INTO signals (user_id, item_id, signal)
SELECT
 (random() * 100000)::integer,
 (random() * 1000)::integer,
 random() * 2.0 - 1.0
FROM generate_series(1, 1100000)
ON CONFLICT (user_id, item_id) DO NOTHING; -- to skip duplicates
```

We now have:

- 100k users
- 1k items
- over 1M interactions

So let's fetch the recommendations for a user:

```sql
SELECT * FROM user_recommendations WHERE user_id = 42 ORDER BY score DESC LIMIT 10;
```

```
 user_id | item_id |        score
---------+---------+---------------------
      42 |     438 | 0.09187011460708962
      42 |     680 | 0.08926545207792841
      42 |     897 | 0.08884137042722827
      42 |     302 | 0.08332909557853353
      42 |     906 | 0.08295293443873514
      42 |     276 | 0.08270721418927421
      42 |     340 | 0.08173571305819198
      42 |       9 | 0.08054026719749253
      42 |     299 | 0.08029276479669858
      42 |     317 | 0.07946202537955073
```

On my machine (with a default Postgres running in Docker), queries like this take (after some warmup of the Postgres engine) ~170 ms, which is not bad because we applied almost zero optimizations so far.

## Potential optimizations

In case it's too slow (or becomes too slow with more data), potential optimizations include:

- Regularly materializing `user_similarities` (and maybe even `recommendations`) periodically
- Limiting the number of pairs considered per user when generating `user_similarities`
- Switch from the user-user approach to the item-item approach if this results in a smaller similarity table
- Shard your data by certain properties of users/items, e.g., the user's country
- Apply standard database tuning techniques
- Use a fancier technology. PostgreSQL is great because of its simplicity and ubiquity, but at some scale, it might struggle. Other approaches could also enable techniques like decomposing the user-item matrix into the product of two smaller matrices to speed up downstream computations.

## Further enhancements

In a mature real-life application, you might want to experiment with some additional ideas:

- Include user demographics to calculate user similarities even for users without interactions to overcome their cold-start problem
- Augmenting the results with the previously mentioned item-item approach (and include item features to overcome item-cold-start problems)
- Calculate similarities transitively to a certain depth (currently it's only `1`)

## Closing words

I hope you enjoyed reading this article as much as I did writing it. If you gather additional insights while using this approach, I'd be happy to hear from you.
