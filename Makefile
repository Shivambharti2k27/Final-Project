.PHONY: install test reproduce dashboard clean

PYTHON ?= .venv/Scripts/python.exe

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

reproduce:
	$(PYTHON) run_all.py

dashboard:
	$(PYTHON) -m streamlit run app/dashboard.py

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['data', 'models']]; [p.unlink(missing_ok=True) for p in ['results/metrics.json', 'results/cwru_validation_status.json']]"