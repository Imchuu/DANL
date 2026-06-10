# Export MySQL columns to Excel

This script exports all column names (and basic metadata) for every table in the configured MySQL database into an Excel file.

Usage

1. Install dependencies:

```bash
pip install -r data_b/requirements.txt
```

2. Run the exporter (defaults to `columns_by_table.xlsx`):

```bash
python data_b/export_columns_to_excel.py --out output.xlsx
```

To export columns from a different database/schema such as `pvn`, pass the `--database` option:

```bash
python data_b/export_columns_to_excel.py --database pvn --out pvn_columns.xlsx
```

The script reads the DB connection from `data_b/config/config_data_b.py` and overrides only the `database` value when `--database` is provided.
