import pandas as pd
import os
from typing import Optional, List, Tuple, Dict, Union

# ---------- VALIDATION FUNCTION  ----------
def validate_dataframe(df: pd.DataFrame,
                       n_cols: Optional[int] = None,
                       n_rows: Optional[Tuple[int, int]] = None,
                       columns: Optional[List[str]] = None,
                       column_types: Optional[Dict[str, type]] = None,
                       check_duplicates: bool = False,
                       check_null_values: bool = False,
                       unique_columns: Optional[List[str]] = None,
                       column_ranges: Optional[Dict[str, Tuple[Union[int, float], Union[int, float]]]] = None,
                       date_columns: Optional[List[str]] = None,
                       categorical_columns: Optional[Dict[str, List[Union[str, int, float]]]] = None
                       ) -> Tuple[bool, str]:
    if n_cols is not None and len(df.columns) != n_cols:
        return False, f"Error: Expected {n_cols} columns, but found {len(df.columns)} columns."
    if n_rows is not None:
        min_rows, max_rows = n_rows
        if not (min_rows <= len(df) <= max_rows):
            return False, f"Error: Number of rows should be between {min_rows} and {max_rows}."
    if columns is not None and not set(columns).issubset(df.columns):
        missing_columns = set(columns) - set(df.columns)
        return False, f"Error: Missing columns: {missing_columns}."
    if column_types is not None:
        for col, expected_type in column_types.items():
            if col not in df.columns:
                return False, f"Error: Column '{col}' not found."
            if not df[col].dtype == expected_type:
                return False, f"Error: Column '{col}' should have type {expected_type}."
    if check_duplicates and df.duplicated().any():
        return False, "Duplicates found in the DataFrame."
    if check_null_values and df.isnull().any().any():
        return False, "DataFrame contains null values."
    if unique_columns is not None:
        for col in unique_columns:
            if col in df.columns and df[col].duplicated().any():
                return False, f"Column '{col}' should have only unique values."
    if column_ranges is not None:
        for col, value_range in column_ranges.items():
            if col in df.columns and not df[col].between(*value_range).all():
                return False, f"Values in '{col}' should be between {value_range[0]} and {value_range[1]}."
    if date_columns is not None:
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col], errors='raise')
                except ValueError:
                    return False, f"'{col}' should be in a valid date format."
    if categorical_columns is not None:
        for col, allowed_values in categorical_columns.items():
            if col in df.columns and not df[col].isin(allowed_values).all():
                return False, f"Values in '{col}' should be {allowed_values}."
    return True, "DataFrame has passed all validations."

# ---------- LOAD FIXED CSV FILES ----------
model_colleteral_raw = pd.read_csv(r"C:\Users\ANKUSH\OneDrive\Documents\Python\FRS data\data\model_collateral.csv")
model_config_raw = pd.read_csv(r"C:\Users\ANKUSH\OneDrive\Documents\Python\FRS data\data\model_config.csv")

# ---------- LOAD MULTIPLE FILES ----------
folder_path = r"C:\Users\ANKUSH\OneDrive\Documents\Python\FRS data\data\model_auth_Rep"
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

model_auth_Rep_raw = {}
for file in csv_files:
    df = pd.read_csv(os.path.join(folder_path, file))
    model_auth_Rep_raw[file] = df

# ---------- VALIDATE ----------
print("Validating model_auth_Rep files:")
for filename, df in model_auth_Rep_raw.items():
    is_valid, message = validate_dataframe(df, n_cols=14, check_duplicates=True)
    print(f"{filename}: {is_valid}, {message}")

print("\nValidating model_collateral:")
is_valid, message = validate_dataframe(model_colleteral_raw, n_cols=78, check_duplicates=True)
print(f"model_collateral.csv: {is_valid}, {message}")

print("\nValidating model_config:")
is_valid, message = validate_dataframe(model_config_raw, n_cols=4, check_duplicates=True)
print(f"model_config.csv: {is_valid}, {message}")

