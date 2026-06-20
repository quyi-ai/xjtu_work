import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from main import EVENT_SCORE_INCREMENTS, TrendingSystem


LAMBDA_DECAY = 0.99
RANDOM_SEED = 2026
DEFAULT_OPERATION_COUNT = 10000
DEFAULT_TOPIC_COUNT = 2500
DEFAULT_K = 10

UPDATE_EVENTS = tuple(EVENT_SCORE_INCREMENTS.keys())


@dataclass
class ExperimentResult:
    workload_name: str
    operation_count: int
    distinct_topics: int
    k: int
    update_count: int
    query_count: int
    total_time: float
    average_update_time: float
    average_query_time: float
    estimated_memory_kib: float


class SlowReferenceSystem:
    def __init__(self, lambda_decay):
        self.lambda_decay = lambda_decay
        self.current_time = 0
        self.scores = {}

    def advance_time(self, t):
        dt = t - self.current_time
        decay_factor = self.lambda_decay ** dt
        for topic_id in list(self.scores):
            self.scores[topic_id] *= decay_factor
        self.current_time = t

    def update(self, event_type, topic_id, t):
        self.advance_time(t)
        increment = EVENT_SCORE_INCREMENTS[event_type]
        self.scores[topic_id] = self.scores.get(topic_id, 0.0) + increment

    def query(self, k, t):
        self.advance_time(t)
        ranked_topics = sorted(self.scores.items(), key=lambda item: (-item[1], item[0]))
        return [topic_id for topic_id, _ in ranked_topics[:k]]

    def rank(self, topic_id, t):
        self.advance_time(t)
        if topic_id not in self.scores:
            return -1

        target_score = self.scores[topic_id]
        rank = 1
        for other_topic_id, score in self.scores.items():
            if score > target_score or (score == target_score and other_topic_id < topic_id):
                rank += 1
        return rank

    def score(self, topic_id, t):
        self.advance_time(t)
        return self.scores.get(topic_id, 0.0)


def random_update_operation(timestamp, topic_id):
    event_type = random.choice(UPDATE_EVENTS)
    return (timestamp, event_type, topic_id)


def count_distinct_topics(operations):
    topic_ids = set()
    for _, operation_name, value in operations:
        if operation_name in EVENT_SCORE_INCREMENTS:
            topic_ids.add(value)
    return len(topic_ids)


def estimate_score_table_memory_kib(system):
    total_bytes = sys.getsizeof(system.normalized_scores)
    for topic_id, normalized_score in system.normalized_scores.items():
        total_bytes += sys.getsizeof(topic_id)
        total_bytes += sys.getsizeof(normalized_score)
    return total_bytes / 1024


def generate_uniform_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    for timestamp in range(1, operation_count + 1):
        if random.random() < 0.8:
            topic_id = random.randint(1, topic_count)
            operations.append(random_update_operation(timestamp, topic_id))
        else:
            operations.append((timestamp, "QUERY", k))
    return operations


def generate_zipfian_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    topics = list(range(1, topic_count + 1))
    weights = [1.0 / (rank ** 1.1) for rank in topics]

    for timestamp in range(1, operation_count + 1):
        if random.random() < 0.8:
            topic_id = random.choices(topics, weights=weights, k=1)[0]
            operations.append(random_update_operation(timestamp, topic_id))
        else:
            operations.append((timestamp, "QUERY", k))
    return operations


def generate_update_heavy_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    for timestamp in range(1, operation_count + 1):
        if random.random() < 0.95:
            topic_id = random.randint(1, topic_count)
            operations.append(random_update_operation(timestamp, topic_id))
        else:
            operations.append((timestamp, "QUERY", k))
    return operations


def generate_query_heavy_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    warmup_topics = min(topic_count, operation_count // 4)

    for topic_id in range(1, warmup_topics + 1):
        operations.append((topic_id, "POST", topic_id))

    timestamp = warmup_topics
    while len(operations) < operation_count:
        timestamp += 1
        if random.random() < 0.75:
            operations.append((timestamp, "QUERY", k))
        else:
            topic_id = random.randint(1, topic_count)
            operations.append(random_update_operation(timestamp, topic_id))
    return operations


def generate_bursty_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    hot_topic_id = 1
    burst_start = operation_count // 2

    for timestamp in range(1, operation_count + 1):
        if timestamp >= burst_start and random.random() < 0.75:
            operations.append(random_update_operation(timestamp, hot_topic_id))
        elif random.random() < 0.8:
            topic_id = random.randint(1, topic_count)
            operations.append(random_update_operation(timestamp, topic_id))
        else:
            operations.append((timestamp, "QUERY", k))
    return operations


def generate_adversarial_tie_workload(
    operation_count=DEFAULT_OPERATION_COUNT,
    topic_count=DEFAULT_TOPIC_COUNT,
    k=DEFAULT_K,
):
    operations = []
    tie_topic_count = min(topic_count, operation_count // 2)

    for topic_id in range(1, tie_topic_count + 1):
        operations.append((1, "POST", topic_id))

    timestamp = 2
    while len(operations) < operation_count:
        if random.random() < 0.7:
            operations.append((timestamp, "QUERY", k))
        else:
            topic_id = random.randint(1, tie_topic_count)
            operations.append((timestamp, "LIKE", topic_id))
        timestamp += 1
    return operations


def generate_k_growth_workload(k, operation_count=5000, topic_count=DEFAULT_TOPIC_COUNT):
    operations = []
    warmup_topics = min(topic_count, operation_count // 2)

    for topic_id in range(1, warmup_topics + 1):
        operations.append((topic_id, "POST", topic_id))

    timestamp = warmup_topics
    while len(operations) < operation_count:
        timestamp += 1
        operations.append((timestamp, "QUERY", k))
    return operations


def run_operations(operations, k, workload_name):
    system = TrendingSystem(LAMBDA_DECAY)
    update_count = 0
    query_count = 0
    update_time = 0.0
    query_time = 0.0

    total_start = time.perf_counter()

    for timestamp, operation_name, value in operations:
        if operation_name in EVENT_SCORE_INCREMENTS:
            start = time.perf_counter()
            system.update(operation_name, value, timestamp)
            update_time += time.perf_counter() - start
            update_count += 1
        elif operation_name == "QUERY":
            start = time.perf_counter()
            system.query(value, timestamp)
            query_time += time.perf_counter() - start
            query_count += 1

    total_time = time.perf_counter() - total_start

    return ExperimentResult(
        workload_name=workload_name,
        operation_count=len(operations),
        distinct_topics=count_distinct_topics(operations),
        k=k,
        update_count=update_count,
        query_count=query_count,
        total_time=total_time,
        average_update_time=update_time / update_count if update_count else 0.0,
        average_query_time=query_time / query_count if query_count else 0.0,
        estimated_memory_kib=estimate_score_table_memory_kib(system),
    )


def collect_outputs(system, operations):
    outputs = []
    for timestamp, operation_name, value in operations:
        if operation_name in EVENT_SCORE_INCREMENTS:
            system.update(operation_name, value, timestamp)
        elif operation_name == "QUERY":
            outputs.append(("QUERY", tuple(system.query(value, timestamp))))
        elif operation_name == "RANK":
            outputs.append(("RANK", system.rank(value, timestamp)))
        elif operation_name == "SCORE":
            outputs.append(("SCORE", round(system.score(value, timestamp), 3)))
    return outputs


def run_correctness_check():
    operations = [
        (1, "POST", 1),
        (2, "LIKE", 1),
        (3, "SHARE", 2),
        (4, "QUERY", 2),
        (5, "COMMENT", 1),
        (6, "LIKE", 2),
        (7, "RANK", 1),
        (8, "POST", 3),
        (9, "QUERY", 3),
        (9, "SCORE", 1),
        (10, "RANK", 99),
    ]

    fast_outputs = collect_outputs(TrendingSystem(LAMBDA_DECAY), operations)
    slow_outputs = collect_outputs(SlowReferenceSystem(LAMBDA_DECAY), operations)
    return fast_outputs == slow_outputs, fast_outputs, slow_outputs


def format_seconds(value):
    return f"{value:.6f}"


def build_markdown_report(results, k_growth_results, correctness_ok, fast_outputs, slow_outputs):
    lines = [
        "# Experiment Results",
        "",
        f"- Random seed: `{RANDOM_SEED}`",
        f"- Lambda decay: `{LAMBDA_DECAY}`",
        f"- Default operation count: `{DEFAULT_OPERATION_COUNT}`",
        f"- Default topic count: `{DEFAULT_TOPIC_COUNT}`",
        "",
        "## Correctness Check",
        "",
        "The fast lazy-decay implementation was compared with a slow reference implementation on a small mixed workload.",
        "",
        f"- Result: `{'PASS' if correctness_ok else 'FAIL'}`",
        f"- Fast outputs: `{fast_outputs}`",
        f"- Slow outputs: `{slow_outputs}`",
        "",
        "## Workload Performance",
        "",
        "| Workload | Operations | Distinct topics | K | Updates | QUERY ops | Total time (s) | Avg update (us) | Avg QUERY (us) | Estimated score-table memory (KiB) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for result in results:
        lines.append(
            "| "
            f"{result.workload_name} | "
            f"{result.operation_count} | "
            f"{result.distinct_topics} | "
            f"{result.k} | "
            f"{result.update_count} | "
            f"{result.query_count} | "
            f"{format_seconds(result.total_time)} | "
            f"{result.average_update_time * 1_000_000:.3f} | "
            f"{result.average_query_time * 1_000_000:.3f} | "
            f"{result.estimated_memory_kib:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Effect of K",
            "",
            "| K | Operations | Distinct topics | QUERY ops | Total time (s) | Avg QUERY (us) |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for result in k_growth_results:
        lines.append(
            "| "
            f"{result.k} | "
            f"{result.operation_count} | "
            f"{result.distinct_topics} | "
            f"{result.query_count} | "
            f"{format_seconds(result.total_time)} | "
            f"{result.average_query_time * 1_000_000:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Query-heavy workloads are expected to be slower because each `QUERY K` scans all active topics.",
            "- Update-heavy workloads are expected to be faster because each update modifies only one dictionary entry.",
            "- Uniform workloads usually create more distinct topics than Zipfian workloads, increasing the cost of `QUERY` and `RANK`.",
            "- Larger `K` usually increases query cost because top-K selection maintains a larger heap.",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    random.seed(RANDOM_SEED)

    workload_builders = [
        ("uniform", generate_uniform_workload),
        ("zipfian", generate_zipfian_workload),
        ("update-heavy", generate_update_heavy_workload),
        ("query-heavy", generate_query_heavy_workload),
        ("bursty", generate_bursty_workload),
        ("adversarial-tie", generate_adversarial_tie_workload),
    ]

    results = []
    for workload_name, build_workload in workload_builders:
        operations = build_workload(k=DEFAULT_K)
        results.append(run_operations(operations, DEFAULT_K, workload_name))

    k_growth_results = []
    for k in (10, 100, 1000):
        operations = generate_k_growth_workload(k)
        k_growth_results.append(run_operations(operations, k, f"k-growth-{k}"))

    correctness_ok, fast_outputs, slow_outputs = run_correctness_check()

    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "experiment_results.md"
    output_path.write_text(
        build_markdown_report(results, k_growth_results, correctness_ok, fast_outputs, slow_outputs),
        encoding="utf-8",
    )

    print(f"Wrote experiment results to {output_path}")


if __name__ == "__main__":
    main()
