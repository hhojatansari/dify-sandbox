import asyncio
from typing import Any, List, Tuple, TypeAlias

import httpx
import numpy as np
import pandas as pd
from pydantic import BaseModel


class VLLMReranker(BaseModel):
    base_url: str
    name: str


ModelScores: TypeAlias = dict[str, List[Tuple[str, float]]]


class QueryScores(BaseModel):
    all_docs: dict[str, Any]
    embedding_scores: ModelScores
    reranking_scores: ModelScores


reranker_models = {
    "bge": VLLMReranker(
        base_url="http://mock-reranker.local",
        name="/models/BAAI_bge-reranker-v2-m3",
    ),
    "jina": VLLMReranker(
        base_url="http://mock-reranker.local",
        name="/models/jinaai_jina-reranker-m0",
    ),
}


def _mock_transport(request: httpx.Request) -> httpx.Response:
    payload = {}
    if request.content:
        payload = __import__("json").loads(request.content.decode("utf-8"))

    docs = payload.get("documents", [])
    query = payload.get("query", "")

    # Deterministic fake reranker scores.
    results = []
    for i, text in enumerate(docs):
        score = 1.0 / (1 + i) + (len(query) % 7) * 0.001
        results.append(
            {
                "index": i,
                "relevance_score": float(score),
                "document": {"text": text},
            }
        )

    return httpx.Response(200, json={"results": results})


async def get_rerank(query: str, documents: list[str], model: VLLMReranker | str):
    if type(model) is str:
        model = reranker_models[model]

    url = f"{model.base_url}/rerank"
    payload = {"model": f"{model.name}", "query": query, "documents": documents}

    transport = httpx.MockTransport(_mock_transport)
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(response.text)
        data = response.json()
        items = [
            (item["index"], item["relevance_score"], item["document"]["text"])
            for item in data["results"]
        ]
        return items


async def gather(coros):
    return await asyncio.gather(*coros)


def make_features(scores: QueryScores) -> list[dict]:
    embedding_models = ["bge", "snowflake"]
    reranking_models = ["jina", "bge"]

    query_doc_pairs_data = []
    for doc in scores.all_docs:
        features = {}
        for model in embedding_models:
            model_scores = scores.embedding_scores[model]
            lowest_score = model_scores[-1][1]
            top3_mean = np.mean([s for d, s in model_scores[:3]]).item()
            sim = next((s for d, s in model_scores if d == doc), lowest_score)
            features[f"emb_sim_{model}"] = sim
            features[f"emb_relative_{model}"] = sim / top3_mean

        for model in reranking_models:
            model_scores = scores.reranking_scores[model]
            rerank_model_top3_mean = np.mean([s for d, s in model_scores[:3]]).item()
            features[f"rerank_sim_{model}"] = next((s for d, s in model_scores if d == doc))
            features[f"rerank_relative_{model}"] = (
                features[f"rerank_sim_{model}"] / rerank_model_top3_mean
            )

        query_doc_pairs_data.append(features)

    return query_doc_pairs_data


w = np.array([-1.44120035, 1.89585005, 7.59292896, 1.39456976, 0.38541923, 2.61055952])
b = -13.5021328


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def predict_proba(X):
    z = X @ w + b
    return sigmoid(z)


def main(query_text: str, bge_results: list, snowflake_results: list):
    def get_segment_id(item):
        return f"{item['title']}-{item['metadata']['segment_position']}"

    bge_map = {get_segment_id(item): item for item in bge_results}
    snowflake_map = {get_segment_id(item): item for item in snowflake_results}
    all_docs = {**bge_map, **snowflake_map}

    bge_scores = [(get_segment_id(item), item["metadata"]["score"]) for item in bge_results]
    sf_scores = [(get_segment_id(item), item["metadata"]["score"]) for item in snowflake_results]

    doc_ids = list(all_docs.keys())
    doc_texts = [item["content"] for item in all_docs.values()]

    reranker_model_list = ["bge", "jina"]

    async def get_rerank2(query_text, doc_texts, m):
        scores = await get_rerank(query_text, doc_texts, m)
        return [(doc_ids[doc_idx], float(score)) for doc_idx, score, text in scores]

    coros = [get_rerank2(query_text, doc_texts, m) for m in reranker_model_list]
    _rerank_scores = asyncio.run(gather(coros))
    rerank_scores = {m: s for s, m in zip(_rerank_scores, reranker_models)}

    query_scores = QueryScores(
        all_docs=all_docs,
        embedding_scores={
            "bge": bge_scores,
            "snowflake": sf_scores,
        },
        reranking_scores=rerank_scores,
    )
    df = pd.DataFrame(make_features(query_scores))

    used_features = [
        "emb_sim_bge",
        "emb_relative_bge",
        "emb_relative_snowflake",
        "rerank_sim_jina",
        "rerank_sim_bge",
        "rerank_relative_bge",
    ]

    final_scores = predict_proba(df[used_features].to_numpy())
    topk_idxs = np.argsort(final_scores)[-20:][::-1]
    result = []
    for idx in topk_idxs:
        doc = all_docs[doc_ids[idx]]
        doc["metadata"]["score"] = round(float(final_scores[idx]), 6)
        result.append(doc)

    return {"result": result}


def build_mock_results(prefix: str, n: int) -> list[dict]:
    items = []
    for i in range(n):
        items.append(
            {
                "title": f"{prefix}-title-{i // 2}",
                "content": f"{prefix} content block {i}",
                "metadata": {
                    "segment_position": i,
                    "score": float(0.2 + (n - i) / (n * 10)),
                },
            }
        )
    return items


if __name__ == "__main__":
    query_text = "can I open account with returned cheque?"
    bge_results = build_mock_results("bge", 24)
    snowflake_results = build_mock_results("sf", 24)

    output = main(query_text, bge_results, snowflake_results)
    print(f"result_count={len(output['result'])}")
    print(f"top_score={output['result'][0]['metadata']['score']}")
