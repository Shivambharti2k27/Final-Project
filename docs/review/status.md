# Independent Review: Status and Execution

## Scope and Safety Record

Review target: the project as found in `C:\Users\shiva\Downloads\Project Btech`, including the current `app/dashboard.py`. Execution used a separate copy at `C:\Users\shiva\Downloads\project_verify_copy` with a fresh `.venv`; full pipeline outputs below are from that copy. The copy's `requirements.txt` installation completed, and the copy used Python 3.13.15 with CPU PyTorch 2.15.0+cpu.

**Important incident:** during environment setup, one pip self-upgrade was mistakenly issued while the terminal's current directory was the original project. It returned `ERROR: Operation cancelled by user` after starting pip removal; a subsequent pip output warned of an incomplete `~ip-26.2.1.dist-info` under the original `.venv`. I did not run tests/pipeline in the original project, and did not edit its source, docs, data, models, or results. However, I cannot honestly confirm that no existing file changed inside the original `.venv`; I left it untouched after recognizing the mistake and did not attempt repair. The verification copy itself was thereafter addressed by absolute path.

## Project Inventory

Transient `__pycache__`, `.pytest_cache`, and the virtual environment are omitted below. `docs/review/` contains only the four new review documents.

| Path | Purpose |
|---|---|
| `.gitignore` | Excludes virtual environment, caches, generated data, models, and secrets from Git. |
| `Makefile` | Convenience targets for install, tests, reproduction, dashboard, and cleanup. |
| `README.md` | Setup, CPU PyTorch install, pipeline commands, dashboard instructions, outputs, and limitations. |
| `requirements.txt` | Declares numerical, ML, CPU-capable PyTorch, test, Jupyter, Streamlit, and HTTP dependencies. |
| `run_all.py` | Runs generators, feature extraction, training, optional CWRU attempt, report generation, and tests in sequence. |
| `app/dashboard.py` | Streamlit UI for synthetic vibration plots, fault prediction, and a synthetic RUL estimate. |
| `src/__init__.py` | Marks `src` as a Python package. |
| `src/simulator.py` | Bearing geometry, BPFO/BPFI/BSF/FTF formulas, vibration synthesis, resonance, jitter, and noise. |
| `src/dataset.py` | Creates the four-class, run-grouped classification windows and metadata. |
| `src/degradation.py` | Creates severity histories, health indicators, failure thresholds, and true simulated RUL labels. |
| `src/features.py` | Extracts time, FFT, and envelope-spectrum features and writes feature tables. |
| `src/result_store.py` | Merges classification and RUL metric sections into `results/metrics.json`. |
| `src/train_classification.py` | Group-splits runs; fits four classical classifiers and a 1-D CNN; writes scores and plots. |
| `src/train_rul.py` | Group-splits life histories; fits two regressors and a temporal CNN; writes scores and a plot. |
| `src/validate_cwru.py` | Attempts a size-limited download of one official-source CWRU archive and logs skip/failure status. |
| `src/write_report.py` | Regenerates `docs/report.md` using `results/metrics.json` and CWRU status. |
| `tests/test_simulator.py` | Checks 6205 fault-frequency values and envelope-spectrum peaks for three fault types. |
| `tests/test_data_pipeline.py` | Checks reproducible synthetic data, finite features, and decreasing RUL per life. |
| `tests/test_rul_model.py` | Checks the temporal CNN accepts feature-channel-first sequences and returns one estimate per sequence. |
| `data/classification_windows.npz` | Generated 4,000 vibration windows, 4,096 samples each. |
| `data/classification_metadata.csv` | Class, run, speed, load, severity, SNR, and domain metadata for classification windows. |
| `data/features.csv` | Engineered classification features joined to classification metadata. |
| `data/degradation_windows.npz` | Generated 1,200 vibration windows across 30 simulated lives. |
| `data/degradation_metadata.csv` | Life, fault, speed/load, age, severity, health indicator, failure threshold, and RUL labels. |
| `data/rul_features.csv` | Engineered RUL features joined to degradation metadata. |
| `models/classification_cnn.pt` | Saved raw-waveform classification CNN weights. |
| `models/fault_classifier.joblib` | Saved validation-selected classical fault classifier. |
| `models/fault_feature_columns.json` | Feature-column order for dashboard inference. |
| `models/rul_preprocessing.joblib` | RUL feature names and imputation medians for dashboard inference. |
| `models/rul_regressor.joblib` | Saved validation-selected classical RUL regressor. |
| `models/rul_temporal_cnn.pt` | Saved temporal RUL CNN and its feature scaling metadata. |
| `results/metrics.json` | Measured classification and RUL scores plus split counts. |
| `results/cwru_validation_status.json` | Records the attempted official archive URL and 404 response. |
| `results/figures/best_classifier_confusion.png` | Confusion matrix for the validation-selected classical classifier. |
| `results/figures/cnn_confusion.png` | Confusion matrix for the raw-waveform CNN. |
| `results/figures/gradient_boosting_confusion.png` | Gradient Boosting confusion matrix. |
| `results/figures/knn_confusion.png` | KNN confusion matrix. |
| `results/figures/noise_robustness.png` | Weighted F1 of the selected classical classifier by test SNR. |
| `results/figures/random_forest_confusion.png` | Random Forest confusion matrix. |
| `results/figures/rul_prediction.png` | True and temporal-CNN RUL trace for one selected test life. |
| `results/figures/svm_confusion.png` | SVM confusion matrix. |
| `docs/assumptions.md` | Explicit bearing, signal, data, and model assumptions. |
| `docs/ppt_outline.md` | Existing 15-slide presentation outline. |
| `docs/report.md` | Existing metrics-driven final report. |
| `docs/theory.md` | Existing bearing and signal-processing theory. |
| `docs/viva_questions.md` | Existing 25 viva questions and answers. |
| `docs/review/status.md` | This independent execution and component-status report. |
| `docs/review/concerns.md` | Evidence-based answers to the requested technical concerns. |
| `docs/review/project_explained.md` | Student-facing implementation and results walkthrough. |
| `docs/review/presentation_guide.md` | Timed scripts, dashboard demo, examiner questions, and preparation list. |

