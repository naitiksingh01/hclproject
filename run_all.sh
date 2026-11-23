#!/usr/bin/env bash
# Re-creates every generated artefact from scratch (Linux/macOS/Git-Bash)
set -e
python python/01_generate_dataset.py
python python/02_clean_sales.py
python python/03_validate_sql.py
python python/04_build_dashboard.py
python python/05_er_diagram.py
