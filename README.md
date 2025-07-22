# IFRS9 Reporting Automation

## Project Overview
This project automates the **IFRS9 Expected Credit Loss (ECL)** reporting process by validating multiple input CSV files, performing data consistency checks, computing key risk metrics such as Stage 1, 2, and 3 ECL, and generating consolidated reports. The outputs are exported in Excel and CSV formats for downstream consumption, such as Power BI dashboards.

## Features
- Validates input data files for schema, duplicates, nulls, and value ranges
- Parses multiple CSV files representing monthly reports
- Calculates ECL values and changes in Exposure at Default (EAD) and Loss Given Default (LGD)
- Combines results to generate comprehensive reports across time periods
- Exports results as Excel files with multiple sheets and CSV for easy analysis

## Technologies
- Python 3
- Pandas for data manipulation
- Excel export using Pandas ExcelWriter

## Usage Instructions

1. Place the input CSV files in their respective folders:
    - `model_collateral.csv` and `model_config.csv` in the data folder
    - Multiple monthly report CSVs in the `model_auth_Rep` folder

2. Update the file paths in the script (currently absolute paths) if needed.

3. Run the script:
    ```
    python ifrs9_reporting.py
    ```

4. Output files will be generated in the current directory:
    - `IFRS9_Reports_All_Files.xlsx`
    - `ECL_Report_All.csv`
    - `EAD_Variation_All.csv`
    - `LGD_Variation_All.csv`

## Data Validation Checks
- Number of columns and rows
- Required columns present
- Data types validation
- Duplicate and null values detection
- Value ranges for numeric columns
- Correct date formatting
- Allowed categorical values where applicable

## Notes
- Filename dates should follow the format `YYYY-MM-DD.csv`.
- The script currently uses hardcoded file paths; it can be extended to accept dynamic input.

## Future Improvements
- Parameterize input paths for flexibility
- Add unit tests for validation functions
- Integrate logging for better traceability
- Package as a Python module or command-line tool

## Author
[Ankush Dhakare]


