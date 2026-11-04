# One entrypoint for the whole pipeline. Every Python step runs isolated (-I).
# make data      fetch public sources and the Screener harvest (network)
# make sector    rebuild the three sector modules (needs the user-supplied NPCI/IRDAI files in data/raw/manual)
# make model     HDFC model: inputs -> workbook -> scenario export -> tornado -> workbook with Tornado tab -> export
# make outputs   SQL warehouse and queries, memo, cockpit, Tableau extracts
# make test      reconciliation checks, pytest, code lint
# make site      export site data, test the browser engine against the Excel export, build site/dist
# make all       model + outputs + test + site (uses committed data; run `make data sector` first for a full refresh)
# make ci-local  run `make all` in a fresh clone of the last commit (committed files only, as CI sees them)
# The steerco deck is on hold: build it explicitly with `make deck`.
PY := python3 -I

.PHONY: all data sector model outputs deck test site ci-local clean

all: model outputs test site

data:
	$(PY) pipeline/fetch.py
	$(PY) pipeline/screener.py
	$(PY) pipeline/fetch_docs.py
	$(PY) pipeline/fetch_docs.py --since 2023-10 --symbols HDFCBANK --kinds PPT --ppt-quarters Q2FY24,Q3FY24,Q4FY24,Q1FY25,Q2FY25,Q3FY25,Q4FY25,Q1FY26,Q2FY26,Q3FY26,Q4FY26,Q1FY27,Q2FY27
	$(PY) pipeline/extract_hdfc_quarterly.py

sector:
	$(PY) pipeline/build_bank_facts.py
	$(PY) pipeline/shapley.py
	$(PY) pipeline/build_bank_xlsx.py
	$(PY) pipeline/extract_irdai.py
	$(PY) pipeline/insurance_model.py
	$(PY) pipeline/upi_model.py
	$(PY) decks/build_decks.py

model:
	$(PY) pipeline/hdfc_walk.py
	$(PY) pipeline/deposit_beta.py
	$(PY) pipeline/build_hdfc_model.py
	$(PY) pipeline/export_scenarios.py
	$(PY) pipeline/tornado.py
	$(PY) pipeline/build_hdfc_model.py
	$(PY) pipeline/export_scenarios.py

outputs:
	$(PY) pipeline/hdfc_quarterly.py
	$(PY) pipeline/breakevens.py
	$(PY) pipeline/call_topics.py
	$(PY) pipeline/warehouse.py
	$(PY) pipeline/run_sql.py
	$(PY) decks/build_memo.py
	$(PY) viz/build_dashboard.py
	$(PY) viz/tableau/build_extracts.py

deck:
	$(PY) decks/build_hdfc_deck.py

test:
	$(PY) pipeline/checks.py
	python3 -m pytest -q -p no:cacheprovider tests
	python3 -m ruff check .

site:
	$(PY) pipeline/export_site_data.py
	cd site && npm ci --no-audit --no-fund && npx vitest run && npx vite build

ci-local:
	rm -rf .ci-local && git clone -q . .ci-local && $(MAKE) -C .ci-local all; status=$$?; rm -rf .ci-local; exit $$status

clean:
	rm -f data/fs.duckdb
