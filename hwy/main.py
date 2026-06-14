import sys
from heapq import nsmallest


UPDATE_EVENT_TYPES = {"POST", "LIKE", "COMMENT", "SHARE"}
EVENT_SCORE_INCREMENTS = {"POST": 1, "LIKE": 2, "COMMENT": 3, "SHARE": 5}


class TrendingSystem:
    def __init__(self, lambda_decay):
        self.lambda_decay = lambda_decay
        self.current_time = 0
        self.global_factor = 1.0
        self.normalized_scores = {}

    def advance_time(self, t):
        dt = t - self.current_time
        self.global_factor *= self.lambda_decay ** dt
        self.current_time = t

    def update(self, event_type, topic_id, t):
        self.advance_time(t)
        increment = EVENT_SCORE_INCREMENTS[event_type]
        old_score = self.normalized_scores.get(topic_id, 0.0)
        self.normalized_scores[topic_id] = old_score + increment / self.global_factor

    def query(self, k, t):
        self.advance_time(t)
        return [
            topic_id
            for topic_id, _ in nsmallest(
                k,
                self.normalized_scores.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]

    def rank(self, topic_id, t):#复杂度为O(n)
        self.advance_time(t)
        target_score = self.normalized_scores.get(topic_id)
        if target_score is None:
            return -1

        rank = 1
        for other_topic_id, score in self.normalized_scores.items():
            if score > target_score or (score == target_score and other_topic_id < topic_id):
                rank += 1
        return rank

    def score(self, topic_id, t):
        self.advance_time(t)
        return self.normalized_scores.get(topic_id, 0.0) * self.global_factor


def main():
    lambda_line = sys.stdin.readline().strip()

    lambda_decay = float(lambda_line)
    operation_count = int(sys.stdin.readline().strip())
    trending_system = TrendingSystem(lambda_decay)

    for _ in range(operation_count):
        line = sys.stdin.readline().strip()
        if not line:
            continue

        parts = line.split()
        timestamp = int(parts[0])
        operation_name = parts[1]

        if operation_name in UPDATE_EVENT_TYPES:
            topic_id = int(parts[2])
            trending_system.update(operation_name, topic_id, timestamp)
        elif operation_name == "QUERY":
            k = int(parts[2])
            result = trending_system.query(k, timestamp)
            print(" ".join(str(topic_id) for topic_id in result))
        elif operation_name == "RANK":
            topic_id = int(parts[2])
            result = trending_system.rank(topic_id, timestamp)
            print(result)
        elif operation_name == "SCORE":
            topic_id = int(parts[2])
            result = trending_system.score(topic_id, timestamp)
            print(f"{result:.3f}")
        else:
            pass


if __name__ == "__main__":
    main()
