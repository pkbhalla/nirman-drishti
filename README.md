# Nirman Drishti

Voice/text citizen road requests -> resolved to a PMGSY habitation (`HAB_ID`) -> equity-weighted priority ranking.
Built for Code for Communities 2.0, Theme 1 (AI for Digital Public Infrastructure & Governance).

## STATUS (read this first)
- **All demo data is SYNTHETIC**, shaped like the GeoSadak Habitation and Proposal PMGSY-III layers (columns `HAB_ID, BLOCK_ID, HAB_NAME, TOT_POPULA`; `MRL_ID, PROPOSED_L, WORK_NAME`). Names, coordinates and populations are invented.
- The Gemini paths (`extract.py`) are written but **untested against the live API**. Without `GEMINI_API_KEY` an offline rule-based fallback runs.
- `scripts/run_eval.py` is a stress test on synthetic data. Its adversarial cases are easy (empty or nonsense mentions), so the numbers measure the algorithm, not real-world accuracy. Replace with real Chandauli habitations and 60 hand-labelled transcripts for a real benchmark.
- `loader.py` (pyshp) reads the real shapefiles but has not been run on them. It assumes EPSG:4326; check the `.prj`.
- The real Road (DRRP) layer downloaded empty, so a true "existing road within 500 m" test needs another existing-road source. In the demo, distance is measured to proposal lines only.
- No Mission Antyodaya data. `vuln_ratio` is a placeholder; replace with Census SC/ST share or another sourced measure.
- The OMMAS `BLOCK_ID` -> LGD block code crosswalk is not included and must be built by hand (9 blocks in Chandauli).
- A habitation with zero requests can rank high (deficit dominates). That is intentional (silence is not "no need") but explain it to judges.

## Pipeline
1. `extract.py`: Gemini multimodal -> block, village mention (Latin script), issue, urgency.
2. `resolver.py`: within that block only, deterministic phonetic candidates (`phonetic.py`, handles b/v, final -wa, dropped vowels). Gemini only arbitrates near-ties. Low score, duplicates or no mention -> `ABSTAIN` with a follow-up question.
3. `geo.py`: point-to-line distance in metres (no polygons needed).
4. `scoring.py`: P = w1 demand + w2 deficit + w3 vulnerability, rank-normalised, demand per 1000 people and winsorised. Missing components are dropped and weights renormalised.

## Run
    pip install -r requirements.txt
    python scripts/build_demo.py
    python scripts/run_eval.py
    python -m pytest -q tests
    streamlit run app.py        # optional: export GEMINI_API_KEY=...

## Using real data
    from nirman_drishti.loader import load_habitations, load_proposals
    habs = load_habitations("Habitation.shp", ommas_district_id=<id>)
    meta, lines = load_proposals("Proposal_PMGSY_III.shp", lgd_district=135)   # Chandauli LGD district code
