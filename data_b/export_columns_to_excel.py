import argparse
import os
import sys

import pandas as pd
import mysql.connector

import config.config_data_b as db_config


def fetch_columns(config):
    db_name = config.get('database')
    if not db_name:
        raise ValueError('`database` key missing from config')

    conn = mysql.connector.connect(**config)
    try:
        cursor = conn.cursor(dictionary=True)
        query = (
            "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT "
            "FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s "
            "ORDER BY TABLE_NAME, ORDINAL_POSITION"
        )
        cursor.execute(query, (db_name,))
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


def rows_to_excel(rows, out_path):
    if not rows:
        print('No columns found for the configured database.')
        return

    import re

    df = pd.DataFrame(rows)

    if 'TABLE_NAME' not in df.columns:
        print('Unexpected result: TABLE_NAME column missing')
        return

    out_dir = os.path.dirname(out_path) or '.'
    os.makedirs(out_dir, exist_ok=True)

    # Helper to create a valid Excel sheet name (max 31 chars, no []:*?/\\)
    def sanitize_sheet(name):
        if not isinstance(name, str):
            name = str(name)
        # Replace invalid characters
        name = re.sub(r'[\\/*?:\[\]]', '_', name)
        name = name.strip()
        if len(name) > 31:
            name = name[:31]
        return name or 'sheet'

    used = set()
    groups = df.groupby('TABLE_NAME')
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        for table_name, group in groups:
            sheet = sanitize_sheet(table_name)
            base = sheet
            suffix = 1
            # Ensure unique sheet names
            while sheet in used:
                # keep total length <=31
                extra = f"_{suffix}"
                sheet = (base[:31 - len(extra)] + extra) if len(base) + len(extra) > 31 else base + extra
                suffix += 1
            used.add(sheet)

            cols = ['COLUMN_NAME', 'DATA_TYPE', 'COLUMN_TYPE', 'IS_NULLABLE', 'COLUMN_DEFAULT']
            out_df = group[[c for c in cols if c in group.columns]]
            out_df = out_df.reset_index(drop=True)
            out_df.to_excel(writer, sheet_name=sheet, index=False)
    total_columns = len(df)
    total_sheets = len(groups)
    print(f'Exported {total_columns} columns into {total_sheets} sheets in {out_path}')


def main():
    parser = argparse.ArgumentParser(description='Export MySQL columns of all tables to an Excel file')
    parser.add_argument('--out', '-o', default='columns_by_table.xlsx', help='Output Excel file path')
    parser.add_argument('--database', '-d', help='MySQL database/schema name to inspect')
    args = parser.parse_args()

    config = dict(db_config.config)
    if args.database:
        config['database'] = args.database

    try:
        rows = fetch_columns(config)
        rows_to_excel(rows, args.out)
    except Exception as e:
        print('Error:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
