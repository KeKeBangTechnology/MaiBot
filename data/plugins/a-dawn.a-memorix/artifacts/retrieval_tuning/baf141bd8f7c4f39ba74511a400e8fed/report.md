# 检索调优报告（baf141bd8f7c4f39ba74511a400e8fed）

## 1. 任务信息
- 状态: completed
- 目标函数: precision_priority
- 强度: standard
- 轮次: baseline + 20
- 创建时间: 2026-05-23 18:04:35
- 开始时间: 2026-05-23 18:04:35
- 完成时间: 2026-05-23 18:30:03

## 2. 基线 vs 最优
- baseline score: 0.579628
- best score: 0.698378
- P@1: 0.3056 -> 0.8056 (Δ +0.5000)
- P@3: 0.8056 -> 0.8750 (Δ +0.0694)
- MRR: 0.5324 -> 0.8426 (Δ +0.3102)
- Recall@K: 0.8472 -> 0.8889 (Δ +0.0417)
- SPO relation hit: 0.9167 -> 0.9167 (Δ +0.0000)
- 空结果率: 0.0139 -> 0.0000 (Δ -0.0139)
- 超时数: 1 -> 0 (Δ -1)
- 平均耗时(ms): 290.10 -> 308.05 (Δ +17.95)

## 3. 最优参数
```json
{
  "retrieval": {
    "top_k_paragraphs": 15,
    "top_k_relations": 10,
    "top_k_final": 15,
    "alpha": 0.7,
    "enable_ppr": false,
    "search": {
      "smart_fallback": {
        "enabled": false
      }
    },
    "sparse": {
      "enabled": true,
      "mode": "auto",
      "candidate_k": 70,
      "relation_candidate_k": 50
    },
    "fusion": {
      "method": "weighted_rrf",
      "rrf_k": 70,
      "vector_weight": 0.8,
      "bm25_weight": 0.2
    }
  },
  "threshold": {
    "percentile": 70.0,
    "min_results": 4
  }
}
```

## 4. 测试集规模
- {"anchors": 24, "case_total": 96, "category_counts": {"spo_relation": 24, "spo_search": 24, "query_kw": 24, "query_nl": 24}, "seed": 554138, "sample_size": 24, "sampling": {"strategy": "predicate_round_robin_entity_diversity", "sample_size": 24, "total_triples": 51, "predicate_total": 43, "predicate_sampled": 24}, "llm_nl_enabled": true, "llm_nl_generated": 24}

## 5. 说明
- 本报告仅对当前已存储图谱与向量状态有效。
- 参数应用策略：运行时生效，不自动写入 config.toml。
