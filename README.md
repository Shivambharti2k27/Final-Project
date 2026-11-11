# Physics-Based Rolling Bearing Fault Diagnosis and RUL

Final-year mechanical engineering project: a seeded, physics-informed simulator and machine-learning workflow for rolling-bearing fault diagnosis and remaining useful life (RUL) estimation. The benchmark uses nominal SKF 6205-2RS geometry and synthetic vibration only. No simulated output is represented as real sensor data.

## Requirements

- Python 3.10 or later (tested in this workspace with Python 3.13)
- A normal CPU laptop; GPU is not required
- Windows PowerShell, macOS, or Linux shell
- Internet access for the initial package install and optional CWRU archive attempt

## Installation

From the project directory, create and activate a virtual environment:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS/Linux, activate with `source .venv/bin/activate` instead. Install the CPU-only PyTorch wheel, then the remaining requirements:

```powershell
python -m pip install --upgrade pip
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

## Reproduce Everything

```powershell
python run_all.py
```

The default run synthesizes at least 4,000 classification windows (1,000 per class), 30 bearing lives, extracts features, trains all models, writes metrics and figures, attempts an optional official-source CWRU download, renders the report from measured metrics, and runs tests. To omit the network attempt or shorten CPU training during development:

```powershell
python run_all.py --skip-cwru
python run_all.py --windows-per-fault 100 --cnn-epochs 1 --rul-cnn-epochs 3 --skip-cwru
```

The reduced command is a development smoke run and does not meet the final 4,000-window dataset requirement. To run individual stages:

```powershell
python -m src.dataset --windows-per-fault 1000
python -m src.degradation
python -m src.features
python -m src.train_classification
python -m src.train_rul
python -m src.validate_cwru
python -m pytest -q
```

The classifier CNN uses 3 epochs by default; the RUL temporal CNN uses 18. Fixed seeds are defined in the source. Full re-execution overwrites generated data, artifacts, and figures in the project output folders.

## Dashboard

After running the pipeline and training artifacts:

```powershell
python -m streamlit run app/dashboard.py
```

The dashboard simulates a selectable bearing condition, plots a waveform and FFT, marks characteristic frequencies on the envelope spectrum, and uses the saved synthetic-data models where present. Predictions are educational and unvalidated for maintenance use.

## Structure

```text
app/dashboard.py             Streamlit condition-monitor dashboard
data/                         Generated windows, labels, and feature tables
docs/assumptions.md            Explicit modeling assumptions
docs/theory.md                 Bearing and signal-processing theory
docs/report.md                 Metrics-driven final report
docs/viva_questions.md         25 viva questions and answers
docs/ppt_outline.md            Slide-by-slide presentation outline
results/metrics.json           Measured test and robustness metrics
results/figures/               Confusion matrices, curves, and RUL plot
src/simulator.py               6205 kinematics and vibration generator
src/degradation.py             Synthetic run-to-failure life histories
src/features.py                Time, spectrum, and envelope feature extraction
src/train_classification.py    Grouped classical and raw-signal CNN diagnosis
src/train_rul.py               Grouped-life regression and temporal CNN
src/validate_cwru.py           Optional official-source archive attempt
tests/                         Simulator and data-pipeline tests
run_all.py                     End-to-end reproduction entry point
requirements.txt               Python dependencies
Makefile                       Common developer targets
```

## Outputs and Interpretation

- `data/classification_windows.npz` and `data/classification_metadata.csv`
- `data/features.csv`
- `data/degradation_windows.npz`, `data/degradation_metadata.csv`, and `data/rul_features.csv`
- `models/` contains fitted model artifacts
- `results/metrics.json` contains measured model metrics and split sizes
- `results/cwru_validation_status.json` records whether the optional archive attempt succeeded. A download is not itself model validation.
- `docs/report.md` is rendered from the current `metrics.json` after the pipeline runs.

Classification windows are split by simulated run; RUL observations are split by bearing life. Results must be described as **synthetic-only** unless independently reproduced and evaluated on real measurements. Model numbers are not claimed here until `run_all.py` has executed locally.

See [theory](docs/theory.md), [assumptions](docs/assumptions.md), and [report](docs/report.md) for formulas, parameter choices, limitations, and results.