## Verification Commands and Results

The copy was created at the sibling path and received a fresh virtual environment. The first dependency command included `pip install --upgrade pip` and was interrupted; it is not counted as a project test or pipeline step. A subsequent ordinary-index requirements install stalled while fetching the 126.7 MB torch wheel and was stopped in the copy. The CPU wheel was installed from PyTorch's CPU index, then the full copied requirements file completed successfully.

| Step | Exact command/action in the verification copy | Result |
|---|---|---|
| Fresh environment | `C:/Users/shiva/AppData/Local/Programs/Python/Python313/python.exe -m venv C:/Users/shiva/Downloads/project_verify_copy/.venv` | Passed. The selected interpreter path was verified to be in the copy. |
| CPU PyTorch | `C:/Users/shiva/Downloads/project_verify_copy/.venv/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu` | Passed; installed `torch 2.15.0+cpu`. |
| Declared dependencies | `C:/Users/shiva/Downloads/project_verify_copy/.venv/Scripts/python.exe -m pip install -r C:/Users/shiva/Downloads/project_verify_copy/requirements.txt` | Passed; pip reported successful installation of requirements and dependencies. |
| Tests before full pipeline | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m pytest -q` (working directory: copy) | Passed: `6 passed in 13.26s`. |
| Full reproduction | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe run_all.py` (working directory: copy) | Passed, exit code 0. See stage breakdown below. |
| Tests within full runner | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m pytest -q` (invoked by `run_all.py`) | Passed: `6 passed in 7.57s`. |
| Tests after repeatability checks | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m pytest -q` (working directory: copy) | Passed: `6 passed in 6.53s`. |
| Dashboard | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m streamlit run C:/Users/shiva/Downloads/project_verify_copy/app/dashboard.py --server.headless true --server.address 127.0.0.1 --server.port 8502` | Passed startup; browser title `Bearing Condition Monitor`, controls and waveform/FFT/envelope plots rendered. Server was then stopped. |

The full runner printed these stages and outcomes:

| Pipeline stage | Exact underlying command from `run_all.py` | Outcome / error |
|---|---|---|
| Classification data | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m src.dataset --windows-per-fault 1000` | Passed: saved 4,000 windows across 80 runs. |
| Degradation data | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m src.degradation` | Passed: saved 1,200 observations across 30 lives. |
| Classification features | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m src.features` | Passed: saved 4,000 feature rows. |
| Fault classifiers | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -c "from src.train_classification import train_classifiers; train_classifiers(cnn_epochs=3)"` | Passed; scores below. |
| RUL models | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -c "from src.train_rul import train_rul_models; train_rul_models(cnn_epochs=18)"` | Passed; scores below. |
| CWRU attempt | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m src.validate_cwru` | Graceful skip/failure recorded: `HTTPError: HTTP Error 404: Not Found`; real-data validation was not done. |
| Report generation | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m src.write_report` | Passed: report regenerated from copy metrics. |
| Full-run tests | `C:\Users\shiva\Downloads\project_verify_copy\.venv\Scripts\python.exe -m pytest -q` | Passed: 6 tests. |

