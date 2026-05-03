# compute_stats.py
# ------------------------------------------------------------
# Purpose:  • Load the SQLite table `player_stats`
#           • For every team (column `squad`) calculate
#               – median
#               – mean
#               – population standard deviation (σ)
#           • Save the aggregates to `player_stats_summary.csv`
#           • Determine the team with the highest mean for each metric
# ------------------------------------------------------------

import json
import sqlite3
import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# Configuration – adjust only the two paths if you move the files
# ------------------------------------------------------------------
DB_PATH = r'C:\\Users\\Admin\\Desktop\\btl code\\player premier legaue.db'
OUTPUT_CSV = r'C:\\Users\\Admin\\Desktop\\btl code\\player_stats_summary.csv'

def load_table(db_path: str, table_name: str = "player_stats") -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def numeric_columns(df: pd.DataFrame) -> list:
    non_numeric = {"id", "player", "nation", "pos", "squad", "age", "born"}
    cols = [c for c in df.columns if c not in non_numeric]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return cols

def main():
    df = load_table(DB_PATH)
    num_cols = numeric_columns(df)
    rows = []
    for squad, group in df.groupby('squad'):
        for col in num_cols:
            series = group[col].dropna()
            if series.empty:
                continue
            mean = series.mean()
            median = series.median()
            std = series.std(ddof=0)  # population std
            rows.append({
                'squad': squad,
                'metric': col,
                'mean': round(mean, 3),
                'median': round(median, 3),
                'std': round(std, 3)
            })
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUT_CSV, index=False)
    print(f'Summary written to {OUTPUT_CSV}')
    # best team per metric
    best = []
    for metric, sub in summary.groupby('metric'):
        best_row = sub.loc[sub['mean'].idxmax()]
        best.append({
            'metric': metric,
            'top_squad': best_row['squad'],
            'mean': best_row['mean']
        })
    print('\nBest teams per metric:')
    print(json.dumps(best, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
