# Presentation Outline

1. **Title and motivation** — project title, bearing reliability problem, project scope.
2. **Bearing anatomy** — 6205-2RS layout, races, balls, cage, defect locations.
3. **Characteristic frequencies** — BPFO, BPFI, BSF, FTF equations and 1,800 rpm example.
4. **Signal processing background** — impact resonance, filtering, Hilbert envelope analysis.
5. **Physics-based simulator** — 12 kHz sampling, resonance, jitter, speed/load/severity/noise assumptions.
6. **Synthetic datasets** — four fault classes, 4,000 windows, 30 run-to-failure lives.
7. **Feature engineering** — time, spectrum, envelope features with example plots.
8. **Experimental protocol** — run/life grouped train-validation-test splits and leakage prevention.
9. **Fault diagnosis models** — SVM, Random Forest, KNN, Gradient Boosting, 1-D CNN.
10. **Diagnosis results** — held-out confusion matrix, noise robustness, speed/load domain test.
11. **Degradation and RUL** — health indicator, failure threshold, target definition.
12. **RUL models and results** — classical regressors versus temporal CNN, predicted/true life curve.
13. **Limitations and real-data status** — explicitly simulated-only results and CWRU attempt outcome.
14. **Conclusion and future work** — main takeaways, measured-data validation plan, uncertainty/domain adaptation.
15. **Questions** — backup slides with formulas, parameter assumptions, metric definitions.