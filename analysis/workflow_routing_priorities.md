# Workflow Routing Priorities

## Baseline metrics

- workflow_path_precision: 0.8496
- legal_path_precision: 0.7548
- workflow_recall_on_workflow_questions: 0.48
- legal_leakage_into_workflow: 0.1333
- workflow_leakage_into_legal: 0.24

## Top recommended fixes

| Rank | Failure group | Topic | Fix type | Count | Total freq | Suggested fix |
|---|---|---|---|---:|---:|---|
| 1 | legal_should_have_stayed_legal_but_went_workflow | accounting_operational / księgowanie / KPiR / okresy | routing keyword issue | 3 | 41 | Boost accounting-operational routing for księgowanie/KPiR/date-of-entry phrases and allow workflow-first on strong bookkeeping verbs. |
| 2 | legal_should_have_stayed_legal_but_went_workflow | accounting_operational / księgowanie / KPiR / okresy | workflow confidence too low | 3 | 23 | Boost accounting-operational routing for księgowanie/KPiR/date-of-entry phrases and allow workflow-first on strong bookkeeping verbs. |
| 3 | legal_should_have_stayed_legal_but_went_workflow | pełnomocnictwa / podpis / kanały złożenia | workflow confidence too low | 3 | 18 | Route form/submission/signature questions to workflow only when they ask how to submit/sign, not when they ask whether something is legally allowed. |
| 4 | legal_should_have_stayed_legal_but_went_workflow | KSeF permissions / authorization / invoice circulation | workflow confidence too low | 1 | 15 | Require stronger operational verbs for KSeF workflow-first, but explicitly allow uprawnienia/token flows when the query asks how to perform the action. |
| 5 | workflow_should_have_hit_but_went_legal | other / mixed routing | workflow confidence too low | 2 | 7 | Increase confidence weighting for title/example overlaps on operational queries and penalize shallow collisions. |
| 6 | workflow_should_have_hit_but_went_legal | JPK tags / procedural-vs-legal ambiguity | clarification gate masking workflow hit | 2 | 4 | Keep legal-first for JPK tag/RO/BFK/DI obligation questions unless the query explicitly asks how to configure or submit them in a system. |
| 7 | workflow_should_have_hit_but_went_legal | KSeF permissions / authorization / invoice circulation | workflow eligibility issue | 1 | 4 | Require stronger operational verbs for KSeF workflow-first, but explicitly allow uprawnienia/token flows when the query asks how to perform the action. |
| 8 | workflow_should_have_hit_but_went_legal | accounting_operational / księgowanie / KPiR / okresy | workflow eligibility issue | 1 | 4 | Boost accounting-operational routing for księgowanie/KPiR/date-of-entry phrases and allow workflow-first on strong bookkeeping verbs. |
| 9 | workflow_should_have_hit_but_went_legal | JPK tags / procedural-vs-legal ambiguity | workflow eligibility issue | 1 | 3 | Keep legal-first for JPK tag/RO/BFK/DI obligation questions unless the query explicitly asks how to configure or submit them in a system. |
| 10 | workflow_should_have_hit_but_went_legal | KSeF permissions / authorization / invoice circulation | workflow confidence too low | 1 | 3 | Require stronger operational verbs for KSeF workflow-first, but explicitly allow uprawnienia/token flows when the query asks how to perform the action. |

## Representative failure clusters

### workflow_should_have_hit_but_went_legal

- other / mixed routing (workflow confidence too low) — count=2, total_freq=7
- JPK tags / procedural-vs-legal ambiguity (clarification gate masking workflow hit) — count=2, total_freq=4
- KSeF permissions / authorization / invoice circulation (workflow eligibility issue) — count=1, total_freq=4
- accounting_operational / księgowanie / KPiR / okresy (workflow eligibility issue) — count=1, total_freq=4
- JPK tags / procedural-vs-legal ambiguity (workflow eligibility issue) — count=1, total_freq=3

### legal_should_have_stayed_legal_but_went_workflow

- accounting_operational / księgowanie / KPiR / okresy (routing keyword issue) — count=3, total_freq=41
- accounting_operational / księgowanie / KPiR / okresy (workflow confidence too low) — count=3, total_freq=23
- pełnomocnictwa / podpis / kanały złożenia (workflow confidence too low) — count=3, total_freq=18
- KSeF permissions / authorization / invoice circulation (workflow confidence too low) — count=1, total_freq=15

### weak_mixed_routing

- JPK tags / procedural-vs-legal ambiguity (clarification gate masking workflow hit) — count=1, total_freq=2
- other / mixed routing (workflow confidence too low) — count=1, total_freq=1