# ---------- COMBINE AND GENERATE REPORTS ----------
combined_ecl = []
combined_ead_var = []
combined_lgd_var = []

for filename, auth_df in model_auth_Rep_raw.items():
    # Extract date from filename, assuming format like "2007-06-01.csv"
    try:
        file_date = pd.to_datetime(filename.replace(".csv", ""), format="%Y-%m-%d")
    except ValueError:
        print(f"⚠️ Warning: Could not parse date from filename '{filename}'. Skipping file.")
        continue

    prev_ead_col = None
    prev_lgd_col = None

    if 'Previous_EAD' in auth_df.columns:
        prev_ead_col = 'Previous_EAD'
    elif 'Previous EAD' in auth_df.columns:
        prev_ead_col = 'Previous EAD'

    if 'Previous_LGD' in auth_df.columns:
        prev_lgd_col = 'Previous_LGD'
    elif 'Previous LGD' in auth_df.columns:
        prev_lgd_col = 'Previous LGD'

    # Construct ECL Data
    df = pd.DataFrame({
        'EAD': auth_df['EAD'],
        'PD12': auth_df['PD12'],
        'PDLT': auth_df['PDLT'],
        'LGD': auth_df['LGD'],
        'Previous EAD': auth_df[prev_ead_col] if prev_ead_col else pd.NA,
        'Previous LGD': auth_df[prev_lgd_col] if prev_lgd_col else pd.NA,
    })

    df['File'] = filename
    df['Date'] = file_date  # Add parsed date for Power BI use

    # ECL Calculations
    df['stage1ecl'] = df['EAD'] * df['PD12'] * df['LGD']
    df['stage2ecl'] = df['EAD'] * df['PDLT'] * df['LGD']
    df['stage3ecl'] = df['EAD'] * df['LGD']
    combined_ecl.append(df[['Date', 'File', 'EAD', 'PD12', 'LGD', 'PDLT', 'stage1ecl', 'stage2ecl', 'stage3ecl']])

    # EAD Variations
    df['change_EAD'] = df['EAD'] - df['Previous EAD']
    df['percentage_change_EAD'] = df['change_EAD'] / df['Previous EAD'] * 100
    df['percentage_change_EAD'] = df['percentage_change_EAD'].replace([float('inf'), -float('inf')], pd.NA)
    combined_ead_var.append(df[['Date', 'File', 'EAD', 'Previous EAD', 'change_EAD', 'percentage_change_EAD']])

    # LGD Variations
    df['change_LGD'] = df['LGD'] - df['Previous LGD']
    df['percentage_change_LGD'] = df['change_LGD'] / df['Previous LGD'] * 100
    df['percentage_change_LGD'] = df['percentage_change_LGD'].replace([float('inf'), -float('inf')], pd.NA)
    combined_lgd_var.append(df[['Date', 'File', 'LGD', 'Previous LGD', 'change_LGD', 'percentage_change_LGD']])

# ---------- COMBINE ALL FILES ----------
ecl_df = pd.concat(combined_ecl, ignore_index=True)
ead_variation_df = pd.concat(combined_ead_var, ignore_index=True)
lgd_variation_df = pd.concat(combined_lgd_var, ignore_index=True)

# ---------- EXPORT ----------
with pd.ExcelWriter("IFRS9_Reports_All_Files.xlsx") as writer:
    ecl_df.to_excel(writer, sheet_name='ECL_Report', index=False)
    ead_variation_df.to_excel(writer, sheet_name='EAD_Variation', index=False)
    lgd_variation_df.to_excel(writer, sheet_name='LGD_Variation', index=False)

# Optional CSVs
ecl_df.to_csv('ECL_Report_All.csv', index=False)
ead_variation_df.to_csv('EAD_Variation_All.csv', index=False)
lgd_variation_df.to_csv('LGD_Variation_All.csv', index=False)

print("✅ Combined Reports generated for all files.")
