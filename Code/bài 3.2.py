import os
import pathlib
import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def load_data(db_path: str) -> pd.DataFrame:
    """Load the ``player_stats`` table from the SQLite database."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM player_stats', conn)
    conn.close()
    return df


def convert_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all columns except identifiers to numeric, coercing errors to NaN."""
    exclude = {'id', 'player', 'nation', 'pos', 'squad', 'age', 'born', 'mp', 'starts'}
    numeric_cols = [c for c in df.columns if c not in exclude]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def plot_elbow_and_silhouette(df_numeric: pd.DataFrame, output_dir: pathlib.Path, k_min=2, k_max=10):
    """Generate Elbow and Silhouette plots for a range of *k*.

    Returns the *k* with the highest silhouette score (ties broken by lower inertia).
    Plots are saved as ``elbow.png`` and ``silhouette.png`` inside ``output_dir``.
    """
    inertias = []
    silhouettes = []
    ks = list(range(k_min, k_max + 1))
    for k in ks:
        km = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = km.fit_predict(df_numeric)
        inertias.append(km.inertia_)
        if k > 1:
            sil = silhouette_score(df_numeric, labels)
        else:
            sil = 0
        silhouettes.append(sil)

    # Elbow plot
    plt.figure(figsize=(6, 4))
    plt.plot(ks, inertias, marker='o')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    elbow_path = output_dir / 'elbow.png'
    plt.tight_layout()
    plt.savefig(elbow_path)
    plt.close()

    # Silhouette plot
    plt.figure(figsize=(6, 4))
    plt.plot(ks, silhouettes, marker='o')
    plt.title('Silhouette Score vs. k')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Silhouette Score')
    sil_path = output_dir / 'silhouette.png'
    plt.tight_layout()
    plt.savefig(sil_path)
    plt.close()

    # Choose best k (max silhouette, then lower inertia)
    best_idx = max(range(len(silhouettes)), key=lambda i: (silhouettes[i], -inertias[i]))
    best_k = ks[best_idx]
    return best_k


def plot_pca_clusters(df_numeric: pd.DataFrame, labels: np.ndarray, output_dir: pathlib.Path, n_components: int = 2):
    """Run PCA to ``n_components`` (2 or 3) and scatter‑plot the K‑means clusters.
    The figure is saved as ``pca_2d.png`` or ``pca_3d.png``.
    """
    pca = PCA(n_components=n_components, random_state=42)
    reduced = pca.fit_transform(df_numeric)

    if n_components == 2:
        plt.figure(figsize=(6, 5))
        sc = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10', s=30)
        plt.title('K‑means clusters (PCA 2‑D)')
        plt.xlabel('PC1')
        plt.ylabel('PC2')
        plt.colorbar(sc, label='Cluster')
        path = output_dir / 'pca_2d.png'
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
    elif n_components == 3:
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(reduced[:, 0], reduced[:, 1], reduced[:, 2], c=labels, cmap='tab10', s=30)
        ax.set_title('K‑means clusters (PCA 3‑D)')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_zlabel('PC3')
        fig.colorbar(sc, ax=ax, label='Cluster')
        path = output_dir / 'pca_3d.png'
        plt.tight_layout()
        plt.savefig(path)
        plt.close()


def main():
    """Run the full workflow:
    1. Load data from the SQLite DB.
    2. Convert to numeric values.
    3. Determine the optimal number of clusters using Elbow & Silhouette plots.
    4. Fit K‑means with that *k*.
    5. Visualise the clusters with PCA (2‑D & 3‑D).
    All artefacts (plots) are written to an ``output`` directory at the repository root.
    """
    # ----- paths -----
    db_path = os.path.join(os.path.dirname(__file__), 'chi so cau thu da hon 90 phut.db')
    output_dir = pathlib.Path(__file__).resolve().parent.parent / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # ----- load & pre‑process -----
    df = load_data(db_path)
    df = convert_to_numeric(df)
    # Drop any rows that are completely NaN after conversion (unlikely but safe)
    df_clean = df.dropna(how='all')
    # Use only numeric columns for clustering
    numeric_cols = [c for c in df_clean.columns if c not in {'id', 'player', 'nation', 'pos', 'squad', 'age', 'born', 'mp', 'starts'}]
    df_numeric = df_clean[numeric_cols].fillna(0)  # fill missing with 0 for clustering

    # ----- choose k -----
    best_k = plot_elbow_and_silhouette(df_numeric, output_dir, k_min=2, k_max=10)
    print(f'Optimal number of clusters (based on silhouette): {best_k}')

    # ----- K‑means -----
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(df_numeric)

    # ----- visualise with PCA -----
    plot_pca_clusters(df_numeric, labels, output_dir, n_components=2)
    plot_pca_clusters(df_numeric, labels, output_dir, n_components=3)
    print('Plots saved in', output_dir)

if __name__ == '__main__':
    main()
