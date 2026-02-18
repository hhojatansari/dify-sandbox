import json


def power_mean(x, y, p=2):
    """
    Generalized mean with parameter controlling bias toward maximum.
    """
    return (x**p + y**p) / (x ** (p - 1) + y ** (p - 1))


def get_segment_id(item):
    return f"{item['title']}-{item['metadata']['segment_position']}"


def main(retrival_result1, retrival_result2):
    map1 = {get_segment_id(item): item for item in retrival_result1}
    map2 = {get_segment_id(item): item for item in retrival_result2}

    all_doc_ids = set(map1) | set(map2)

    fallback_score_1 = retrival_result1[-1]["metadata"]["score"] if retrival_result1 else 0
    fallback_score_2 = retrival_result2[-1]["metadata"]["score"] if retrival_result2 else 0

    combined_results = []
    for doc_id in all_doc_ids:
        item1 = map1.get(doc_id)
        item2 = map2.get(doc_id)

        score1 = item1["metadata"]["score"] if item1 else fallback_score_1
        score2 = item2["metadata"]["score"] if item2 else fallback_score_2

        base_item = item1 or item2
        result_item = base_item.copy()
        result_item["metadata"] = dict(base_item["metadata"])
        result_item["metadata"]["score"] = power_mean(score1, score2)

        combined_results.append(result_item)

    combined_results.sort(key=lambda x: x["metadata"]["score"], reverse=True)
    return {"top4_retrival": combined_results[:5]}


def _mock_list(prefix, n, start_score):
    rows = []
    for i in range(n):
        rows.append(
            {
                "title": f"{prefix}-title-{i // 2}",
                "content": f"{prefix} content {i}",
                "metadata": {
                    "segment_position": i,
                    "score": round(start_score - i * 0.01, 6),
                },
            }
        )
    return rows


if __name__ == "__main__":
    # Overlap a few IDs intentionally, keep others unique.
    retrival_result1 = _mock_list("A", 7, 0.95)
    retrival_result2 = _mock_list("A", 3, 0.92) + _mock_list("B", 5, 0.89)

    out = main(retrival_result1, retrival_result2)
    print(
        json.dumps(
            {
                "result_count": len(out["top4_retrival"]),
                "top_score": out["top4_retrival"][0]["metadata"]["score"],
                "top_ids": [get_segment_id(x) for x in out["top4_retrival"]],
            }
        )
    )
