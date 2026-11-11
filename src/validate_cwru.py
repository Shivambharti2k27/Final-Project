"""Attempt an official CWRU 12 kHz drive-end archive download, skipping safely on failure."""

from __future__ import annotations

import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_ARCHIVE = "https://engineering.case.edu/sites/default/files/12k_drive_end_bearing_fault_data.zip"


def attempt_download(output_dir: Path = ROOT / "data", timeout_seconds: int = 12) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "cwru_12k_drive_end.zip"
    status: dict[str, object] = {
        "attempted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": OFFICIAL_ARCHIVE,
        "real_data_validation_done": False,
    }
    request = urllib.request.Request(OFFICIAL_ARCHIVE, headers={"User-Agent": "bearing-rul-course-project/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 250_000_000:
                raise ValueError(f"Archive exceeds 250 MB safety limit ({content_length} bytes)")
            with destination.open("wb") as archive_file:
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > 250_000_000:
                        raise ValueError("Archive exceeded the 250 MB safety limit")
                    archive_file.write(chunk)
        with zipfile.ZipFile(destination) as archive:
            mat_files = [name for name in archive.namelist() if name.lower().endswith(".mat")]
        status.update({
            "downloaded": True,
            "archive_bytes": destination.stat().st_size,
            "mat_file_count": len(mat_files),
            "real_data_validation_done": False,
            "note": "Official archive download succeeded and was inspected; model evaluation on real data was not performed.",
        })
    except Exception as error:  # Network, URL, archive, and filesystem failures all skip gracefully.
        destination.unlink(missing_ok=True)
        status.update({"downloaded": False, "skip_reason": f"{type(error).__name__}: {error}"})
    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "cwru_validation_status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))
    return status


if __name__ == "__main__":
    attempt_download()
