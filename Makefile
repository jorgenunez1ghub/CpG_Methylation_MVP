PYTHON ?= python3
PROJECT_PYTHONPATH ?= src

.PHONY: doctor lint typecheck test app-smoke verify clean

doctor:
	$(PYTHON) --version
	$(PYTHON) -m pip --version
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -c "import importlib.util as u, sys; missing=[m for m in ('mypy', 'pandas', 'pytest', 'ruff', 'streamlit', 'cpg_methylation_mvp') if u.find_spec(m) is None]; sys.exit('Missing packages: ' + ', '.join(missing) + '. Run: pip install -e \".[dev]\"') if missing else print('doctor OK: required imports available')"

lint:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m ruff check app src tests

typecheck:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m mypy

test:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m pytest -q

app-smoke:
	PYTHONPATH=$(PROJECT_PYTHONPATH) $(PYTHON) -m pytest -q tests/test_streamlit_smoke.py

verify: doctor lint typecheck test

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +
