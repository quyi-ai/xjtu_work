# Homework Y: Trending Topic System

本项目实现数据结构作业 Homework Y 的 baseline trending topic system。

系统支持：

- `POST / LIKE / COMMENT / SHARE` 事件更新
- 时间衰减
- `QUERY K` 查询当前 top-K topics
- `RANK topic_id` 查询话题排名
- `SCORE topic_id` 查询当前分数
- 同分时 `topic_id` 小的排在前面

事件分值：

| Event | Increment |
| --- | ---: |
| `POST` | 1 |
| `LIKE` | 2 |
| `COMMENT` | 3 |
| `SHARE` | 5 |

## 文件结构

```text
hwy/
├── main.py
├── experiment.py
├── report.md
├── tests/
└── outputs/
```

## 输入格式

第一行是衰减因子 `lambda`。
第二行是操作数量 `M`。
接下来 `M` 行是带时间戳的操作。

```text
lambda
M
t POST topic_id
t LIKE topic_id
t COMMENT topic_id
t SHARE topic_id
t QUERY K
t RANK topic_id
t SCORE topic_id
```

时间戳 `t` 是非递减整数。

## 运行主程序

在项目根目录运行：

```bash
python3 hwy/main.py
```

或者使用输入文件运行：

```bash
python3 hwy/main.py < hwy/tests/tiny.in
```

## 运行测试

测试文件位于 `hwy/tests/`，每个测试包含一个 `.in` 输入文件和一个 `.out` 期望输出文件。

运行单个测试：

```bash
python3 hwy/main.py < hwy/tests/tiny.in > /tmp/tiny.actual
diff -u hwy/tests/tiny.out /tmp/tiny.actual
```

如果 `diff` 没有输出，说明测试通过。

运行全部测试：

```bash
for test_file in hwy/tests/*.in; do
  output_file="${test_file%.in}.out"
  actual_file="/tmp/$(basename "${test_file%.in}").actual"
  python3 hwy/main.py < "$test_file" > "$actual_file"
  diff -u "$output_file" "$actual_file" && echo "$test_file OK"
done
```

## 示例

输入：

```text
0.99
10
1 POST 1
2 LIKE 1
3 SHARE 2
4 QUERY 2
5 COMMENT 1
6 LIKE 2
7 RANK 1
8 POST 3
9 QUERY 3
9 SCORE 1
```

输出：

```text
2 1
2
2 1 3
5.669
```
