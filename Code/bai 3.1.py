import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import os

def is_number(x):
    """Return True if x can be converted to float."""
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False

def load_data(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM player_stats', conn)
    conn.close()
    return df

def convert_numeric(df: pd.DataFrame) -> pd.DataFrame:
    # Identify columns that should be numeric (excluding id, player, nation, pos, squad, age, born, mp, starts)
    exclude = {'id', 'player', 'nation', 'pos', 'squad', 'age', 'born', 'mp', 'starts'}
    numeric_cols = [c for c in df.columns if c not in exclude]
    for col in numeric_cols:
        # Convert to numeric, coerce errors to NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def compute_team_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # Group by team (squad)
    metric_cols = [c for c in df.columns if c not in {'id', 'player', 'nation', 'pos', 'squad', 'age', 'born', 'mp', 'starts'}]
    results = []
    for squad, group in df.groupby('squad'):
        for col in metric_cols:
            series = group[col].dropna()
            if series.empty:
                continue
            mean = series.mean()
            median = series.median()
            std = series.std(ddof=0)  # population std
            results.append({
                'squad': squad,
                'metric': col,
                'mean': round(mean, 3),
                'median': round(median, 3),
                'std': round(std, 3)
            })
    return pd.DataFrame(results)

def compute_best_teams(team_metrics: pd.DataFrame) -> pd.DataFrame:
    # For each metric, find squad with highest mean
    best = []
    for metric, sub in team_metrics.groupby('metric'):
        idx = sub['mean'].idxmax()
        row = sub.loc[idx]
        best.append({
            'metric': metric,
            'best_squad': row['squad'],
            'mean': row['mean']
        })
    return pd.DataFrame(best)

def main():
    """Entry point.
    The script always writes (or overwrites) the CSV files in the ``output``
    directory.  If the directory or the files are missing – for example, you
    delete them after a previous run – executing the script again will recreate
    the full output automatically.  This makes the code portable: anyone who
    clones the repository can simply run the script and obtain the CSV files
    without any manual preparation.
    """
    # Path to the SQLite database (relative to this script)
    db_path = os.path.join(os.path.dirname(__file__), 'chi so cau thu da hon 90 phut.db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f'Database not found at {db_path}')
    df = load_data(db_path)
    df = convert_numeric(df)
    team_metrics = compute_team_metrics(df)
    # Ensure a clean output directory at the repository root
    import pathlib
    output_dir = pathlib.Path(__file__).resolve().parent.parent / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save per‑team metric statistics
    team_metrics_path = output_dir / 'team_stats.csv'
    team_metrics.to_csv(team_metrics_path, index=False)

    # Compute and save best squad per metric (based on mean)
    best_teams = compute_best_teams(team_metrics)
    best_teams_path = output_dir / 'best_teams_per_metric.csv'
    best_teams.to_csv(best_teams_path, index=False)

    print('Analysis complete. Files written:')
    print(f'  {team_metrics_path}')
    print(f'  {best_teams_path}')

if __name__ == '__main__':
    main()