No step in the copied `run_all.py` failed. The only failed setup attempt was the nonessential pip self-upgrade described above; the full declared requirements subsequently installed successfully in the copy.

## Reproducibility Check

The two key training functions were each run twice in the copy with their documented default epoch counts and identical generated inputs:

- Classification: `train_classifiers(root=copy_root, cnn_epochs=3)` twice. All recorded classification metric sections were exactly equal, including the CNN, noise, and domain scores.
- RUL: `train_rul_models(root=copy_root, cnn_epochs=18)` twice. The temporal-CNN scores were bit-identical. Two classical metric fields differed only by floating-point accumulation: Random Forest MAE by `8.88e-16` hours and validation RMSE by `1.78e-15` hours. They are identical at reported precision and within `1e-10` absolute tolerance.

This supports reproducibility on this interpreter/CPU setup, not guaranteed bitwise identity on every library/hardware version.

## Measured Copy Results

| Measure | Verification-copy result |
|---|---:|
| Classification windows / classes | 4,000 / 4 classes / 1,000 per class |
| Classification runs | 80 total; 56 train, 12 validation, 12 test |
| Samples / window; sample rate | 4,096; 12,000 Hz |
| RUL observations / lives | 1,200 / 30; 40 per life |
| RUL split | 21 train, 4 validation, 5 test lives |
| SVM, Random Forest, KNN, Gradient Boosting | Each test accuracy and weighted F1 = 1.000 |
| 1-D CNN diagnosis | Accuracy 0.825; weighted F1 0.8210957645 |
| Low-to-high speed/load domain check | Accuracy 0.9125; weighted F1 0.9097356544 |
| Selected classical RUL model | Gradient Boosting by validation RMSE; test RMSE 10.2207317 h, MAE 7.6957414 h |
| Random Forest RUL | Test RMSE 9.9246763 h, MAE 7.3702055 h |
| Temporal CNN RUL | Test RMSE 12.7229093 h, MAE 9.5061293 h |
| Envelope peaks measured in 5 s seeded tests at 1,800 rpm | Inner 162.6 Hz vs 162.45; outer 107.6 Hz vs 107.55; ball 70.8 Hz vs 70.7218 |

## Component Status

| Component | Status | Evidence |
|---|---|---|
| Data generation | Working (synthetic) | Full copy run wrote 4,000 windows; four balanced classes; six tests passed. |
| Degradation model | Partly working | Full copy run wrote 30 lives and 1,200 observations; labels reach zero at each final time. This is assumed exponential severity, not observed physical life. |
| Feature extraction | Working | Full copy run wrote 4,000 classification feature rows and RUL features; both had zero numeric NaNs. |
| Classification models | Partly working | Four classical models and CNN trained; grouped split is used. Perfect classical scores and simulated-only distributions limit evidential value. |
| RUL models | Partly working | Two regressors and a temporal CNN trained on life-grouped splits. The custom asymmetry implementation contradicts its stated late-error penalty. |
| Real-data validation | Not working / not completed | URL returned 404; status explicitly says `real_data_validation_done: false`. |
| Dashboard | Working as a synthetic demo | Copy server started and page/plots rendered in browser, then server stopped. No real sensor upload or live acquisition is implemented. |
| README | Working as setup guidance | Install and run commands are present; copy run validated the primary `run_all.py` path. |
| Report | Partly working | Metrics match at displayed precision and synthetic-only limitation is explicit. Theory file has a BSF rounding mismatch; the RUL asymmetry prose/code is contradictory. |
| Viva questions | Working as a starter | 25 numbered questions and answers are present; answers are mostly consistent with implementation but do not warn about the score-direction bug. |
| PPT outline | Working as an outline | 15 slides are listed. It is an outline, not a finished slide deck. |

## Manual Work Still Required

1. Replace or locate the current official CWRU download route and perform a documented evaluation on actual files; current CWRU validation is absent.
2. Obtain bearing-rig measurements and calibrate signal amplitudes, resonance, noise, speed variation, load, and defect evolution against them.
3. Resolve the asymmetric-score direction before presenting its numeric values as a late-failure penalty.
4. Add a documented exact SKF catalogue edition/page or product datasheet supporting the 6205 geometry, and complete DOI/URL details for references.
5. Present the perfect classical scores as simulator-separability results, not claimed field diagnostic accuracy.
6. Be ready to explain the four-class test confusion counts and the five-life RUL test size; the windows within one run/life are correlated observations, not independent bearings.
7. Convert `docs/ppt_outline.md` into actual slides and make original figures/tables suitable for the department's submission format.
