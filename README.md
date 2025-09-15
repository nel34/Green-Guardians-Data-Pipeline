# Green Guardians — Data Pipeline

This repository provides a small Streamlit-based app and helper modules to analyze seagrass and related ecological data from a single Excel workbook. The app visualizes seagrass cover, mapped seagrass surface, dugong feeding evidence and cyanobacteria evidence.

## Project structure

- `app.py` — Main Streamlit app launcher and page router. Displays a sidebar menu to switch between modules.
- `seagrass_cover.py` — Page showing average seagrass cover by year and by month, with filters for years and months and interactive Plotly charts.
- `seagrass_cover_zones.py` — Utilities and/or page to compute and visualize seagrass cover per zone (zone-level summaries).
- `drone_mapping.py` — Visualizations for mapped seagrass surface and dugong feeding evidence mapping (grouped by year and month).
- `dugong_grazing.py` — Analyses and plots related to dugong grazing / feeding evidence across sites and months.
- `Cyanobacteria_evidence.py` — Dedicated page for cyanobacteria evidence visualizations (moved out from `drone_mapping.py`).
- `TRANSECT_DATA_SUMMARY.xlsx` — Excel workbook that must contain the data. See Compatibility below.
- `requirements.txt` — Python dependencies used by the app.

## Module responsibilities (summary)

- `app.py`:
  - Sets the Streamlit page configuration and provides a sidebar menu to navigate between the different pages.
  - Imports each module's `main()` function and calls it when the corresponding page is selected.

- `seagrass_cover.py`:
  - Loads data from the Excel workbook and computes average seagrass cover per year (with standard errors).
  - Provides filters for selecting years and months. When years are selected, the monthly chart is filtered to the same years.
  - Renders interactive Plotly bar charts and a numeric summary table.

- `seagrass_cover_zones.py`:
  - Provides zonal summaries of seagrass cover (if present in the dataset). Used by the app to display zone-level metrics and charts.

- `drone_mapping.py`:
  - Produces a mapped seagrass surface chart (summed or sampled per month depending on the code logic).
  - Produces a dugong feeding evidence chart grouped by year and month.
  - The cyanobacteria evidence chart has been removed from this file and moved to `Cyanobacteria_evidence.py`.

- `dugong_grazing.py`:
  - Computes and plots dugong grazing / feeding evidence across sites, months and years.
  - The per-chart data tables were removed to keep the UI focused on charts only.

- `Cyanobacteria_evidence.py`:
  - New dedicated page to visualize cyanobacteria evidence by month and year.
  - Provides year/month filters and a grouped Plotly bar chart per month with year as color.

## Dependencies

The app uses the packages listed in `requirements.txt`. Typical dependencies:

- streamlit
- pandas
- numpy
- plotly
- openpyxl (for reading .xlsx files with pandas)

Install them with:

```powershell
# Windows PowerShell
python -m pip install -r requirements.txt
```

If you prefer a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Excel compatibility

The app expects a single Excel workbook named `TRANSECT_DATA_SUMMARY.xlsx` in the project root. The primary sheet used in current modules is `TRANSECT DATA SUMMARY` (case-sensitive sheet name used when reading via pandas). Required columns (expected) include — but are not strictly limited to:

- `YEAR` — numeric year values (e.g., 2022). The code coerces to numeric and drops invalid rows.
- `MONTH` — month names (any capitalization). The code normalizes month names to UPPER case and sorts months using a fixed chronological order.
- `SEAGRASS_COVER` — numeric percent cover values or counts used to calculate averages.
- `SURFACE SEAGRASS MAPPING` — numeric mapped surface values used by `drone_mapping.py`.
- `DUGONG FEEDING EVIDENCE MAPPING` — numeric evidence counts used by `dugong_grazing.py` and/or `drone_mapping.py`.
- `CYANOBACTERIA EVIDENCE` — numeric evidence counts used by `Cyanobacteria_evidence.py`.

If any of these columns are missing, each module contains defensive checks and will show a Streamlit message. Ensure months are spelled in English (JANUARY, FEBRUARY, ... or normal mixed-case variants).

## Run the app

From the project root (Windows PowerShell):

```powershell
streamlit run app.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501`) in your browser.

## Navigation and usage

- Use the left sidebar to select a page:
  - `Seagrass Cover` — view average seagrass cover by year and a secondary chart by month. Select years at the top; the monthly chart will be filtered by the selected years.
  - `Drone Mapping` — mapped seagrass surface and dugong feeding evidence charts grouped by month and year.
  - `Dugong Grazing` — detailed dugong grazing/feeding visualizations.
  - `Cyanobacteria evidence` — view cyanobacteria evidence by month and year; filter years and months.

- Common UI tips:
  - Year filters are shown as multi-select boxes and are sorted numerically.
  - Month filters are shown in chronological order irrespective of the selection order.
  - Numeric values in charts and dataframes are formatted to 2 decimal places where appropriate; some tables hide empty values.

## Notes and troubleshooting

- If charts show commas in years (e.g., '2,022'), the code converts `YEAR` to integer then to string to prevent thousand separators in Plotly/Streamlit display.
- If a chart is empty, check the Excel file to ensure data exists for the selected years/months and that the column names match exactly.
- After modifying Python files, restart the Streamlit app to pick up code changes.

## Suggested next steps

- Add small unit tests for data-processing functions.
- Add documentation of expected Excel column types and a sample minimal CSV/Excel file for testing.

---

If you want, I can also commit this README into the repository and run a quick linter/format check. Let me know if you want the README in French instead or to include screenshots.