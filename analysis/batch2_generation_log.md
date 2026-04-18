# Batch 2 Generation Log

Data: 2026-04-18
Model: claude-opus-4-7 (fallback claude-opus-4-6)
OK: 32/32
Failed: 0

## Cumulative totals (run 1 + resume run 2)
- Run 1: 30/32 drafts, in=568168, out=155142, web_req=10, cost=$20.2582, elapsed=2519s
  - hit $20 cost cap after cluster 30; 2 smallest kadry clusters (130, 74) skipped
- Run 2 (resume): 2/32 drafts, in=18955, out=9672, web_req=0, cost=$1.0097, elapsed=153s
- **TOTAL: in=587123, out=164814, web_req=10, cost=$21.2679, elapsed=~45 min**
- Cap raised from $20 → $25 on run 2 (documented) to finish last 2 clusters (~$1 cost)

## Last run's per-cluster detail (mostly `ok_resumed` from run 1)

## Per cluster
| # | target_key | topic | 2026? | status | in | out | web | s |
|---|---|---|---|---|---|---|---|---|
| 1 | 45 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 2 | 66 | VAT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 3 | 35 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 4 | merge_101_102 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 5 | 99 | KSeF | Y | ok_resumed | 0 | 0 | 0 | 0.0 |
| 6 | merge_33_86_95 | PIT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 7 | 125 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 8 | 8 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 9 | 82 | ZUS |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 10 | 143 | software |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 11 | 138 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 12 | 98 | ZUS |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 13 | 15 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 14 | 34 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 15 | 90 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 16 | 24 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 17 | 19 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 18 | 87 | PIT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 19 | 30 | JPK |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 20 | 48 | PIT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 21 | 53 | VAT | Y | ok_resumed | 0 | 0 | 0 | 0.0 |
| 22 | 4 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 23 | 71 | kadry | Y | ok_resumed | 0 | 0 | 0 | 0.0 |
| 24 | 51 | rachunkowość |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 25 | 110 | KPiR | Y | ok_resumed | 0 | 0 | 0 | 0.0 |
| 26 | 94 | VAT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 27 | 135 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 28 | 127 | kadry |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 29 | 134 | ZUS |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 30 | 75 | PIT |  | ok_resumed | 0 | 0 | 0 | 0.0 |
| 31 | 130 | kadry |  | ok | 9241 | 5220 | 0 | 79.43 |
| 32 | 74 | kadry |  | ok | 9714 | 4452 | 0 | 69.39 |
