## Problem understanding and chosen interpretation

维护一个 trending topics 排行榜。输入是一串带时间戳的事件和查询，系统需要实时更新 topic 分数，并回答 top-K、rank、score 查询。
在 baseline 中，trending 被定义为“当前衰减后的 engagement score 最大”。分数越高，排名越靠前。为了避免旧事件的影响永久累积，系统引入时间衰减因子，使较早发生的事件影响逐渐降低。

## Baseline data structure design

Baseline 实现主要使用哈希表 `normalized_scores`、全局衰减因子 `global_factor` 和堆选择方法。

系统使用 Python 字典 `normalized_scores` 存储每个话题的归一化分数。字典的键是 `topic_id`，值是该话题的 normalized score。这样在处理更新事件和查询单个话题分数时，可以通过哈希表快速找到对应话题。

为了避免每次时间前进时遍历所有话题，我使用变量 `global_factor` 表示所有话题共同乘上的衰减因子。系统中的真实分数满足：

```text
real_score(topic) = normalized_scores[topic] * global_factor
```

当时间从 `current_time` 前进到 `t` 时，程序只更新：

```text
global_factor *= lambda_decay ** (t - current_time)
current_time = t
```

这样不用每次时间变化都遍历所有 topic，而是用 lazy decay 把所有 topic 共同的衰减合并到一个变量里。

对于更新事件，`POST`、`LIKE`、`COMMENT`、`SHARE` 的分数增量分别是 1、2、3、5。由于字典中保存的是 normalized score，而不是真实分数，所以新的事件增量 `increment` 需要转换成 `increment / global_factor` 后再加入字典。这样乘回 `global_factor` 后，真实分数正好增加 `increment`。

对于 `QUERY K`，程序使用 `heapq.nsmallest` 从所有 topic 中选出排名最高的 K 个。比较键是 `(-normalized_score, topic_id)`，其中 `-normalized_score` 保证分数高的 topic 排在前面，`topic_id` 保证同分时编号小的 topic 排在前面。因为所有 topic 的真实分数都乘以同一个正数 `global_factor`，所以按照 normalized score 排名和按照真实分数排名结果相同。

对于 `RANK topic_id`，当前实现使用简单遍历。程序遍历所有出现过的 topic，统计有多少 topic 的分数更高，或者在同分时有更小的 `topic_id`。如果目标 topic 从未出现过，则返回 `-1`。

设 `T` 是已经出现过的 topic 数量，`K` 是 `QUERY K` 中的 K。当前实现的复杂度如下：

| 操作 | 时间复杂度 | 原因 |
| --- | ---: | --- |
| `advance_time` | `O(1)` | 只更新 `global_factor` 和 `current_time` |
| `update` | 平均 `O(1)` | 字典查找和修改 topic 分数 |
| `score` | 平均 `O(1)` | 字典查找后乘以 `global_factor` |
| `query` | 约 `O(T log K)` | 扫描所有 topic，并用堆维护 top-K |
| `rank` | `O(T)` | 遍历所有 topic 计算排名 |
| 空间 | `O(T)` | 每个出现过的 topic 存一个 normalized score |

如果很多 topic 分数相同，系统会按照 `topic_id` 从小到大稳定排序。如果分数非常接近，由于使用浮点数，理论上可能有精度误差，但 baseline 实现直接使用 Python float 比较。

这个设计的优点是实现简单、正确性容易解释，并且 `update` 和 `score` 很快。缺点是 `query` 和 `rank` 都需要扫描所有 topic，因此在 topic 数量很大或者查询非常频繁时会比较慢。如果要进一步优化精确排名，可以考虑使用支持顺序统计的平衡二叉搜索树，但实现复杂度会明显提高。

## Correctness argument and invariants

这一节说明程序为什么是正确的，并指出代码中一直保持成立的关键不变量。对本题来说，需要写清楚三件事：时间衰减为什么正确，事件更新为什么正确，以及查询排名为什么可以直接比较 normalized score。最重要的不变量是 lazy decay 的分数表示方式：

```text
real_score(topic) = normalized_scores[topic] * global_factor
```

其中 `real_score(topic)` 是题目要求的真实衰减后分数，`normalized_scores[topic]` 是程序内部保存的归一化分数，`global_factor` 是所有 topic 共同乘上的全局衰减因子。

首先考虑时间前进。假设上一条操作的时间是 `current_time`，新操作的时间是 `t`，则时间差为：

```text
dt = t - current_time
```

题目要求所有 topic 的真实分数都乘上：

```text
lambda_decay ** dt
```

程序没有遍历所有 topic，而是只更新：

```text
global_factor *= lambda_decay ** dt
```

因为每个 topic 的真实分数都等于 `normalized_scores[topic] * global_factor`，所以当 `global_factor` 被乘上 `lambda_decay ** dt` 时，所有 topic 的真实分数也同时乘上了相同的衰减因子。因此，时间衰减的效果与逐个更新所有 topic 是一致的。

其次考虑事件更新。对于 `POST`、`LIKE`、`COMMENT`、`SHARE`，程序先根据事件类型得到分数增量 `increment`。由于内部保存的是 normalized score，而不是 real score，如果直接执行：

```text
normalized_scores[topic] += increment
```

那么真实分数只会增加：

```text
increment * global_factor
```

这不等于题目要求的 `increment`。因此程序实际增加的是：

```text
increment / global_factor
```

更新后该 topic 的真实分数增加量为：

```text
(increment / global_factor) * global_factor = increment
```

所以事件更新也保持了不变量。

对于 `SCORE topic_id` 查询，程序返回：

```text
normalized_scores.get(topic_id, 0.0) * global_factor
```

这正好是不变量中定义的真实分数。如果 topic 从未出现，字典中没有该 topic，程序把它的分数视为 0。

对于 `QUERY K` 和 `RANK topic_id`，程序直接比较 `normalized_scores`。这是正确的，因为所有 topic 的真实分数都乘以同一个正数 `global_factor`。当 `global_factor > 0` 时，两个 topic 的相对顺序不会改变：

```text
real_score_a > real_score_b
```

等价于：

```text
normalized_score_a > normalized_score_b
```

因此，按照 normalized score 排名和按照真实分数排名得到的结果相同。同分时，程序按照题目要求让较小的 `topic_id` 排在前面。

这个正确性论证依赖两个输入假设：第一，题目给出的时间戳是非递减的，因此 `dt >= 0`；第二，题目给出的衰减因子满足 `0.95 <= lambda_decay <= 0.9999`，所以在数学意义上 `global_factor` 始终为正数。在这些假设下，lazy decay 的 invariant 可以在初始化、时间推进、事件更新和查询过程中一直保持成立。

## Complexity analysis