"""Reproduce the full synthetic bearing diagnosis and RUL project."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str], description: str) -> None:
    print(f"\n=== {description} ===", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows-per-fault", type=int, default=1000)
    parser.add_argument("--cnn-epochs", type=int, default=3)
    parser.add_argument("--rul-cnn-epochs", type=int, default=18)
    parser.add_argument("--skip-cwru", action="store_true", help="Skip the optional official-source download attempt")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    python = sys.executable
    run([python, "-m", "src.dataset", "--windows-per-fault", str(args.windows_per_fault)], "Generate classification data")
    run([python, "-m", "src.degradation"], "Generate run-to-failure histories")
    run([python, "-m", "src.features"], "Extract classification features")
    run([python, "-c", "from src.train_classification import train_classifiers; train_classifiers(cnn_epochs="
         + str(args.cnn_epochs) + ")"], "Train fault diagnosis models")
    run([python, "-c", "from src.train_rul import train_rul_models; train_rul_models(cnn_epochs="
         + str(args.rul_cnn_epochs) + ")"], "Train RUL models")
    if not args.skip_cwru:
        run([python, "-m", "src.validate_cwru"], "Attempt optional CWRU download")
    run([python, "-m", "src.write_report"], "Render report from measured metrics")
    if not args.skip_tests:
        run([python, "-m", "pytest", "-q"], "Run project tests")


if __name__ == "__main__":
    main()