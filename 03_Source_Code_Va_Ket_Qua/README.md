# FairDispatch — MOMAQL Fairness-Aware Ride-Hailing Dispatch

Independent, from-scratch **trend replication** of the qualitative claims in
Kang et al. [2024], *"Long-term Fairness in Ride-Hailing Platform"* (ECML
PKDD 2024, [arXiv:2407.17839](https://arxiv.org/abs/2407.17839)) — a
multi-objective RL dispatch policy (MOMAQL) that trades off driver-income
fairness against utility, using a demand forecast to avoid myopic
per-window fairness decisions.

This is a **qualitative trend replication**, not an exact numerical
reproduction — the source paper does not publish enough implementation
detail (MLP architecture, driver count, spatial clustering algorithm, exact
seeds) for exact reproduction to be a meaningful goal. Every deviation from
the paper is disclosed explicitly rather than smoothed over. All numbers in
this repository are real simulation output, computed from a real 2013 NYC
TLC taxi temporal slice (912,375 training / 195,508 validation / 195,510
test trips).

## Key results (real, 5-seed mean unless noted)

| Policy | Utility ($) | Gini |
|---|---:|---:|
| **MOMAQL** | **1,422,441** | **0.204** |
| Greedy | 1,001,551 | 0.531 |
| Nearest | 789,444 | 0.430 |
| LAF | 766,265 | 0.002 |
| Exact REASSIGN | 648,160 | 0.417 |

- **C1 (utility–fairness trade-off exists):** Reproduced.
- **C2 (MOMAQL beats adapted baselines on balance):** Reproduced, within the
  adapted-baseline scope disclosed above.
- **C3 (long-horizon RL behavior stabilizes):** Partially reproduced — Q
  coverage and per-day score composition stabilize, but only correlational
  evidence, not a controlled causal test.
- **C4 (forecast improves long-term fairness): Not Reproduced.** Utility
  advantage opens up between day 14–21 and reaches +20% by day 37, but
  Gini/variance show **No-Forecast is fairer than Full** at every checkpoint
  from day 21 onward — the opposite direction from the paper's claim. The
  paper's own day-3 crossover is not observed either way.
- **C5 (forecast ablation helps Utility + Fairness):** Partial — Utility
  component reproduced (+22.4%, 5/5 seeds); **Fairness component NOT
  reproduced** (No-Forecast is fairer than Full, not the other way round).
- **C6 (removing fairness maximizes utility, worsens inequality):** Partial —
  inequality direction reproduced (Gini 0.204 → 0.450), utility direction
  **not** reproduced (utility falls −37% here vs. rises sharply in the
  paper).

A later **Final Held-out Temporal Test** (frozen protocol, run once on
`test.parquet` after every configuration choice above was locked) confirmed
13/13 pre-specified Validation findings generalize in the same direction on
Test — including the C4 discrepancy above, which also held on Test. This
strengthens confidence that the implementation's behavior is temporally
robust; it does **not** convert C4 into a reproduced claim. See
`final_test/FINAL_TEST_MENTOR_SUMMARY.md` and Sec. 8–9 of the Research
Report / Sec. 8 of the Technical Documentation for the full dual-axis
(`heldout_generalization` vs. `paper_replication_verdict`) claim table.

Six further mechanism experiments (fleet-scale sweep, spatial candidate-pool
depth, day-by-day Q-table convergence, weekly demand-cycle test, a real
PyTorch MLP demand forecaster benchmarked head-to-head against the tabular
Q-table, and a fairness/lookahead score-balance trace) dig into *why* the
day-14–21 transition happens, not just *when*. Full claim-by-claim verdicts
are in the Research Report (see below).

## Repository layout

```text
03_Source_Code_Va_Ket_Qua/   # this bundle's root; identical relative layout
│                             # to the fairdispatch_v3_clean/ dev repo it was
│                             # copied from, just a different root folder name
├── src/
│   ├── simulator.py        # batched dispatch sim: init_drivers, feasible_drivers,
│   │                        #   commit_trip, run_simulation_batched/_with_horizon
│   └── policies.py         # Greedy, Nearest, LAF, Exact REASSIGN, MOMAQL
├── common_loader.py         # parquet -> request-dict loader; Gini/variance/std/CV
├── train_momaql.py          # trains the canonical tabular Q(zone,hour) table
├── run_r1.py                 # R1: 5-policy baseline comparison
├── run_r2_ablation.py        # R2: Full / w/o-Forecast / w/o-Fairness ablation
├── run_pareto_frontier.py    # utility-fairness Pareto sweep over lambda
├── run_multi_horizon.py      # multi-horizon trajectory study (day 1-37)
├── run_complete_verifications.py    # fleet-scale sweep + spatial disagreement
├── run_spatial_candidate_pool.py    # candidate-pool depth, core vs. periphery
├── run_q_table_convergence.py       # day-by-day Q-table convergence (37 days)
├── run_hypothesis1_weekly_cycle.py  # weekly demand-cycle mechanism test
├── run_hypothesis4_fairness_balance.py  # fairness/lookahead score-balance trace
├── train_and_eval_mlp.py     # real PyTorch MLP demand forecaster vs. tabular Q
├── make_report_figures.py    # regenerates every figure in docs/ from reports/*.csv
├── tests/test_simulator_invariants.py   # 20 invariant tests (no double-booking,
│                                          #   time monotonicity, etc. -- needs
│                                          #   data/*.parquet present locally to run)
├── scripts/final_test/       # Final Held-out Test pipeline: quality transform,
│                              #   baseline/ablation/long-horizon runners, summary
├── data/                     # train/val/test parquet splits (not tracked; see
│                              #   reports/dataset_checksums.json for SHA-256) +
│                              #   the trained Q-table JSON
├── reports/                  # every real Validation CSV/JSON result cited
├── final_test/                # Final Held-out Test outputs: protocol, data-quality
│                              #   gate, per-seed results, claim assessment, figures
└── docs/
    ├── docx_report/          # mentor-facing Research/Experimental Report (.docx)
    ├── techdoc/               # engineering Technical Documentation
    ├── ride_hailing_fairness_report_en/  # LaTeX paper (English) + compiled PDF
    └── ride_hailing_fairness_report_vi/  # LaTeX paper (Vietnamese) + compiled PDF
```

## Reproducing the results

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install numpy pandas pyarrow scipy matplotlib pytest python-docx
pip install torch   # only needed for train_and_eval_mlp.py

python -m pytest tests/test_simulator_invariants.py -q   # 20 passed
# (needs data/train.parquet present locally -- gitignored/not shipped in this
#  bundle; obtain the parquet splits separately first, see docs/techdoc/ Sec. 11.3)

python train_momaql.py            # canonical Q-table -> data/momaql_q_table_trained.json
python run_r1.py                  # -> reports/r1_validation_results.csv
python run_r2_ablation.py         # -> reports/r2_ablation_results.csv
python run_pareto_frontier.py     # -> reports/pareto_frontier_summary.csv
python run_multi_horizon.py       # -> reports/multi_horizon_results.csv
python make_report_figures.py     # regenerates every figure from the CSVs above
```

Full commands, module contracts, configuration, and known assumptions are
in `docs/techdoc/`. PyTorch is only required for `train_and_eval_mlp.py`.

## Disclosed deviations from the paper

- **Dataset:** NYC TLC **2013** (this project's own cleaned sample), not the
  paper's 2016 slice — an alternative temporal slice, not the same data year.
- **Forecast model:** a tabular `Q(zone, hour)` value estimator learned via
  online Bellman TD(0), not the paper's 3-layer MLP demand-count predictor.
  A real MLP is trained and benchmarked head-to-head in
  `train_and_eval_mlp.py` — the tabular Q-table wins on both utility and
  fairness.
- **Driver count (200), objective scalarization, and two baselines**
  (Exact REASSIGN, LAF) are disclosed assumptions/approximations — see
  the Research Report for the full component-by-component comparison table.

## References

- Yufan Kang, Jeffrey Chan, Wei Shao, Flora D. Salim, Christopher Leckie.
  *Long-term fairness in ride-hailing platform.* ECML PKDD 2024, LNCS 14949.
  [arXiv:2407.17839](https://arxiv.org/abs/2407.17839)
- Nixie S. Lesmana, Xuan Zhang, Xiaohui Bei. *Balancing efficiency and
  fairness in on-demand ridesourcing.* NeurIPS 2019.
- Tom Sühr, Asia J. Biega, Meike Zehlike, Krishna P. Gummadi, Abhijnan
  Chakraborty. *Two-sided fairness for repeated matchings in two-sided
  markets.* KDD 2019.

---

*AI Research Internship, Ride Allocation Group. Progress snapshot: August
2026.*
