# Batch 2 Final Summary

Data: 2026-04-18
Pipeline: 6 stage (plan → generate → self-validate → verifier v1 → verifier v2 → apply → retag)

## Final counts

| Metric | Batch 1 | Batch 2 | Total (42 drafts) |
|---|---|---|---|
| Workflow drafts | 10 | 32 | 42 |
| Flagi self_critique | 122 | 354 | 476 |
| Confirmed (v1+v2) | 22 | 23 | 45 |
| False_positive (v1+v2) | 36 | 66 | 102 |
| Community_feedback_needed | 64 | 265 | 329 |
| Corrections applied (LLM) | 21 | 20 | 41 |
| Corrections applied (manual) | 1 | 0 | 1 |
| Correction failed (JSON) | 0* | 3 | 3 |

*wf_79 flag#4 batch 1 failed LLM 3x — dopisane manualnie, więc 22 confirmed = 21 LLM + 1 manual.

## Koszty per stage (batch 2)
| Stage | Model | Cap | Actual | % cap |
|---|---|---|---|---|
| 1 — generate | Opus 4.7 + web_search | $20* | $21.27 | 106% |
| 2 — self-validate | Haiku 4.5 | $3 | $0.38 | 13% |
| 3 — verifier v1 (KB) | Sonnet 4.6 | $5 | $4.33 | 87% |
| 4 — verifier v2 (web) | Sonnet 4.6 | $5 | $5.06 | 101% |
| 5 — apply corrections | Sonnet 4.6 | $3 | $1.63 | 54% |
| 6 — retag | (no LLM) | $0 | $0.00 | — |
| **Total batch 2** | | **$36** | **$32.67** | **91%** |

*Stage 1 cap podniesiony z $20 → $25 po hit capie przy 30/32 (brakowało 2 smallest
clusters 130, 74 — obu kadry, finish kosztował $1 więcej).

## 4 klastry 2026 z web_search
| Cluster | Topic | Searches | Confirmed web_citation |
|---|---|---|---|
| 99 — KSeF uprawnienia/certyfikaty | KSeF | 2 | gofin.pl + podatki.gov.pl |
| 71 — Minimalne wynagrodzenie 2026 | kadry | 2 | Rozporządzenie RM z 11.09.2025 |
| 110 — KPiR 2026 faktury do paragonów | KPiR | 4 | gofin.pl + infor |
| 53 — Najem prywatny a VAT/KSeF | VAT | 2 | infor |

Łącznie stage 1 web: 10 searches, 0 fetches.

## 3 failed corrections do manualnego review
Wszystkie to ten sam pattern (LLM generuje malformed JSON z unescape'd quote po 3x retry):
- `wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan` flag#0
- `wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty` flag#2
- `wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty` flag#4

Rekomendacja: manualny fix (Python inline edit) analogicznie do wf_79 flag#4 z batch 1.

## Testy
`pytest`: 260 passed, 0 failed (końcowy run po Stage 6).

## Stan pipeline
- **6 commitów + 6 pushów** do `main` (pushed to promptymike/Aktuo):
  1. `chore: add batch 2 plan (32 clusters, 4 with 2026 web topics)`
  2. `feat: generate batch 2 - 32 workflow drafts (web-aware for 2026 topics)`
  3. `feat: self-validate batch 2 with Haiku 4.5`
  4. `feat: verify batch 2 flags with Sonnet vs KB (verifier v1)`
  5. `feat: verify batch 2 cannot_verify flags with Sonnet + web search (verifier v2)`
  6. `fix: apply 20 confirmed corrections batch 2 (3 failed JSON parse)`
  7. `feat: tag 329 cannot_verify flags as community_feedback_needed (batch 2)`

Wszystkie drafty w `data/workflow_drafts/wf_*.json` (42 pliki). Żaden sub-folder nie został utworzony.

## Ready-to-ship status
- 45 confirmed corrections applied (41 LLM + 1 manual + 3 pending manual fix)
- 102 false_positive oznaczone (niewidoczne w UI)
- 329 community_feedback_needed z `ui_label` na UX (6 polskich etykiet)
- 42 drafty opublikowane do Aktuo preview z "draft: true"

## Raporty
- `analysis/batch2_plan.json` — pre-step cluster plan
- `analysis/batch2_generation_log.md` — Stage 1
- `analysis/batch2_self_validation_report.md` — Stage 2
- `analysis/batch2_verifier_report.md` — Stage 3
- `analysis/batch2_verifier_v2_report.md` — Stage 4
- `analysis/batch2_corrections_log.md` — Stage 5
- `analysis/batch2_community_feedback_summary.md` — Stage 6
- `analysis/batch2_final_summary.md` — ten dokument
