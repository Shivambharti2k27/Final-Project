# Independent Review: Answers to Technical Concerns

Evidence refers to the source as reviewed and the outputs of the isolated copy at `C:\Users\shiva\Downloads\project_verify_copy`. No conclusion below treats generated data as real bearing measurements.

## A. Dataset and Provenance

**Source:** All analysis signals in the successful run were produced by this project's own simulator. [`generate_dataset`](../../src/dataset.py#L16-L58) calls [`simulate_signal`](../../src/simulator.py#L55-L126) to generate classification windows; [`simulate_life_histories`](../../src/degradation.py#L17-L58) calls the same simulator for degradation observations. The files are saved under `data/` as NPZ signals plus CSV metadata. The 4,000 classification windows, 1,200 RUL windows, and all reported labels are synthetic. No CWRU or other real dataset was used for training or evaluation.

The optional CWRU attempt used this exact URL from `src/validate_cwru.py`:

`https://engineering.case.edu/sites/default/files/12k_drive_end_bearing_fault_data.zip`

The URL is defined in [`src/validate_cwru.py`](../../src/validate_cwru.py#L12-L23). In the isolated copy, `python run_all.py` recorded `HTTPError: HTTP Error 404: Not Found`, `downloaded: false`, and `real_data_validation_done: false` in `results/cwru_validation_status.json`. The attempt failed; real-data validation was not done.

| Item | Verified value |
|---|---|
| Classification samples/windows | 4,000, 1,000 per class |
| Classes | Healthy, Inner Race, Outer Race, Ball |
| Sampling rate | 12,000 samples/s (12 kHz) |
| Window length | 4,096 samples, about 0.3413 s at 12 kHz |
| Classification runs/split | 80 total; 56 train, 12 validation, 12 test |
| Classification windows/split | 2,800 train, 600 validation, 600 test (50 windows/run) |
| RUL observations | 1,200 (30 lives × 40 observations) |
| RUL split | 21 train lives, 4 validation lives, 5 test lives; respectively 840, 160, 200 observations |

[`src/dataset.py`](../../src/dataset.py#L24-L50) creates 20 run IDs per class and places 10 runs per class into each operating domain. [`grouped_indices`](../../src/train_classification.py#L53-L65) splits unique `run_id` values before mapping them to window indices. [`train_rul_models`](../../src/train_rul.py#L98-L109) splits unique `life_id` values before mapping life IDs to rows.

## B. Leakage Review

**Main split:** grouped, not random-window. The main classifier uses whole run IDs in one split only (56/12/12 runs). The RUL experiment uses whole life IDs in one split only (21/4/5 lives). This is the right basic design for adjacent windows from a common simulated run or life.

**Training and scaling:** classical estimators fit only `x[train_idx]`; CNN weights fit on training windows, validation is used for model selection/early stopping, and the final test windows are evaluated after fitting ([`src/train_classification.py`](../../src/train_classification.py#L151-L188)). RUL `StandardScaler` is fit on `x[train_idx]` only ([`src/train_rul.py`](../../src/train_rul.py#L119-L133)). Test labels are used for reported scores and figures, not for fitting.

**Caveat:** both training functions call `x.fillna(x.median())` before splitting ([classifier](../../src/train_classification.py#L144-L146), [RUL](../../src/train_rul.py#L93-L95)), so if future feature tables contain missing values, the imputation median would use validation/test rows. The verification-copy CSVs contained zero numeric NaNs (`features.csv`: 4,000 rows, zero; `rul_features.csv`: 1,200 rows, zero), so this run had no actual median values derived from held-out rows. There is no feature selection based on test performance.

The speed/load robustness experiment is separate from the primary grouped split: it refits the chosen classical estimator using 1,400 low-domain windows that are in the primary training runs and scores 2,000 high-domain windows. Low and high domains are disjoint by `domain` and by the generator's chosen operating bands. The primary 12-run test score should not be confused with this domain-shift score.

## C. Do Numbers Match?

The copied pipeline regenerated metrics and report. Counts and rounded model metrics in `docs/report.md` agree with the copy's `results/metrics.json` at the report's stated precision:

| Report statement | Metrics/run result | Match? |
|---|---:|---|
| 4,000 windows, 80 classification runs | 4,000, 80 | Yes |
| 56/12/12 run split | 56/12/12 | Yes |
| 1,200 observations, 30 lives | 1,200, 30 | Yes |
| 21/4/5 life split | 21/4/5 | Yes |
| Four classical classifier models each: accuracy/weighted F1 1.000 | Each 1.000/1.000 | Yes |
| CNN: accuracy 0.825, weighted F1 0.821 | 0.825, 0.8210957645 | Yes after rounding |
| Noise F1: 1.000 at 0, 5, 10, 15, 20 dB | All five values 1.000 | Yes |
| Low-to-high domain accuracy 0.912, F1 0.910 | 0.9125, 0.9097356544 | Yes after rounding |
| RUL RF: RMSE 9.92 h, MAE 7.37 h, score 1.362 | 9.9246763, 7.3702055, 1.3623933 | Yes after rounding |
| RUL GB: RMSE 10.22 h, MAE 7.70 h, score 1.860 | 10.2207317, 7.6957414, 1.8595959 | Yes after rounding |
| Temporal CNN: RMSE 12.72 h, MAE 9.51 h, score 2.097 | 12.7229093, 9.5061293, 2.0972641 | Yes after rounding |
| Real-data validation not done; CWRU URL returned 404 | status says false / 404 | Yes |

**Numerical mismatch found outside the report table:** [`docs/theory.md`](../theory.md#L34) gives BSF as approximately 70.75 Hz at 1,800 rpm. The exact code calculation in [`src/simulator.py`](../../src/simulator.py#L32-L47) returns 70.721782 Hz, which rounds to **70.72 Hz**, not 70.75 Hz. The test's `pytest.approx(..., abs=0.2)` assertion in [`tests/test_simulator.py`](../../tests/test_simulator.py#L19-L24) accepts the rounded discrepancy. BPFO 107.550461 Hz, BPFI 162.449539 Hz, and FTF 11.950051 Hz round to the theory's 107.55, 162.45, and 11.95 Hz.

The README's counts, default epoch counts, and commands match the implementation ([README](../../README.md#L35-L54)). Its sentence “Model numbers are not claimed here until `run_all.py` has executed locally” is true of the README itself, but the adjacent report does contain measured values generated by the successful copy run ([README](../../README.md#L100), [report](../report.md#L5-L7)). The existing PPT outline says 4,000 windows and 30 lives, matching the run. The assumptions document's 1,000/class, 20 runs/class, 10 runs/domain, 30 lives, 40 steps/life, and severity threshold match generator defaults. The viva document contains 25 questions; the PPT outline contains 15 slides.

## D. Real Versus Simulated

Every metric and figure in the report is from this project's simulator and synthetic labels. `docs/report.md` says so in the abstract and limitations, and the dashboard caption warns that the models are not validated diagnostic advice. The CWRU archive was not downloaded, and no real-data model validation was done. Do not describe the 1.000 classifier accuracy or any RUL score as CWRU, rig, or field performance.

## E. Physics and Signal Checks

The simulator's geometry constants are in [`src/simulator.py`](../../src/simulator.py#L12-L18), and the formulas are in [`fault_frequencies`](../../src/simulator.py#L32-L47). At 1,800 rpm (`f_r = 30 Hz`), code calculations are:

| Frequency | Formula | Code result |
|---|---|---:|
| FTF | `fr/2 * (1 - d/D*cos(theta))` | 11.950051 Hz |
| BPFO | `n*fr/2 * (1 - d/D*cos(theta))` | 107.550461 Hz |
| BPFI | `n*fr/2 * (1 + d/D*cos(theta))` | 162.449539 Hz |
| BSF | `D*fr/(2*d) * (1 - (d/D*cos(theta))^2)` | 70.721782 Hz |

A direct five-second envelope-spectrum check in the copy measured the expected peak near each defect fundamental: inner race 162.6 Hz (0.093% difference), outer race 107.6 Hz (0.046%), ball 70.8 Hz (0.111%). The signal's resonance/jitter construction is at [`src/simulator.py`](../../src/simulator.py#L95-L118); envelope test code is in [`tests/test_simulator.py`](../../tests/test_simulator.py#L10-L39). The test passed its formulas and 2.5%-tolerance envelope checks. This verifies the generated synthetic signals under those settings; it does not verify physical sensor behavior.

The code creates shaft speed and load variation across windows/lives. Each individual 4,096-sample signal has a fixed `rpm` and `load`; continuous within-window speed ramping is not implemented. Impact timing receives 1.5% Gaussian interval jitter. A damped 2–4 kHz sinusoid is used as the structural response. These are simplified modeling choices, not a contact-dynamics solution.

## F. References

Crossref metadata and the publisher/catalog source were checked where retrievable. Confidence concerns the cited item being real; it does not mean every entry is fully specified in the report.

| Report reference | Assessment |
|---|---|
| McFadden & Smith (1984), “Model for the vibration produced by a single point defect in a rolling element bearing,” *Journal of Sound and Vibration* 96(1), 69–82 | **High confidence, verified.** Crossref returns the exact authors, title, year, journal, volume/pages; DOI is 10.1016/0022-460X(84)90595-9. The report omits the DOI. |
| Tandon & Choudhury (1999), “A review of vibration and acoustic measurement methods for the detection of defects in rolling element bearings,” *Tribology International* 32(8), 469–480 | **High confidence, verified.** Crossref returns exact title/authors/year/volume/pages; DOI is 10.1016/S0301-679X(99)00077-8. Note the similar but incorrect `...00007-8` DOI is not this article; the report omits a DOI. |
| Randall & Antoni (2011), “Rolling element bearing diagnostics: A tutorial,” *Mechanical Systems and Signal Processing* 25(2), 485–520 | **High confidence, verified.** Crossref record gives authors, 2011 issue, title variant with an em dash, volume/pages; DOI 10.1016/j.ymssp.2010.07.017. |
| Antoni (2006), “The spectral kurtosis: a useful tool for characterising non-stationary signals,” *Mechanical Systems and Signal Processing* 20(2), 282–307 | **High confidence, real and verifiable.** This exact work is cross-referenced by Randall & Antoni; DOI 10.1016/j.ymssp.2004.09.001. The report omits the DOI. A different DOI tested during lookup (`10.1016/j.ymssp.2005.09.002`) belongs to an unrelated hydraulic-seal article; do not use that DOI for Antoni's paper. |
| SKF, *Rolling Bearings Catalogue*, 6205-2RS1 product data | **Source is real; citation is incomplete.** The product is searchable at SKF, but no catalogue edition, page, or exact document link is specified. The attempted product page redirected to a region-selection page. Geometry is coded as assumed nominal data; the cited entry alone does not let a reader reproduce the exact dimensions. |
| ISO 15243:2017, *Rolling bearings — Damage and failures — Terms, characteristics and causes* | **High confidence that the standard identifier/title are real, but source link not established here.** The attempted ISO page URL returned 404, so the exact official landing-page link should be checked. |
| Saxena et al. (2008), “Damage propagation modeling for aircraft engine run-to-failure simulation,” 2008 International Conference on Prognostics and Health Management | **High confidence, verified.** Crossref returns exact title/authors, conference event and pages 1–9; DOI 10.1109/PHM.2008.4711414. |
| Case Western Reserve University Bearing Data Center, *12k Drive End Bearing Fault Data* | **High confidence the CWRU repository/dataset is real; not used in this project run.** The homepage fetch redirected, and the project's ZIP URL returned 404. The report cites no version/date for a downloaded subset because there was no download. |

No fabricated citation was identified. The weaknesses are missing DOIs/edition-level details and the failed official archive URL, not evidence that these publications were invented.

## G. Suspiciously High Classification Scores

All four feature-based classifiers scored accuracy and weighted F1 of 1.000 on 600 main test windows (150 per class). Their confusion matrix is exactly diagonal: 150 correct examples for each of the four classes, zero off-diagonal errors. The test runs are separate from training runs, so this is not explained by a random-window split bug. It is nevertheless a result on a hand-designed simulator whose fault label directly controls a repetitive impulse frequency, resonance excitation, modulation, and a small set of statistical/spectral features. Classes are cleanly separable by construction, and even the 0 dB requested SNR did not challenge the selected feature model.

The appropriate statement is: “The selected feature classifiers separated the four classes in this synthetic benchmark.” Do not say “near-perfect bearing diagnosis,” “proven industrial accuracy,” or imply field use. The more realistic next test is a locked evaluation on physically measured bearings from units never used for calibration, with documented sensor placement, load, speed, and fault severity.

The raw CNN scored 0.825 accuracy / 0.821 weighted F1. Its errors are specific: inner-race windows were predicted outer-race 57 times and ball 4 times; outer-race windows were predicted ball 33 times; ball windows were predicted healthy 11 times. The perfect noise curve is for the validation-selected **classical** model, not the CNN.

## H. Other Examiner-Level Weaknesses

1. **RUL penalty contradicts the stated cost direction.** [`asymmetric_rul_score`](../../src/train_rul.py#L46-L49) uses `exp(-error/10)-1` for negative error and `exp(error/13)-1` for positive error, where `error = predicted - actual`. Positive error overestimates remaining life and is the dangerous late prediction, but divisor 13 grows more slowly than divisor 10. The implementation therefore penalizes equal-magnitude underestimates more than overestimates, contrary to its docstring, score description, and viva answer. Report the metric as implemented only after explicitly acknowledging this; it is not currently evidence for the claimed “late errors penalized more” objective.
+2. **Very few independent prognostic units.** The RUL test includes five complete synthetic lives (200 correlated observations), not 200 independent bearings. The plotted curve is only life `L015`.
+3. **Health indicator is a privileged synthetic proxy.** It is generated from true simulated severity plus small noise, then passed to RUL training. Real deployments do not receive hidden simulator severity; they must derive a health indicator from measured vibration and validate it.
+4. **Assumed degradation law.** Every label is generated from an exponential severity curve and a chosen 0.90 threshold. The learned model is evaluated against that same synthetic mechanism, not unknown physical failures.
+5. **No within-window speed trajectory.** Speed changes between generated records, not during the 0.341 s sample window. The time series is therefore not a variable-speed order-tracking benchmark.
+6. **Synthetic feature fingerprints.** Fault type determines impulse periodicity and amplitude modulation directly. The perfect scores can reflect these idealized rule boundaries and should trigger a domain realism discussion.
+7. **Only one seeded split and one model seed are reported.** There are no confidence intervals or repeated group-split distributions; reproducibility of one split does not quantify statistical uncertainty.
+8. **Global median imputation is future leakage risk.** Current generated tables have no NaNs, but the implementation calculates medians before split creation. A later dataset with missing feature values would leak validation/test distribution information.
+9. **Feature inputs include operating conditions.** Classification numeric inputs include `rpm` and `load` as well as 24 signal features. Dashboard predictions also supply those slider values. This is not target leakage in this balanced design, but it affects transfer claims and should be stated.
+10. **Real-data step is only a download attempt.** It does not parse a successful archive or evaluate a model on it; even successful ZIP inspection only reports a MAT-file count.
+11. **Geometry citation is not audit-ready.** SKF product variant, catalogue revision, and page are missing. Bearing suffixes and catalogue variants should be checked against the exact physical sample.
+12. **No uncertainty or decision threshold.** Dashboard RUL is a point estimate with no interval, calibration, or risk logic and is labeled synthetic-only; it is not maintenance guidance.
+13. **Feature definitions are not all scale-invariant.** Spectral energy is normalized within each window, while RMS/crest/kurtosis are amplitude/noise sensitive. Real sensor gain and preprocessing could shift them.
+14. **“Combined” fault synthesis is not trained.** The simulator accepts Combined, but the four-class dataset and dashboard selector use only the four labels Healthy/Inner/Outer/Ball.
+15. **README install is CPU-specific but version constraints are loose.** Reproduction may choose newer package releases later; record a lock file or tested package versions for a formal hand-in.
