PYTHON ?= python3
PROJECT_PYTHONPATH ?= src

.PHONY: doctor test app-smoke verify clean

doctor:
	$(PYTHON) --version
	$(PYTHON) -m pip --version
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -c "import importlib.util as u, sys; missing=[m for m in ('pandas', 'streamlit', 'pytest', 'cpg_methylation_mvp') if u.find_spec(m) is None]; sys.exit('Missing packages: ' + ', '.join(missing) + '. Run: pip install -e \".[dev]\"') if missing else print('doctor OK: required imports available')"

test:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m pytest -q

app-smoke:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m pytest -q tests/test_streamlit_smoke.py

verify: doctor test

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
