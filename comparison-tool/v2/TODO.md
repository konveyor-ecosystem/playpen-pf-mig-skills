# TODO

- [ ] **Incremental writes**: Write `evaluation.json` and `report.md` after each layer/attempt completes, not just at the end. If the run crashes mid-way, partial results are still available.

- [ ] **Extend existing run**: Add `--extend-run previous/evaluation.json` flag to `migeval evaluate`. Loads previous run, reuses `before` and existing attempt results, only runs layers on new `--attempt`(s), then recomputes all comparisons. Warn if target config hash differs between runs.
